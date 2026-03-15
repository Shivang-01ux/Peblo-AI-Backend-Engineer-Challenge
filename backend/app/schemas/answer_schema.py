"""
Pydantic schemas for answer submission and student progress.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Request schemas ──────────────────────────────────────────────

class SubmitAnswerRequest(BaseModel):
    """Payload when a student submits an answer."""
    student_id: str = Field(..., min_length=1, max_length=100)
    question_id: int = Field(..., gt=0)
    selected_answer: str = Field(..., min_length=1, max_length=500)


# ── Response schemas ─────────────────────────────────────────────

class SubmitAnswerResponse(BaseModel):
    """Feedback returned after answer submission."""
    is_correct: bool
    correct_answer: str
    current_difficulty: str
    correct_streak: int
    wrong_streak: int
    message: str


class StudentProgressResponse(BaseModel):
    """Current progress snapshot for a student."""
    student_id: str
    current_difficulty: str
    correct_streak: int
    wrong_streak: int
    total_answered: int
    total_correct: int
    accuracy: Optional[float] = None
    last_activity: Optional[datetime]

    model_config = {"from_attributes": True}
