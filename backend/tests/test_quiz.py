"""
Tests for quiz generation schema validation.

Tests the Pydantic schemas and question validation logic
without requiring an actual LLM API call.
"""

import pytest

from app.schemas.quiz_schema import (
    DifficultyLevel,
    GenerateQuizRequest,
    QuestionType,
    QuizQuestionResponse,
)
from app.schemas.answer_schema import SubmitAnswerRequest


class TestQuizSchemas:
    """Validation tests for quiz-related Pydantic schemas."""

    def test_generate_quiz_request_defaults(self):
        req = GenerateQuizRequest()
        assert req.source_id is None
        assert req.topic is None
        assert req.num_chunks == 5
        assert req.difficulty is None

    def test_generate_quiz_request_with_values(self):
        req = GenerateQuizRequest(
            source_id=1, topic="Math", num_chunks=3, difficulty=DifficultyLevel.HARD
        )
        assert req.source_id == 1
        assert req.difficulty == DifficultyLevel.HARD

    def test_num_chunks_validation(self):
        with pytest.raises(Exception):
            GenerateQuizRequest(num_chunks=0)
        with pytest.raises(Exception):
            GenerateQuizRequest(num_chunks=25)

    def test_difficulty_enum_values(self):
        assert DifficultyLevel.EASY.value == "easy"
        assert DifficultyLevel.MEDIUM.value == "medium"
        assert DifficultyLevel.HARD.value == "hard"

    def test_question_type_enum(self):
        assert QuestionType.MCQ.value == "MCQ"
        assert QuestionType.TRUE_FALSE.value == "true_false"
        assert QuestionType.FILL_IN_THE_BLANK.value == "fill_in_the_blank"


class TestAnswerSchemas:
    """Validation tests for answer-related Pydantic schemas."""

    def test_submit_answer_request_valid(self):
        req = SubmitAnswerRequest(
            student_id="S001", question_id=12, selected_answer="3"
        )
        assert req.student_id == "S001"
        assert req.question_id == 12

    def test_submit_answer_empty_student_id(self):
        with pytest.raises(Exception):
            SubmitAnswerRequest(
                student_id="", question_id=1, selected_answer="A"
            )

    def test_submit_answer_invalid_question_id(self):
        with pytest.raises(Exception):
            SubmitAnswerRequest(
                student_id="S001", question_id=0, selected_answer="A"
            )

    def test_submit_answer_empty_answer(self):
        with pytest.raises(Exception):
            SubmitAnswerRequest(
                student_id="S001", question_id=1, selected_answer=""
            )


class TestQuestionValidation:
    """Tests for the quiz generation service's question validation logic."""

    def test_valid_mcq(self):
        from app.services.quiz_generation_service import QuizGenerationService
        svc = QuizGenerationService.__new__(QuizGenerationService)
        q = {
            "question": "What is 2+2?",
            "type": "MCQ",
            "options": ["1", "2", "3", "4"],
            "answer": "4",
        }
        assert svc._validate_question(q) is True

    def test_mcq_without_options(self):
        from app.services.quiz_generation_service import QuizGenerationService
        svc = QuizGenerationService.__new__(QuizGenerationService)
        q = {
            "question": "What is 2+2?",
            "type": "MCQ",
            "options": None,
            "answer": "4",
        }
        assert svc._validate_question(q) is False

    def test_valid_true_false(self):
        from app.services.quiz_generation_service import QuizGenerationService
        svc = QuizGenerationService.__new__(QuizGenerationService)
        q = {
            "question": "The earth is flat.",
            "type": "true_false",
            "options": ["True", "False"],
            "answer": "False",
        }
        assert svc._validate_question(q) is True

    def test_valid_fill_in_blank(self):
        from app.services.quiz_generation_service import QuizGenerationService
        svc = QuizGenerationService.__new__(QuizGenerationService)
        q = {
            "question": "The capital of France is ___.",
            "type": "fill_in_the_blank",
            "answer": "Paris",
        }
        assert svc._validate_question(q) is True

    def test_missing_required_fields(self):
        from app.services.quiz_generation_service import QuizGenerationService
        svc = QuizGenerationService.__new__(QuizGenerationService)
        assert svc._validate_question({"question": "Q?"}) is False
        assert svc._validate_question({"type": "MCQ"}) is False

    def test_invalid_type(self):
        from app.services.quiz_generation_service import QuizGenerationService
        svc = QuizGenerationService.__new__(QuizGenerationService)
        q = {"question": "Q?", "type": "essay", "answer": "A"}
        assert svc._validate_question(q) is False
