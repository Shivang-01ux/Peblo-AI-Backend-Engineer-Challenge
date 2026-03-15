"""
Content repository — data access layer for documents and chunks.
"""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.source_document import SourceDocument
from app.models.content_chunk import ContentChunk
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ContentRepository:
    """CRUD operations for SourceDocument and ContentChunk."""

    def __init__(self, db: Session):
        self.db = db

    # ── SourceDocument ───────────────────────────────────────────

    def create_document(
        self, title: str, file_path: str, grade: Optional[int] = None, subject: Optional[str] = None
    ) -> SourceDocument:
        """Persist a new source document record."""
        doc = SourceDocument(title=title, file_path=file_path, grade=grade, subject=subject)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        logger.info("Created document id=%d title='%s'", doc.id, doc.title)
        return doc

    def get_document_by_id(self, doc_id: int) -> Optional[SourceDocument]:
        return self.db.query(SourceDocument).filter(SourceDocument.id == doc_id).first()

    def list_documents(self, skip: int = 0, limit: int = 50) -> list[SourceDocument]:
        return self.db.query(SourceDocument).offset(skip).limit(limit).all()

    def update_chunk_count(self, doc_id: int, count: int) -> None:
        self.db.query(SourceDocument).filter(SourceDocument.id == doc_id).update(
            {"total_chunks": count}
        )
        self.db.commit()

    # ── ContentChunk ─────────────────────────────────────────────

    def create_chunks(self, chunks: list[ContentChunk]) -> list[ContentChunk]:
        """Bulk-insert content chunks."""
        self.db.add_all(chunks)
        self.db.commit()
        for c in chunks:
            self.db.refresh(c)
        logger.info("Inserted %d chunks", len(chunks))
        return chunks

    def get_chunk_by_id(self, chunk_id: int) -> Optional[ContentChunk]:
        return self.db.query(ContentChunk).filter(ContentChunk.id == chunk_id).first()

    def get_chunks_by_source(self, source_id: int) -> list[ContentChunk]:
        return (
            self.db.query(ContentChunk)
            .filter(ContentChunk.source_id == source_id)
            .all()
        )

    def get_chunks_by_topic(self, topic: str, limit: int = 10) -> list[ContentChunk]:
        """Case-insensitive topic search."""
        return (
            self.db.query(ContentChunk)
            .filter(func.lower(ContentChunk.topic).contains(topic.lower()))
            .limit(limit)
            .all()
        )

    def get_random_chunks(self, limit: int = 5) -> list[ContentChunk]:
        """Return random chunks for quiz generation."""
        return (
            self.db.query(ContentChunk)
            .order_by(func.random())
            .limit(limit)
            .all()
        )

    def update_embedding(self, chunk_id: int, embedding: list[float]) -> None:
        self.db.query(ContentChunk).filter(ContentChunk.id == chunk_id).update(
            {"embedding": embedding}
        )
        self.db.commit()

    def get_all_embeddings(self) -> list[ContentChunk]:
        """Return all chunks that have embeddings (for similarity search)."""
        return (
            self.db.query(ContentChunk)
            .filter(ContentChunk.embedding.isnot(None))
            .all()
        )
