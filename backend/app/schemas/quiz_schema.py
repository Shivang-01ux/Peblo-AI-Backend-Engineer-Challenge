"""
Pydantic schemas for quiz generation and retrieval.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    MCQ = "MCQ"
    TRUE_FALSE = "true_false"
    FILL_IN_THE_BLANK = "fill_in_the_blank"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ── Request schemas ──────────────────────────────────────────────

class GenerateQuizRequest(BaseModel):
    """Request to generate quiz questions from stored chunks."""
    source_id: Optional[int] = Field(None, description="Source document ID (optional filter)")
    topic: Optional[str] = Field(None, description="Topic filter")
    num_chunks: int = Field(5, ge=1, le=20, description="How many chunks to use")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Target difficulty")


# ── Response schemas ─────────────────────────────────────────────

class QuizQuestionResponse(BaseModel):
    """A single quiz question."""
    id: int
    question: str
    type: str
    options: Optional[list[str]]
    answer: str
    difficulty: str
    source_chunk_id: int
    quality_score: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerateQuizResponse(BaseModel):
    """Response from quiz generation."""
    questions_generated: int
    questions: list[QuizQuestionResponse]
    message: str = "Quiz questions generated successfully"


class QuizListResponse(BaseModel):
    """Paginated list of quiz questions."""
    total: int
    questions: list[QuizQuestionResponse]
