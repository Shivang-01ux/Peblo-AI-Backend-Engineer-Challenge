"""
Pydantic schemas for the content ingestion pipeline.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Request schemas ──────────────────────────────────────────────

class IngestRequest(BaseModel):
    """Metadata sent alongside a PDF upload."""
    title: str = Field(..., min_length=1, max_length=500, description="Document title")
    grade: Optional[int] = Field(None, ge=1, le=12, description="Grade level (1-12)")
    subject: Optional[str] = Field(None, max_length=200, description="Subject area")


# ── Response schemas ─────────────────────────────────────────────

class ChunkResponse(BaseModel):
    """A single content chunk returned after ingestion."""
    id: int
    source_id: int
    chunk_id: str
    topic: Optional[str]
    text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class IngestResponse(BaseModel):
    """Response returned after successful PDF ingestion."""
    document_id: int
    title: str
    total_chunks: int
    chunks: list[ChunkResponse]
    message: str = "Document ingested successfully"


class DocumentResponse(BaseModel):
    """Summary view of a source document."""
    id: int
    title: str
    grade: Optional[int]
    subject: Optional[str]
    file_path: str
    total_chunks: int
    created_at: datetime

    model_config = {"from_attributes": True}
