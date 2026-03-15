"""
QuizQuestion ORM model.

Represents a generated quiz question linked to a content chunk.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class QuizQuestion(Base):
    """An LLM-generated quiz question traceable to its source chunk."""

    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # MCQ | true_false | fill_in_the_blank
    options = Column(JSON, nullable=True)  # list of option strings (null for fill-in)
    answer = Column(String(500), nullable=False)
    difficulty = Column(String(20), nullable=False, default="easy")  # easy | medium | hard
    source_chunk_id = Column(
        Integer,
        ForeignKey("content_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quality_score = Column(Integer, nullable=True)  # 1-10, set by LLM quality check
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    source_chunk = relationship("ContentChunk", back_populates="questions")
    answers = relationship(
        "StudentAnswer", back_populates="question", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<QuizQuestion id={self.id} type='{self.type}' difficulty='{self.difficulty}'>"
