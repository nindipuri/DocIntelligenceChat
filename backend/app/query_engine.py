"""
Question-answering over a document using retrieved pages and an LLM.
"""

import logging
from typing import Any

from openai import OpenAI

from app.config import get_settings
from app.rag_engine import search

logger = logging.getLogger(__name__)


def _build_context(pages: list[dict[str, Any]]) -> str:
    """Format retrieved pages as context block for the prompt."""
    parts = []
    for p in pages:
        page_num = p.get("page", "?")
        text = (p.get("text") or "").strip()
        parts.append(f"[Page {page_num}]\n{text}")
    return "\n\n---\n\n".join(parts)


def answer(
    document_id: str,
    question: str,
    *,
    openai_client: OpenAI | None = None,
) -> tuple[str, list[int]]:
    """
    Answer a question about a document using PageIndex retrieval and the LLM.

    Returns (answer_text, list of cited page numbers).
    """
    settings = get_settings()
    client = openai_client or OpenAI(api_key=settings.openai_api_key)

    # 1. Retrieve relevant pages
    retrieved = search(document_id, question, openai_client=client)
    if not retrieved:
        return (
            "I could not find any content for this document. Please check that the document was uploaded and indexed.",
            [],
        )

    context = _build_context(retrieved)
    cited_pages = sorted({p.get("page") for p in retrieved if p.get("page") is not None})

    prompt = f"""You are an assistant answering questions about a document.

Use only the context below to answer. Extract and synthesize information from the provided pages.
- If the answer is in the context (even if phrased differently), provide it clearly and cite the relevant page(s).
- If the context has partial or related information, provide what you can find.
- Only say "I cannot find the answer in the document" if the context clearly does not contain any relevant information.

Context:
{context}

Question:
{question}"""

    try:
        response = client.chat.completions.create(
            model=settings.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        answer_text = (response.choices[0].message.content or "").strip()
        logger.info("Query answered for document %s, cited pages: %s", document_id, cited_pages)
        return answer_text, cited_pages
    except Exception as e:
        logger.exception("LLM request failed: %s", e)
        raise
