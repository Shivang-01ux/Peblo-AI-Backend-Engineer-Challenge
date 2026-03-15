"""
Text cleaning service.

Normalizes and cleans raw extracted text using NLTK.
"""

import re
import unicodedata

import nltk

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Ensure NLTK data is available
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)


class TextCleaningService:
    """Cleans and normalizes raw text extracted from PDFs."""

    def clean(self, text: str) -> str:
        """
        Apply a full cleaning pipeline to raw text.

        Steps:
            1. Unicode normalization
            2. Remove control characters
            3. Collapse whitespace
            4. Remove page headers/footers patterns
            5. Strip leading/trailing whitespace
        """
        if not text:
            return ""

        text = self._normalize_unicode(text)
        text = self._remove_control_chars(text)
        text = self._remove_page_artifacts(text)
        text = self._collapse_whitespace(text)
        text = text.strip()

        logger.debug("Cleaned text to %d characters", len(text))
        return text

    def sentence_tokenize(self, text: str) -> list[str]:
        """Split text into sentences using NLTK."""
        if not text:
            return []
        sentences = nltk.sent_tokenize(text)
        return [s.strip() for s in sentences if s.strip()]

    # ── Private methods ──────────────────────────────────────────

    @staticmethod
    def _normalize_unicode(text: str) -> str:
        """Normalize Unicode to NFC form."""
        return unicodedata.normalize("NFC", text)

    @staticmethod
    def _remove_control_chars(text: str) -> str:
        """Remove non-printable control characters (keep newlines/tabs)."""
        return re.sub(r"[^\S \n\t]+", " ", text)

    @staticmethod
    def _remove_page_artifacts(text: str) -> str:
        """Remove common page number patterns and artifacts."""
        # Page numbers like "Page 1", "- 3 -", "1 of 10"
        text = re.sub(r"(?i)\bpage\s+\d+\s*(of\s+\d+)?\b", "", text)
        text = re.sub(r"\n\s*-?\s*\d+\s*-?\s*\n", "\n", text)
        return text

    @staticmethod
    def _collapse_whitespace(text: str) -> str:
        """Replace multiple spaces/newlines with single versions."""
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text
