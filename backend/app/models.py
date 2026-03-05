"""Pydantic request/response models for the API."""

from pydantic import BaseModel, Field


# --- Upload ---


class UploadResponse(BaseModel):
    """Response after uploading a document."""

    document_id: str = Field(..., description="Unique document identifier (UUID)")
    pages: int = Field(..., description="Number of pages/sections in the document")


# --- Chat ---


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    document_id: str = Field(..., description="UUID of the document to query")
    question: str = Field(..., min_length=1, description="User question")


class SourceRef(BaseModel):
    """Reference to a source page."""

    page: int = Field(..., description="Page number (1-based)")


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    answer: str = Field(..., description="Generated answer")
    sources: list[SourceRef] = Field(default_factory=list, description="Cited page numbers")


# --- Documents list ---


class DocumentListItem(BaseModel):
    """Single document in the list."""

    document_id: str = Field(..., description="Document UUID")
    filename: str = Field(..., description="Original filename")
    pages: int = Field(..., description="Number of pages")


# GET /documents returns a JSON array; use list[DocumentListItem] as response_model
