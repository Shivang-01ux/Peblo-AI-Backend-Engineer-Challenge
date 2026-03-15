"""
StudentProgress ORM model.

Tracks per-student adaptive difficulty state.
"""

from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime

from app.database import Base


class StudentProgress(Base):
    """Tracks adaptive difficulty progression for each student."""

    __tablename__ = "student_progress"

    student_id = Column(String(100), primary_key=True, index=True)
    current_difficulty = Column(String(20), default="easy")  # easy | medium | hard
    correct_streak = Column(Integer, default=0)
    wrong_streak = Column(Integer, default=0)
    total_answered = Column(Integer, default=0)
    total_correct = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"<StudentProgress student='{self.student_id}' "
            f"difficulty='{self.current_difficulty}'>"
        )
