const API_BASE = "http://localhost:8000";

// Helper to create a fetch with timeout
function fetchWithTimeout(url: string, options: RequestInit, timeoutMs: number): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  return fetch(url, { ...options, signal: controller.signal }).finally(() => clearTimeout(timeout));
}

async function extractError(res: Response, fallback: string): Promise<string> {
  try {
    const body = await res.json();
    return body.detail || body.message || fallback;
  } catch {
    return fallback;
  }
}

// ── Ingest a PDF ────────────────────────────────────────────────
export interface IngestResponse {
  document_id: number;
  title: string;
  total_chunks: number;
  message: string;
}

export async function ingestPDF(
  file: File,
  title: string,
  subject?: string
): Promise<IngestResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", title);
  if (subject) formData.append("subject", subject);

  let res: Response;
  try {
    res = await fetchWithTimeout(`${API_BASE}/ingest`, {
      method: "POST",
      body: formData,
    }, 120000); // 2 minute timeout for PDF processing
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error("PDF upload timed out. The file may be too large or the server is busy.");
    }
    throw new Error("Could not connect to the backend server. Make sure it is running on port 8000.");
  }

  if (!res.ok) {
    const detail = await extractError(res, "Upload failed");
    throw new Error(detail);
  }
  return res.json();
}

// ── Generate quiz from a document ────────────────────────────────
export interface QuizQuestion {
  id: number;
  question: string;
  type: string;
  options: string[] | null;
  answer: string;
  difficulty: string;
  source_chunk_id: number;
  quality_score: number | null;
}

export interface GenerateQuizResponse {
  questions_generated: number;
  questions: QuizQuestion[];
  message: string;
}

export async function generateQuiz(
  sourceId: number,
  difficulty?: "easy" | "medium" | "hard"
): Promise<GenerateQuizResponse> {
  const body: Record<string, unknown> = {
    source_id: sourceId,
    num_chunks: 5,
  };
  if (difficulty) body.difficulty = difficulty;

  let res: Response;
  try {
    res = await fetchWithTimeout(`${API_BASE}/generate-quiz`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }, 120000); // 2 minute timeout for LLM generation
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error("Quiz generation timed out. The AI is taking too long to respond.");
    }
    throw new Error("Could not connect to the backend server. Make sure it is running on port 8000.");
  }

  if (!res.ok) {
    const detail = await extractError(res, "Quiz generation failed");
    throw new Error(detail);
  }
  return res.json();
}


// ── Submit an answer ─────────────────────────────────────────────
export interface SubmitAnswerResponse {
  is_correct: boolean;
  correct_answer: string;
  current_difficulty: string;
  correct_streak: number;
  wrong_streak: number;
  message: string;
}

export async function submitAnswer(
  studentId: string,
  questionId: number,
  selectedAnswer: string
): Promise<SubmitAnswerResponse> {
  let res: Response;
  try {
    res = await fetchWithTimeout(`${API_BASE}/submit-answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_id: studentId,
        question_id: questionId,
        selected_answer: selectedAnswer,
      }),
    }, 15000);
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error("Answer submission timed out.");
    }
    throw new Error("Could not connect to the backend server.");
  }

  if (!res.ok) {
    const detail = await extractError(res, "Answer submission failed");
    throw new Error(detail);
  }
  return res.json();
}

// ── Get student progress ─────────────────────────────────────────
export interface StudentProgress {
  student_id: string;
  current_difficulty: string;
  correct_streak: number;
  wrong_streak: number;
  total_answered: number;
  total_correct: number;
  accuracy: number | null;
}

export async function getProgress(studentId: string): Promise<StudentProgress> {
  let res: Response;
  try {
    res = await fetchWithTimeout(`${API_BASE}/progress/${studentId}`, {}, 10000);
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error("Progress fetch timed out.");
    }
    throw new Error("Could not connect to the backend server.");
  }

  if (!res.ok) {
    const detail = await extractError(res, "Failed to fetch progress");
    throw new Error(detail);
  }
  return res.json();
}

// ── Get existing quiz questions by source document ───────────────
export interface QuizListResponse {
  total: number;
  questions: QuizQuestion[];
}

export async function getQuizBySource(sourceId: number, limit: number = 50): Promise<QuizListResponse> {
  let res: Response;
  try {
    res = await fetchWithTimeout(
      `${API_BASE}/quiz?source_id=${sourceId}&limit=${limit}`,
      {},
      15000
    );
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error("Quiz fetch timed out.");
    }
    throw new Error("Could not connect to the backend server.");
  }

  if (!res.ok) {
    const detail = await extractError(res, "Failed to fetch quiz questions");
    throw new Error(detail);
  }
  return res.json();
}
