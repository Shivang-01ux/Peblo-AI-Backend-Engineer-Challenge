"""
StudentAnswer ORM model.

Records each answer submitted by a student for a quiz question.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class StudentAnswer(Base):
    """A single answer submission from a student."""

    __tablename__ = "student_answers"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    question_id = Column(
        Integer,
        ForeignKey("quiz_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    selected_answer = Column(String(500), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    question = relationship("QuizQuestion", back_populates="answers")

    def __repr__(self) -> str:
        return (
            f"<StudentAnswer id={self.id} student='{self.student_id}' "
            f"correct={self.is_correct}>"
        )
