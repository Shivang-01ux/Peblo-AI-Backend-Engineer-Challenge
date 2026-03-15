"""
Adaptive difficulty engine.

Adjusts quiz difficulty dynamically based on student performance streaks.
"""

from app.models.student_progress import StudentProgress
from app.utils.difficulty_classifier import (
    next_difficulty,
    previous_difficulty,
    DIFFICULTY_LEVELS,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── Configuration ────────────────────────────────────────────────
CORRECT_STREAK_THRESHOLD = 2   # Consecutive correct answers to level-up
WRONG_STREAK_THRESHOLD = 2     # Consecutive wrong answers to level-down


class AdaptiveEngine:
    """
    Manages difficulty progression for each student.

    Rules:
        - If correct_streak >= threshold  →  difficulty++  (reset streaks)
        - If wrong_streak   >= threshold  →  difficulty--  (reset streaks)
        - On correct answer: correct_streak++, wrong_streak = 0
        - On wrong answer:   wrong_streak++, correct_streak = 0
    """

    def update_progress(self, progress: StudentProgress, is_correct: bool) -> StudentProgress:
        """
        Update student progress after an answer is submitted.

        Args:
            progress: Current StudentProgress record.
            is_correct: Whether the latest answer was correct.

        Returns:
            Updated StudentProgress (not yet committed — caller commits).
        """
        progress.total_answered += 1

        if is_correct:
            progress.total_correct += 1
            progress.correct_streak += 1
            progress.wrong_streak = 0

            if progress.correct_streak >= CORRECT_STREAK_THRESHOLD:
                old = progress.current_difficulty
                progress.current_difficulty = next_difficulty(old)
                if progress.current_difficulty != old:
                    logger.info(
                        "Student %s leveled UP: %s → %s",
                        progress.student_id,
                        old,
                        progress.current_difficulty,
                    )
                progress.correct_streak = 0  # Reset after promotion
        else:
            progress.wrong_streak += 1
            progress.correct_streak = 0

            if progress.wrong_streak >= WRONG_STREAK_THRESHOLD:
                old = progress.current_difficulty
                progress.current_difficulty = previous_difficulty(old)
                if progress.current_difficulty != old:
                    logger.info(
                        "Student %s leveled DOWN: %s → %s",
                        progress.student_id,
                        old,
                        progress.current_difficulty,
                    )
                progress.wrong_streak = 0  # Reset after demotion

        return progress

    @staticmethod
    def get_recommended_difficulty(progress: StudentProgress) -> str:
        """Return the difficulty that should be served next."""
        return progress.current_difficulty

    @staticmethod
    def get_accuracy(progress: StudentProgress) -> float | None:
        """Calculate the student's overall accuracy."""
        if progress.total_answered == 0:
            return None
        return round(progress.total_correct / progress.total_answered * 100, 2)
