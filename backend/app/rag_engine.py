"""
PageIndex-style storage and retrieval.

Stores document pages on disk. Search uses reasoning-based selection
(LLM picks relevant pages) — no vectors or embeddings.
"""

import json
import logging
from pathlib import Path
from typing import Any

from openai import OpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)


def _index_path(document_id: str) -> Path:
    """Path to the JSON file storing the page index for a document."""
    settings = get_settings()
    settings.storage_indexes.mkdir(parents=True, exist_ok=True)
    return settings.storage_indexes / f"{document_id}.json"


def add_pages(document_id: str, pages: list[dict[str, Any]], *, filename: str = "") -> None:
    """
    Store document pages for a given document_id.
    Persists to storage/indexes/{document_id}.json.
    """
    path = _index_path(document_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"filename": filename, "pages": pages}, f, ensure_ascii=False, indent=0)
    logger.info("Indexed document %s: %d pages", document_id, len(pages))


def get_pages(document_id: str) -> list[dict[str, Any]]:
    """
    Load stored pages for a document.
    Returns list of {"page": int, "text": str}.
    """
    path = _index_path(document_id)
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("pages", [])


def list_documents() -> list[dict[str, Any]]:
    """
    List all indexed documents: document_id, filename, page count.
    """
    settings = get_settings()
    settings.storage_indexes.mkdir(parents=True, exist_ok=True)
    result = []
    for path in settings.storage_indexes.glob("*.json"):
        doc_id = path.stem
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            pages = data.get("pages", [])
            result.append({
                "document_id": doc_id,
                "filename": data.get("filename", path.name),
                "pages": len(pages),
            })
        except Exception as e:
            logger.warning("Skip index %s: %s", path, e)
    return result


# For large docs: pre-filter to this many candidates before LLM selection
_PREFILTER_CANDIDATES = 50
# Min pages to trigger two-stage retrieval (keyword pre-filter + LLM)
_LARGE_DOC_THRESHOLD = 25
# For summary/conclusion questions, always include last N pages (conclusions often at end)
_TAIL_PAGES_FOR_SUMMARY = 8
_SUMMARY_KEYWORDS = ("summary", "conclusion", "conclude", "overview", "main", "key finding", "overall", "in summary")


def _normalize_for_match(text: str) -> str:
    """Normalize text for keyword matching (handles unicode spaces, etc.)."""
    import re
    import unicodedata
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text.lower())
    text = re.sub(r"[\xa0\u200b\u200c\u200d\ufeff]+", " ", text)
    return " ".join(text.split())


def _keyword_prefilter(pages: list[dict[str, Any]], query: str, top_n: int) -> list[dict[str, Any]]:
    """
    Pre-filter pages by keyword overlap so the LLM sees a manageable set.
    Helps with large documents (100+ pages) where sending all summaries overwhelms the model.
    """
    import re
    query_terms = set(re.findall(r"\b\w{2,}\b", _normalize_for_match(query)))
    if not query_terms:
        return pages[:top_n]

    scored: list[tuple[float, dict[str, Any]]] = []
    for p in pages:
        text = _normalize_for_match(p.get("text") or "")
        hits = sum(1 for t in query_terms if t in text)
        scored.append((hits, p))
    scored.sort(key=lambda x: (-x[0], x[1].get("page", 0)))
    return [p for _, p in scored[:top_n]]


def search(
    document_id: str,
    query: str,
    *,
    top_k: int | None = None,
    openai_client: OpenAI | None = None,
) -> list[dict[str, Any]]:
    """
    Reasoning-based retrieval: use LLM to select which pages are relevant to the query.
    For large documents, pre-filters by keyword overlap before LLM selection.
    Returns list of {"page": int, "text": str} for the top-k relevant pages.
    """
    pages = get_pages(document_id)
    if not pages:
        return []

    settings = get_settings()
    k = top_k or settings.max_context_pages
    k = min(k, len(pages))

    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY not set; returning first %d pages", k)
        return pages[:k]

    # For large docs: keyword pre-filter to reduce prompt size so LLM can pick from the right pages
    if len(pages) > _LARGE_DOC_THRESHOLD:
        candidates = _keyword_prefilter(pages, query, _PREFILTER_CANDIDATES)
        if not candidates:
            candidates = pages[:_PREFILTER_CANDIDATES]
        # For summary/conclusion questions, add last pages (conclusions often at end of reports)
        q_lower = query.lower()
        if any(kw in q_lower for kw in _SUMMARY_KEYWORDS) and len(pages) > _TAIL_PAGES_FOR_SUMMARY:
            tail = pages[-_TAIL_PAGES_FOR_SUMMARY:]
            for p in tail:
                if p not in candidates:
                    candidates.append(p)
        logger.info("Pre-filtered %d pages to %d candidates for query", len(pages), len(candidates))
    else:
        candidates = pages

    client = openai_client or OpenAI(api_key=settings.openai_api_key)

    page_summaries = []
    for p in candidates:
        text = (p.get("text") or "")[:400]
        page_summaries.append(f"Page {p.get('page', '?')}: {text}...")

    prompt = f"""You are a retrieval assistant. Given the following document page summaries and a user question, choose the page numbers that are most relevant to answering the question. Reply with ONLY a comma-separated list of page numbers (e.g. 1, 3, 5). Choose at most {k} pages.

Document page summaries:
---
{"---".join(page_summaries)}
---

User question: {query}

Relevant page numbers (comma-separated, at most {k}):"""

    try:
        response = client.chat.completions.create(
            model=settings.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=100,
        )
        content = (response.choices[0].message.content or "").strip()
        chosen = set()
        for part in content.replace(" ", "").split(","):
            part = part.strip()
            if part.isdigit():
                chosen.add(int(part))
        result = []
        for p in candidates:
            if p.get("page") in chosen:
                result.append(p)
        for p in candidates:
            if len(result) >= k:
                break
            if p not in result:
                result.append(p)
        return result[:k]
    except Exception as e:
        logger.exception("PageIndex search failed: %s", e)
        return pages[:k]
