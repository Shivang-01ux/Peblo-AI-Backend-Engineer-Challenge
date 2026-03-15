"""
PDF ingestion service.

Extracts raw text from uploaded PDF files using PyMuPDF (fitz).
"""

import os
from typing import Optional

import fitz  # PyMuPDF

from app.utils.logger import get_logger

logger = get_logger(__name__)


class PDFIngestionService:
    """Handles PDF upload, validation, and text extraction."""

    SUPPORTED_EXTENSIONS = {".pdf"}

    def validate_file(self, file_path: str) -> bool:
        """Check that the file exists and is a PDF."""
        if not os.path.isfile(file_path):
            logger.error("File not found: %s", file_path)
            return False
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            logger.error("Unsupported file type: %s", ext)
            return False
        return True

    def extract_text(self, file_path: str) -> str:
        """
        Extract all text from a PDF file.

        Args:
            file_path: Path to the PDF on disk.

        Returns:
            Concatenated text from all pages.

        Raises:
            ValueError: If the file is invalid or empty.
        """
        if not self.validate_file(file_path):
            raise ValueError(f"Invalid PDF file: {file_path}")

        logger.info("Extracting text from: %s", file_path)
        text_parts: list[str] = []

        try:
            doc = fitz.open(file_path)
            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text("text")
                if page_text.strip():
                    text_parts.append(page_text)
                    logger.debug(
                        "Page %d: extracted %d characters", page_num, len(page_text)
                    )
            doc.close()
        except Exception as exc:
            logger.exception("Failed to extract text from %s", file_path)
            raise ValueError(f"PDF extraction failed: {exc}") from exc

        full_text = "\n\n".join(text_parts)
        if not full_text.strip():
            raise ValueError("PDF contains no extractable text.")

        logger.info(
            "Extracted %d characters from %d pages", len(full_text), len(text_parts)
        )
        return full_text

    def extract_text_by_pages(self, file_path: str) -> list[dict]:
        """
        Extract text page-by-page with metadata.

        Returns:
            List of dicts with 'page_number' and 'text' keys.
        """
        if not self.validate_file(file_path):
            raise ValueError(f"Invalid PDF file: {file_path}")

        pages = []
        doc = fitz.open(file_path)
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text("text")
            if page_text.strip():
                pages.append({"page_number": page_num, "text": page_text})
        doc.close()
        return pages
