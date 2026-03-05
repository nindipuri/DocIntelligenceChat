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


def search(
    document_id: str,
    query: str,
    *,
    top_k: int | None = None,
    openai_client: OpenAI | None = None,
) -> list[dict[str, Any]]:
    """
    Reasoning-based retrieval: use LLM to select which pages are relevant to the query.
    Returns list of {"page": int, "text": str} for the top-k relevant pages.
    """
    pages = get_pages(document_id)
    if not pages:
        return []

    settings = get_settings()
    k = top_k or settings.max_context_pages
    k = min(k, len(pages))

    if not settings.openai_api_key:
        # No API key: return first k pages as fallback
        logger.warning("OPENAI_API_KEY not set; returning first %d pages", k)
        return pages[:k]

    client = openai_client or OpenAI(api_key=settings.openai_api_key)

    # Build a short summary per page for the LLM (first ~200 chars)
    page_summaries = []
    for p in pages:
        text = (p.get("text") or "")[:300]
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
        # Parse "1, 3, 5" or "1,3,5"
        chosen = set()
        for part in content.replace(" ", "").split(","):
            part = part.strip()
            if part.isdigit():
                chosen.add(int(part))
        # Build result in order of appearance, then fill with remaining pages if needed
        result = []
        for p in pages:
            if p.get("page") in chosen:
                result.append(p)
        # If LLM returned few, add by order until we have k
        for p in pages:
            if len(result) >= k:
                break
            if p not in result:
                result.append(p)
        return result[:k]
    except Exception as e:
        logger.exception("PageIndex search failed: %s", e)
        return pages[:k]
