-- Database Schema (SQLite)
-- 5 tables: source_documents, content_chunks, quiz_questions, student_answers, student_progress

CREATE TABLE source_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(500) NOT NULL,
    filename VARCHAR(500) NOT NULL,
    subject VARCHAR(200),
    grade INTEGER,
    total_chunks INTEGER DEFAULT 0,
    file_hash VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE content_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL REFERENCES source_documents(id) ON DELETE CASCADE,
    chunk_id VARCHAR(100) UNIQUE NOT NULL,
    topic VARCHAR(300),
    text TEXT NOT NULL,
    embedding JSON,           -- 384-dim vector stored as JSON array
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE quiz_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,       -- MCQ, true_false, fill_in_the_blank
    options JSON,                     -- ["opt1","opt2","opt3","opt4"] or null
    answer VARCHAR(500) NOT NULL,
    difficulty VARCHAR(20) NOT NULL DEFAULT 'easy',
    source_chunk_id INTEGER NOT NULL REFERENCES content_chunks(id) ON DELETE CASCADE,
    quality_score INTEGER,           -- 1-10 LLM rating (optional)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE student_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(100) NOT NULL,
    question_id INTEGER NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,
    selected_answer VARCHAR(500) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE student_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(100) UNIQUE NOT NULL,
    current_difficulty VARCHAR(20) DEFAULT 'easy',
    correct_streak INTEGER DEFAULT 0,
    wrong_streak INTEGER DEFAULT 0,
    total_answered INTEGER DEFAULT 0,
    total_correct INTEGER DEFAULT 0,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
);
