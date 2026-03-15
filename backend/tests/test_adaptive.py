"""
Tests for the adaptive difficulty engine.

Covers difficulty progression, streak resets, and boundary conditions.
"""

import pytest

from app.models.student_progress import StudentProgress
from app.services.adaptive_engine import AdaptiveEngine


def _make_progress(
    difficulty: str = "easy",
    correct_streak: int = 0,
    wrong_streak: int = 0,
) -> StudentProgress:
    """Create a StudentProgress instance (detached from DB session)."""
    p = StudentProgress.__new__(StudentProgress)
    p.student_id = "test_student"
    p.current_difficulty = difficulty
    p.correct_streak = correct_streak
    p.wrong_streak = wrong_streak
    p.total_answered = 0
    p.total_correct = 0
    return p


class TestAdaptiveEngine:
    """Unit tests for adaptive difficulty engine."""

    def setup_method(self):
        self.engine = AdaptiveEngine()

    # ── Correct streaks ──────────────────────────────────────────

    def test_single_correct_no_level_change(self):
        progress = _make_progress(difficulty="easy")
        self.engine.update_progress(progress, is_correct=True)
        assert progress.current_difficulty == "easy"
        assert progress.correct_streak == 1
        assert progress.wrong_streak == 0

    def test_two_correct_levels_up(self):
        progress = _make_progress(difficulty="easy", correct_streak=1)
        self.engine.update_progress(progress, is_correct=True)
        assert progress.current_difficulty == "medium"
        assert progress.correct_streak == 0  # Reset after promotion

    def test_level_up_medium_to_hard(self):
        progress = _make_progress(difficulty="medium", correct_streak=1)
        self.engine.update_progress(progress, is_correct=True)
        assert progress.current_difficulty == "hard"

    def test_level_up_capped_at_hard(self):
        progress = _make_progress(difficulty="hard", correct_streak=1)
        self.engine.update_progress(progress, is_correct=True)
        assert progress.current_difficulty == "hard"

    # ── Wrong streaks ────────────────────────────────────────────

    def test_single_wrong_no_level_change(self):
        progress = _make_progress(difficulty="medium")
        self.engine.update_progress(progress, is_correct=False)
        assert progress.current_difficulty == "medium"
        assert progress.wrong_streak == 1
        assert progress.correct_streak == 0

    def test_two_wrong_levels_down(self):
        progress = _make_progress(difficulty="medium", wrong_streak=1)
        self.engine.update_progress(progress, is_correct=False)
        assert progress.current_difficulty == "easy"
        assert progress.wrong_streak == 0  # Reset after demotion

    def test_level_down_hard_to_medium(self):
        progress = _make_progress(difficulty="hard", wrong_streak=1)
        self.engine.update_progress(progress, is_correct=False)
        assert progress.current_difficulty == "medium"

    def test_level_down_capped_at_easy(self):
        progress = _make_progress(difficulty="easy", wrong_streak=1)
        self.engine.update_progress(progress, is_correct=False)
        assert progress.current_difficulty == "easy"

    # ── Streak resets ────────────────────────────────────────────

    def test_correct_resets_wrong_streak(self):
        progress = _make_progress(difficulty="medium", wrong_streak=1)
        self.engine.update_progress(progress, is_correct=True)
        assert progress.wrong_streak == 0
        assert progress.correct_streak == 1

    def test_wrong_resets_correct_streak(self):
        progress = _make_progress(difficulty="medium", correct_streak=1)
        self.engine.update_progress(progress, is_correct=False)
        assert progress.correct_streak == 0
        assert progress.wrong_streak == 1

    # ── Counters ─────────────────────────────────────────────────

    def test_total_answered_increments(self):
        progress = _make_progress()
        self.engine.update_progress(progress, is_correct=True)
        self.engine.update_progress(progress, is_correct=False)
        assert progress.total_answered == 2

    def test_total_correct_increments_only_on_correct(self):
        progress = _make_progress()
        self.engine.update_progress(progress, is_correct=True)
        self.engine.update_progress(progress, is_correct=False)
        self.engine.update_progress(progress, is_correct=True)
        assert progress.total_correct == 2

    # ── Accuracy ─────────────────────────────────────────────────

    def test_accuracy_none_when_no_answers(self):
        progress = _make_progress()
        assert self.engine.get_accuracy(progress) is None

    def test_accuracy_calculation(self):
        progress = _make_progress()
        progress.total_answered = 10
        progress.total_correct = 7
        assert self.engine.get_accuracy(progress) == 70.0

    def test_accuracy_100_percent(self):
        progress = _make_progress()
        progress.total_answered = 5
        progress.total_correct = 5
        assert self.engine.get_accuracy(progress) == 100.0

    # ── Full progression scenario ────────────────────────────────

    def test_full_progression_easy_to_hard_and_back(self):
        """Simulate a student going easy → medium → hard → medium → easy."""
        progress = _make_progress(difficulty="easy")

        # 2 correct → level up to medium
        self.engine.update_progress(progress, is_correct=True)
        self.engine.update_progress(progress, is_correct=True)
        assert progress.current_difficulty == "medium"

        # 2 correct → level up to hard
        self.engine.update_progress(progress, is_correct=True)
        self.engine.update_progress(progress, is_correct=True)
        assert progress.current_difficulty == "hard"

        # 2 wrong → level down to medium
        self.engine.update_progress(progress, is_correct=False)
        self.engine.update_progress(progress, is_correct=False)
        assert progress.current_difficulty == "medium"

        # 2 wrong → level down to easy
        self.engine.update_progress(progress, is_correct=False)
        self.engine.update_progress(progress, is_correct=False)
        assert progress.current_difficulty == "easy"
