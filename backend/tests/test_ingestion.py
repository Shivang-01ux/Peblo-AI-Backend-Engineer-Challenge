"""
Tests for the content ingestion pipeline.

Covers text cleaning, semantic chunking, and difficulty classification.
"""

import pytest

from app.services.text_cleaning_service import TextCleaningService
from app.services.chunking_service import ChunkingService
from app.utils.difficulty_classifier import (
    classify_text_difficulty,
    next_difficulty,
    previous_difficulty,
)


# ── TextCleaningService ──────────────────────────────────────────

class TestTextCleaning:
    """Unit tests for text cleaning pipeline."""

    def setup_method(self):
        self.cleaner = TextCleaningService()

    def test_clean_removes_extra_whitespace(self):
        raw = "Hello    world   this   is   a   test."
        result = self.cleaner.clean(raw)
        assert "    " not in result
        assert "Hello world this is a test." == result

    def test_clean_removes_page_numbers(self):
        raw = "Some text.\nPage 1\nMore text.\n- 2 -\nEnd."
        result = self.cleaner.clean(raw)
        assert "Page 1" not in result
        assert "- 2 -" not in result

    def test_clean_handles_empty_string(self):
        assert self.cleaner.clean("") == ""
        assert self.cleaner.clean("   ") == ""

    def test_sentence_tokenize(self):
        text = "This is sentence one. This is sentence two. And a third."
        sentences = self.cleaner.sentence_tokenize(text)
        assert len(sentences) == 3
        assert sentences[0] == "This is sentence one."

    def test_sentence_tokenize_empty(self):
        assert self.cleaner.sentence_tokenize("") == []

    def test_clean_collapses_newlines(self):
        raw = "Line one.\n\n\n\n\nLine two."
        result = self.cleaner.clean(raw)
        assert "\n\n\n" not in result


# ── ChunkingService ──────────────────────────────────────────────

class TestChunking:
    """Unit tests for semantic text chunking."""

    def test_basic_chunking(self):
        chunker = ChunkingService(chunk_size=10, chunk_overlap=2)
        text = ". ".join([f"Sentence number {i}" for i in range(20)]) + "."
        chunks = chunker.chunk_text(text, source_id="TEST")
        assert len(chunks) > 1
        assert all("chunk_id" in c for c in chunks)
        assert all("text" in c for c in chunks)

    def test_single_sentence(self):
        chunker = ChunkingService(chunk_size=100, chunk_overlap=10)
        text = "This is a single short sentence."
        chunks = chunker.chunk_text(text, source_id="TEST")
        assert len(chunks) == 1

    def test_empty_text(self):
        chunker = ChunkingService(chunk_size=100, chunk_overlap=10)
        chunks = chunker.chunk_text("", source_id="TEST")
        assert chunks == []

    def test_chunk_ids_are_unique(self):
        chunker = ChunkingService(chunk_size=10, chunk_overlap=2)
        text = ". ".join([f"This is sentence number {i}" for i in range(30)]) + "."
        chunks = chunker.chunk_text(text, source_id="1")
        ids = [c["chunk_id"] for c in chunks]
        assert len(ids) == len(set(ids))

    def test_chunk_id_format(self):
        chunker = ChunkingService(chunk_size=10, chunk_overlap=2)
        text = ". ".join([f"Sentence {i}" for i in range(10)]) + "."
        chunks = chunker.chunk_text(text, source_id="42")
        assert chunks[0]["chunk_id"].startswith("SRC_42_CH_")


# ── Difficulty Classifier ────────────────────────────────────────

class TestDifficultyClassifier:
    """Unit tests for difficulty classification utilities."""

    def test_simple_text_is_easy(self):
        text = "A cat sat on a mat. The dog ran."
        assert classify_text_difficulty(text) == "easy"

    def test_complex_text_with_high_grade(self):
        text = (
            "Photosynthesis involves the transformation of electromagnetic "
            "radiation into biochemical energy through chlorophyll absorption "
            "in the thylakoid membranes of chloroplasts."
        )
        result = classify_text_difficulty(text, grade=11)
        assert result in ("medium", "hard")

    def test_next_difficulty(self):
        assert next_difficulty("easy") == "medium"
        assert next_difficulty("medium") == "hard"
        assert next_difficulty("hard") == "hard"  # capped

    def test_previous_difficulty(self):
        assert previous_difficulty("hard") == "medium"
        assert previous_difficulty("medium") == "easy"
        assert previous_difficulty("easy") == "easy"  # capped

    def test_empty_text(self):
        assert classify_text_difficulty("") == "easy"
