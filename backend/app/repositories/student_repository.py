"""
Student repository — data access for answers and progress tracking.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.student_answer import StudentAnswer
from app.models.student_progress import StudentProgress
from app.utils.logger import get_logger

logger = get_logger(__name__)


class StudentRepository:
    """CRUD operations for StudentAnswer and StudentProgress."""

    def __init__(self, db: Session):
        self.db = db

    # ── StudentAnswer ────────────────────────────────────────────

    def create_answer(
        self,
        student_id: str,
        question_id: int,
        selected_answer: str,
        is_correct: bool,
    ) -> StudentAnswer:
        answer = StudentAnswer(
            student_id=student_id,
            question_id=question_id,
            selected_answer=selected_answer,
            is_correct=is_correct,
        )
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        logger.info(
            "Recorded answer student=%s question=%d correct=%s",
            student_id,
            question_id,
            is_correct,
        )
        return answer

    def get_student_answers(
        self, student_id: str, limit: int = 50
    ) -> list[StudentAnswer]:
        return (
            self.db.query(StudentAnswer)
            .filter(StudentAnswer.student_id == student_id)
            .order_by(StudentAnswer.timestamp.desc())
            .limit(limit)
            .all()
        )

    # ── StudentProgress ──────────────────────────────────────────

    def get_or_create_progress(self, student_id: str) -> StudentProgress:
        """Get existing progress or create a fresh one."""
        progress = (
            self.db.query(StudentProgress)
            .filter(StudentProgress.student_id == student_id)
            .first()
        )
        if not progress:
            progress = StudentProgress(student_id=student_id)
            self.db.add(progress)
            self.db.commit()
            self.db.refresh(progress)
            logger.info("Created progress record for student=%s", student_id)
        return progress

    def update_progress(self, progress: StudentProgress) -> StudentProgress:
        """Persist updated progress state."""
        self.db.commit()
        self.db.refresh(progress)
        return progress
