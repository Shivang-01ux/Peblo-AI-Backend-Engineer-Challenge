"""
ContentChunk ORM model.

Represents a semantically meaningful chunk of extracted text.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class ContentChunk(Base):
    """A semantic chunk extracted from a source document."""

    __tablename__ = "content_chunks"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("source_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(String(100), unique=True, nullable=False, index=True)
    topic = Column(String(300), nullable=True)
    text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # stored as JSON list for SQLite compat
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    source = relationship("SourceDocument", back_populates="chunks")
    questions = relationship(
        "QuizQuestion", back_populates="source_chunk", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ContentChunk id={self.id} chunk_id='{self.chunk_id}'>"
