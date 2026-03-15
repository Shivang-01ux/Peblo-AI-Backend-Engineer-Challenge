"""
SourceDocument ORM model.

Represents an uploaded educational PDF document.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class SourceDocument(Base):
    """An ingested educational document (PDF)."""

    __tablename__ = "source_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    grade = Column(Integer, nullable=True)
    subject = Column(String(200), nullable=True)
    file_path = Column(String(1000), nullable=False)
    total_chunks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chunks = relationship(
        "ContentChunk", back_populates="source", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SourceDocument id={self.id} title='{self.title}'>"
