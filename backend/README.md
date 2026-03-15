# Peblo AI Mini — Content Ingestion + Adaptive Quiz Engine

Backend system that takes in educational PDFs, extracts and chunks the content, generates quiz questions through an LLM, and adjusts difficulty based on how students are performing.

Built for the Peblo Backend AI Engineer challenge.

---

## Architecture

The backend follows a layered architecture — API routes sit on top of service classes, which talk to repositories for database access. This keeps things modular and easy to test.

```
backend/
├── app/
│   ├── main.py              # FastAPI app, startup, CORS, health check
│   ├── config.py            # env-based settings (Pydantic)
│   ├── database.py          # SQLAlchemy engine + session
│   │
│   ├── api/                 # Route handlers
│   │   ├── ingest_api.py    # POST /ingest
│   │   ├── quiz_api.py      # POST /generate-quiz, GET /quiz
│   │   └── answer_api.py    # POST /submit-answer, GET /progress/:id
│   │
│   ├── services/            # Business logic
│   │   ├── pdf_ingestion_service.py    # PDF text extraction (PyMuPDF)
│   │   ├── text_cleaning_service.py    # whitespace cleanup, artifact removal
│   │   ├── chunking_service.py         # sentence-based chunking w/ overlap
│   │   ├── embedding_service.py        # SentenceTransformer embeddings
│   │   ├── quiz_generation_service.py  # LLM prompting + response parsing
│   │   ├── adaptive_engine.py          # difficulty adjustment logic
│   │   └── cache_service.py            # in-memory TTL cache
│   │
│   ├── repositories/        # Data access (SQLAlchemy queries)
│   │   ├── content_repository.py
│   │   ├── quiz_repository.py
│   │   └── student_repository.py
│   │
│   ├── models/              # ORM models (5 tables)
│   │   ├── source_document.py
│   │   ├── content_chunk.py
│   │   ├── quiz_question.py
│   │   ├── student_answer.py
│   │   └── student_progress.py
│   │
│   ├── schemas/             # Pydantic request/response models
│   │   ├── ingest_schema.py
│   │   ├── quiz_schema.py
│   │   └── answer_schema.py
│   │
│   └── utils/
│       ├── logger.py
│       ├── duplicate_detection.py    # cosine similarity check
│       └── difficulty_classifier.py  # easy/medium/hard transitions
│
├── tests/
│   ├── test_ingestion.py
│   ├── test_quiz.py
│   └── test_adaptive.py
│
├── sample_outputs/          # Example API responses + DB schema
├── .env.example
├── requirements.txt
└── README.md
```

### Data Flow

```
PDF Upload → Text Extraction → Cleaning → Chunking → Embeddings → Store in DB
                                                                       ↓
Student Progress ← Adaptive Engine ← Submit Answer ← Serve Quiz ← LLM Generation
```

---

## Setup

### What you need

- Python 3.11+
- A Groq API key (free at https://console.groq.com) — or OpenAI/Gemini key

### Installation

```bash
cd backend

# create venv
python -m venv venv
venv\Scripts\activate        # windows
# source venv/bin/activate   # mac/linux

# install deps
pip install -r requirements.txt

# setup env
cp .env.example .env
# open .env and paste your API key in LLM_API_KEY
```

### Running

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be at http://localhost:8000  
Swagger docs at http://localhost:8000/docs

### Environment Variables

| Variable | What it does |
|----------|-------------|
| `LLM_PROVIDER` | `groq`, `openai`, or `gemini` |
| `LLM_API_KEY` | your API key (don't commit this) |
| `LLM_MODEL` | model name, e.g. `llama-3.3-70b-versatile` |
| `DATABASE_URL` | defaults to `sqlite:///./peblo.db` (zero config) |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` (runs locally, no API needed) |
| `SKIP_QUALITY_SCORING` | `true` to skip per-question LLM scoring (faster) |
| `CHUNK_SIZE` | words per chunk (default 500) |
| `CHUNK_OVERLAP` | overlap between chunks (default 50) |

---

## API Endpoints

### `POST /ingest` — Upload and process a PDF

```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@peblo_pdf_grade4_english_grammar.pdf" \
  -F "title=English Grammar Grade 4" \
  -F "subject=English" \
  -F "grade=4"
```

What happens: extracts text with PyMuPDF, cleans it, splits into overlapping chunks, generates embeddings, stores everything.

### `POST /generate-quiz` — Generate questions from stored content

```bash
curl -X POST http://localhost:8000/generate-quiz \
  -H "Content-Type: application/json" \
  -d '{"source_id": 1, "num_chunks": 3, "difficulty": "medium"}'
```

Sends chunks to the LLM with a structured prompt. Gets back MCQ, true/false, and fill-in-the-blank questions. Each question links back to the source chunk it came from.

### `GET /quiz` — Retrieve stored questions

```bash
# get questions for a specific document
curl "http://localhost:8000/quiz?source_id=1&limit=20"

# filter by topic and difficulty
curl "http://localhost:8000/quiz?topic=Math&difficulty=easy"
```

### `POST /submit-answer` — Submit a student answer

```bash
curl -X POST http://localhost:8000/submit-answer \
  -H "Content-Type: application/json" \
  -d '{"student_id": "S001", "question_id": 1, "selected_answer": "3"}'
```

Evaluates correctness, records the answer, and runs the adaptive engine to update difficulty.

### `GET /progress/{student_id}` — Check student progress

```bash
curl http://localhost:8000/progress/S001
```

Returns accuracy, streaks, current difficulty level, total answered/correct.

### `GET /features` — Check which optional features are active

```bash
curl http://localhost:8000/features
```

---

## Database Schema

Five tables — everything traces back to the source document.

```
source_documents  →  content_chunks  →  quiz_questions  →  student_answers
                                                         ↗
                                        student_progress
```

- **source_documents**: PDF metadata (title, subject, grade, file hash for dedup)
- **content_chunks**: extracted text segments with embeddings, linked to source
- **quiz_questions**: LLM-generated questions with type, options, answer, difficulty, quality score — each linked to its source chunk
- **student_answers**: records of each answer submission (student, question, selected answer, correct/incorrect)
- **student_progress**: tracks streaks and current difficulty per student

Full schema is in `sample_outputs/database_schema.sql`.

---

## AI Integration

### Quiz Generation (quiz_generation_service.py)

- Uses a structured prompt that tells the LLM exactly what format to return (JSON array with specific keys)
- Asks for 4 MCQ + 1 true/false + 1 fill-in-the-blank per chunk
- Parses the response, strips markdown fences, validates each question
- Retry logic with exponential backoff if the API rate-limits us (3 retries, 5s/10s/20s delays)
- Works with Groq, OpenAI, and Gemini through the same OpenAI-compatible client

### Adaptive Difficulty (adaptive_engine.py)

Simple streak-based system:
- 2 correct answers in a row → difficulty goes up (easy → medium → hard)
- 2 wrong answers in a row → difficulty goes down (hard → medium → easy)
- Streaks reset after each difficulty change

This gets tracked per student in the `student_progress` table.

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

Covers text cleaning, chunking logic, question schema validation, and adaptive engine rules.

---

## Optional Features

These are all implemented and can be verified:

### Duplicate Question Detection (`utils/duplicate_detection.py`)
When generating new questions, each one gets an embedding vector (SentenceTransformer). We compare it against all existing question embeddings using cosine similarity. If similarity is above 0.90, the question gets skipped. This prevents the same question from being generated twice even if you re-run quiz generation on the same content.

### Question Validation (`services/quiz_generation_service.py`)
LLMs sometimes return malformed JSON or questions with wrong structure. The `_validate_question()` method checks every question coming back from the LLM — makes sure MCQs have exactly 4 options, true/false has 2, every question has an answer, etc. Bad questions get filtered silently.

### Embeddings for Similarity (`services/embedding_service.py`)
Uses `all-MiniLM-L6-v2` from SentenceTransformers to generate 384-dimensional vectors. Runs locally, no API calls needed. Used for both chunk embeddings and the duplicate detection system mentioned above.

### Caching (`services/cache_service.py`)
In-memory TTL cache. Student progress gets cached for 30 seconds so repeated dashboard refreshes don't hit the database every time. Cache gets invalidated when a new answer is submitted so the data stays fresh.

### Quality Scoring (`services/quiz_generation_service.py`)
Each generated question can optionally be scored by the LLM on a 1-10 scale for accuracy, clarity, educational value, and grammar. Disabled by default (`SKIP_QUALITY_SCORING=true`) because it adds an extra LLM call per question which slows things down. Set to `false` in `.env` to turn it on — scored questions will have a `quality_score` field.

---

## Sample Outputs

Example API responses are in the `sample_outputs/` directory:
- `ingestion_response.json` — what you get back after uploading a PDF
- `quiz_generation_response.json` — generated questions with MCQ, T/F, fill-in-blank
- `submit_answer_response.json` — response after submitting an answer
- `student_progress_response.json` — student progress with accuracy and streaks
- `database_schema.sql` — full database schema

---

## Tech Stack

| What | Using |
|------|-------|
| Framework | FastAPI |
| Database | SQLite (via SQLAlchemy) |
| PDF parsing | PyMuPDF |
| Text processing | NLTK |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) |
| LLM | Groq (Llama 3.3 70B) — also supports OpenAI, Gemini |
| Caching | In-memory TTL cache |
