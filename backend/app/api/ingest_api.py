"""
Ingestion API router.

Endpoints for uploading and processing educational PDF documents.
"""

import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.content_chunk import ContentChunk
from app.repositories.content_repository import ContentRepository
from app.schemas.ingest_schema import ChunkResponse, DocumentResponse, IngestResponse
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.pdf_ingestion_service import PDFIngestionService
from app.services.text_cleaning_service import TextCleaningService
from app.utils.logger import get_logger

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)


@router.post("/ingest", response_model=IngestResponse, status_code=201)
def ingest_pdf(
    file: UploadFile = File(...),
    title: str = Form(...),
    grade: int | None = Form(None),
    subject: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """
    Upload a PDF document and run the full ingestion pipeline.

    Pipeline: Upload → Extract → Clean → Chunk → Embed → Store
    """
    # ── 1. Validate upload ───────────────────────────────────────
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # ── 2. Save file to disk ─────────────────────────────────────
    unique_name = f"{uuid4().hex}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        logger.info("Saved upload to %s", file_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"File save failed: {exc}")

    # ── 3. Extract text ──────────────────────────────────────────
    pdf_service = PDFIngestionService()
    try:
        raw_text = pdf_service.extract_text(file_path)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # ── 4. Clean text ────────────────────────────────────────────
    cleaner = TextCleaningService()
    cleaned_text = cleaner.clean(raw_text)

    # ── 5. Create document record ────────────────────────────────
    repo = ContentRepository(db)
    document = repo.create_document(
        title=title, file_path=file_path, grade=grade, subject=subject
    )

    # ── 6. Chunk text ────────────────────────────────────────────
    chunker = ChunkingService()
    raw_chunks = chunker.chunk_text(cleaned_text, source_id=str(document.id))

    if not raw_chunks:
        raise HTTPException(status_code=422, detail="No chunks could be created from this document.")

    # ── 7. Generate embeddings ───────────────────────────────────
    embedding_service = EmbeddingService()
    texts = [c["text"] for c in raw_chunks]
    try:
        embeddings = embedding_service.generate_embeddings_batch(texts)
    except RuntimeError:
        logger.warning("Embedding generation failed — storing chunks without embeddings")
        embeddings = [None] * len(raw_chunks)

    # ── 8. Store chunks ──────────────────────────────────────────
    chunk_models = []
    for i, raw_chunk in enumerate(raw_chunks):
        chunk_model = ContentChunk(
            source_id=document.id,
            chunk_id=raw_chunk["chunk_id"],
            topic=subject or "General",
            text=raw_chunk["text"],
            embedding=embeddings[i] if embeddings[i] else None,
        )
        chunk_models.append(chunk_model)

    stored_chunks = repo.create_chunks(chunk_models)
    repo.update_chunk_count(document.id, len(stored_chunks))

    logger.info(
        "Ingestion complete: document=%d chunks=%d", document.id, len(stored_chunks)
    )

    return IngestResponse(
        document_id=document.id,
        title=document.title,
        total_chunks=len(stored_chunks),
        chunks=[ChunkResponse.model_validate(c) for c in stored_chunks],
    )


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    """List all ingested documents."""
    repo = ContentRepository(db)
    return repo.list_documents(skip=skip, limit=limit)
