"""
Quiz generation service.

Uses an LLM (OpenAI / Anthropic / Gemini) to generate quiz questions
from content chunks via structured prompt engineering.
"""

import json
import re
import time
from typing import Optional

import openai

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# ── Quiz generation prompt template ──────────────────────────────
QUIZ_PROMPT_TEMPLATE = """You are an expert educational content creator.

Generate quiz questions from the following educational text.

Text:
---
{text_chunk}
---

Subject: {subject}
Grade Level: {grade}
Target Difficulty: {difficulty}

Generate exactly 6 questions:
- 4 Multiple Choice Questions (MCQ) — each with exactly 4 options
- 1 True/False Question
- 1 Fill in the Blank Question

Return ONLY a valid JSON array. Each element must have these keys:
- "question": string (the question text)
- "type": string (one of "MCQ", "true_false", "fill_in_the_blank")
- "options": array of strings (4 options for MCQ, ["True","False"] for true_false, null for fill_in_the_blank)
- "answer": string (the correct answer)
- "difficulty": string (one of "easy", "medium", "hard")

Ensure:
- Factual correctness based strictly on the provided text
- Educational clarity and grade-appropriate language
- Each question is unique and tests a different concept
- For MCQ, make all 4 options plausible — avoid obviously wrong distractors

Return ONLY the JSON array, no markdown, no explanation.
"""

# ── Question quality scoring prompt ──────────────────────────────
QUALITY_PROMPT_TEMPLATE = """Rate the quality of this educational quiz question on a scale of 1-10.

Question: {question}
Type: {question_type}
Options: {options}
Answer: {answer}
Source Text: {source_text}

Evaluate based on:
1. Factual accuracy (does the answer match the source?)
2. Clarity (is the question unambiguous?)
3. Educational value (does it test understanding?)
4. Grammar and formatting

Return ONLY a JSON object: {{"score": <integer 1-10>, "feedback": "<brief feedback>"}}
"""


class QuizGenerationService:
    """Generates quiz questions from text chunks using LLM."""

    def __init__(self):
        api_key = settings.LLM_API_KEY
        if not api_key or api_key in ("PASTE_YOUR_API_KEY_HERE", "your-api-key-here", ""):
            raise RuntimeError(
                "LLM API key is not configured. Please set LLM_API_KEY in backend/.env "
                "with a valid API key for your chosen provider."
            )

        provider = settings.LLM_PROVIDER.lower()
        if provider == "gemini":
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        elif provider == "groq":
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
        else:
            self.client = openai.OpenAI(api_key=api_key)
        self.model = settings.LLM_MODEL

    def generate_questions(
        self,
        text_chunk: str,
        subject: str = "General",
        grade: int = 5,
        difficulty: str = "medium",
    ) -> list[dict]:
        """
        Generate quiz questions from a text chunk using the LLM.

        Args:
            text_chunk: The source text to generate questions from.
            subject: Subject area for context.
            grade: Grade level for difficulty calibration.
            difficulty: Target difficulty (easy/medium/hard).

        Returns:
            List of question dicts matching the quiz schema.
        """
        prompt = QUIZ_PROMPT_TEMPLATE.format(
            text_chunk=text_chunk,
            subject=subject,
            grade=grade,
            difficulty=difficulty,
        )

        max_retries = 3
        retry_delays = [5, 10, 20]  # seconds between retries

        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert quiz question generator. Always return valid JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                )

                raw_content = response.choices[0].message.content.strip()
                questions = self._parse_llm_response(raw_content)
                logger.info("Generated %d questions from LLM", len(questions))
                return questions

            except openai.RateLimitError as exc:
                if attempt < max_retries:
                    delay = retry_delays[attempt]
                    logger.warning(
                        "Rate limited (attempt %d/%d), retrying in %ds: %s",
                        attempt + 1, max_retries, delay, exc,
                    )
                    time.sleep(delay)
                    continue
                logger.error("Rate limit exceeded after %d retries", max_retries)
                raise RuntimeError(
                    "LLM rate limit exceeded. Please wait a moment and try again."
                ) from exc
            except openai.AuthenticationError as exc:
                logger.error("LLM authentication failed — check your API key: %s", exc)
                raise RuntimeError(
                    "LLM authentication failed. Please check your LLM_API_KEY in .env"
                ) from exc
            except openai.APIError as exc:
                logger.error("LLM API error: %s", exc)
                raise RuntimeError(f"LLM API error: {exc}") from exc
            except Exception as exc:
                logger.exception("Quiz generation failed")
                raise RuntimeError(f"Quiz generation failed: {exc}") from exc

        raise RuntimeError("Quiz generation failed after retries")

    def score_question_quality(
        self, question: str, question_type: str, options: list | None, answer: str, source_text: str
    ) -> dict:
        """
        Use the LLM to rate a question's quality (1-10).

        Returns:
            Dict with 'score' (int) and 'feedback' (str).
        """
        prompt = QUALITY_PROMPT_TEMPLATE.format(
            question=question,
            question_type=question_type,
            options=json.dumps(options) if options else "N/A",
            answer=answer,
            source_text=source_text[:500],  # truncate for token economy
        )

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Return valid JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=200,
                )
                raw = response.choices[0].message.content.strip()
                result = json.loads(self._clean_json(raw))
                return {"score": int(result.get("score", 5)), "feedback": result.get("feedback", "")}
            except openai.RateLimitError:
                if attempt < 2:
                    time.sleep(5 * (attempt + 1))
                    continue
                return {"score": 5, "feedback": "Rate limited during scoring"}
            except Exception as exc:
                logger.warning("Quality scoring failed: %s", exc)
                return {"score": 5, "feedback": "Unable to score"}

    # ── Helpers ──────────────────────────────────────────────────

    def _parse_llm_response(self, raw: str) -> list[dict]:
        """Parse and validate the LLM JSON response."""
        cleaned = self._clean_json(raw)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse LLM response: %s", raw[:200])
            raise ValueError(f"Invalid JSON from LLM: {exc}") from exc

        if isinstance(data, dict) and "questions" in data:
            data = data["questions"]

        if not isinstance(data, list):
            raise ValueError("LLM response is not a list of questions")

        validated: list[dict] = []
        for item in data:
            if self._validate_question(item):
                validated.append(item)
            else:
                logger.warning("Skipping invalid question: %s", item)

        return validated

    @staticmethod
    def _validate_question(q: dict) -> bool:
        """Check that a question dict has all required fields."""
        required = {"question", "type", "answer"}
        if not required.issubset(q.keys()):
            return False
        if q["type"] not in ("MCQ", "true_false", "fill_in_the_blank"):
            return False
        if q["type"] == "MCQ" and (not q.get("options") or len(q["options"]) < 2):
            return False
        return True

    @staticmethod
    def _clean_json(raw: str) -> str:
        """Strip markdown code fences if present."""
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return raw.strip()
