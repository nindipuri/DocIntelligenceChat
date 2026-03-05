"""
FastAPI application: document upload, chat, and document list.
"""

import logging
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.document_loader import load_document, SUPPORTED_EXTENSIONS
from app.models import (
    ChatRequest,
    ChatResponse,
    DocumentListItem,
    SourceRef,
    UploadResponse,
)
from app.query_engine import answer
from app.rag_engine import add_pages, get_pages, list_documents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DocIntelligenceChat API",
    description="Vectorless RAG chatbot: upload documents, ask questions, get answers with citations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _doc_path(document_id: str, suffix: str) -> Path:
    """Path under storage/documents for an uploaded file."""
    settings = get_settings()
    settings.storage_documents.mkdir(parents=True, exist_ok=True)
    return settings.storage_documents / f"{document_id}{suffix}"


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload a document (PDF, DOCX, or TXT). File is stored and parsed into pages;
    a PageIndex-style index is created for retrieval.
    """
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    document_id = str(uuid.uuid4())
    path = _doc_path(document_id, suffix)

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        path.write_bytes(contents)
    except Exception as e:
        logger.exception("Failed to save upload: %s", e)
        raise HTTPException(status_code=500, detail="Failed to save file")

    try:
        pages = load_document(path)
    except Exception as e:
        logger.exception("Failed to parse document: %s", e)
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Document parsing failed: {e!s}")

    if not pages:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Document produced no pages")

    add_pages(document_id, pages, filename=file.filename or path.name)
    logger.info("Uploaded document_id=%s filename=%s pages=%d", document_id, file.filename, len(pages))

    return UploadResponse(document_id=document_id, pages=len(pages))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Ask a question about an uploaded document. Returns an answer and source page numbers.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if not get_pages(request.document_id):
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        answer_text, cited_pages = answer(request.document_id, request.question.strip())
    except Exception as e:
        logger.exception("Chat failed: %s", e)
        raise HTTPException(status_code=500, detail="Query failed")

    return ChatResponse(
        answer=answer_text,
        sources=[SourceRef(page=p) for p in cited_pages],
    )


@app.get("/documents", response_model=list[DocumentListItem])
async def get_documents() -> list[DocumentListItem]:
    """List all uploaded documents with id, filename, and page count."""
    docs = list_documents()
    return [DocumentListItem(document_id=d["document_id"], filename=d["filename"], pages=d["pages"]) for d in docs]


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check."""
    return {"status": "ok"}
