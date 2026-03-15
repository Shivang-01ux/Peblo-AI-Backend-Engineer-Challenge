"use client"

import { useState, useEffect, Suspense } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useSearchParams } from "next/navigation"
import { ProgressTracker } from "@/components/features/ProgressTracker"
import { QuizOptionButton } from "@/components/features/QuizOptionButton"
import { DifficultyMeter } from "@/components/features/DifficultyMeter"
import { ArrowLeft, Check, FastForward, PlayCircle, Loader2 } from "lucide-react"
import Link from "next/link"
import { submitAnswer, getQuizBySource } from "@/services/api"
import type { QuizQuestion, SubmitAnswerResponse } from "@/services/api"

const STUDENT_ID = "student_01" // simple default for demo

const FALLBACK_QUESTIONS = [
  {
    id: -1,
    question: "What is the primary factor that causes the adaptive difficulty to increase in this AI system?",
    type: "MCQ",
    options: [
      "Answering questions slowly but correctly",
      "Consistently answering questions correctly in a row",
      "Uploading larger PDF files",
      "Selecting the 'Hard Mode' option in settings"
    ],
    answer: "Consistently answering questions correctly in a row",
    difficulty: "easy",
    source_chunk_id: 0,
    quality_score: null,
  },
  {
    id: -2,
    question: "Which of the following best describes 'Semantic Chunking' in document processing?",
    type: "MCQ",
    options: [
      "Splitting a document exactly every 500 words",
      "Grouping texts by paragraph formatting only",
      "Dividing text based on meaning, context, and topical boundaries",
      "Translating the document sentence by sentence"
    ],
    answer: "Dividing text based on meaning, context, and topical boundaries",
    difficulty: "medium",
    source_chunk_id: 0,
    quality_score: null,
  },
  {
    id: -3,
    question: "In the context of the RAG (Retrieval-Augmented Generation) pipeline, what role does the vector database play?",
    type: "MCQ",
    options: [
      "It generates the final quiz questions",
      "It stores mathematical representations of text chunks for fast similarity search",
      "It manages user authentication and payment processing",
      "It renders the 3D particle background in the frontend"
    ],
    answer: "It stores mathematical representations of text chunks for fast similarity search",
    difficulty: "hard",
    source_chunk_id: 0,
    quality_score: null,
  }
]

function mapDifficulty(diff: string): "Beginner" | "Intermediate" | "Advanced" {
  const d = diff.toLowerCase()
  if (d === "easy") return "Beginner"
  if (d === "hard") return "Advanced"
  return "Intermediate"
}

function QuizContent() {
  const searchParams = useSearchParams()
  const docId = searchParams.get("docId")

  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)

  const [hasStarted, setHasStarted] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selectedOption, setSelectedOption] = useState<number | null>(null)
  const [isAnswered, setIsAnswered] = useState(false)
  const [score, setScore] = useState(0)
  const [isFinished, setIsFinished] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Adaptive feedback state
  const [lastFeedback, setLastFeedback] = useState<SubmitAnswerResponse | null>(null)
  const [currentDifficulty, setCurrentDifficulty] = useState("medium")
  const [correctStreak, setCorrectStreak] = useState(0)

  // Load questions on mount
  useEffect(() => {
    async function loadQuestions() {
      // First try sessionStorage (from PDFUploader navigation)
      const storedQuestions = sessionStorage.getItem("quiz_questions")
      if (storedQuestions) {
        try {
          const parsed = JSON.parse(storedQuestions) as QuizQuestion[]
          // Use questions that have options (MCQ and true/false)
          const usable = parsed.filter(q => q.options && q.options.length >= 2)
          if (usable.length > 0) {
            setQuestions(usable)
            sessionStorage.removeItem("quiz_questions")
            setIsLoading(false)
            return
          }
        } catch { /* fall through */ }
      }

      // If we have a docId, FETCH existing questions from the DB (not regenerate)
      if (docId) {
        try {
          const result = await getQuizBySource(Number(docId))
          const usable = result.questions.filter(q => q.options && q.options.length >= 2)
          if (usable.length > 0) {
            setQuestions(usable)
            setIsLoading(false)
            return
          }
        } catch (err) {
          setLoadError(err instanceof Error ? err.message : "Failed to load questions")
        }
      }

      // Fallback to demo questions
      setQuestions(FALLBACK_QUESTIONS)
      setIsLoading(false)
    }

    loadQuestions()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [docId])

  const currentQuestion = questions[currentIndex]
  const isRealBackend = currentQuestion && currentQuestion.id > 0

  const handleStart = () => setHasStarted(true)

  const handleSelectOption = (index: number) => {
    if (isAnswered || isSubmitting) return;
    setSelectedOption(index)
  }

  const handleSubmit = async () => {
    if (selectedOption === null || !currentQuestion?.options) return;
    setIsSubmitting(true)
    setIsAnswered(true)

    const selectedText = currentQuestion.options[selectedOption]

    if (isRealBackend) {
      // Submit to backend for adaptive tracking
      try {
        const feedback = await submitAnswer(STUDENT_ID, currentQuestion.id, selectedText)
        setLastFeedback(feedback)
        setCurrentDifficulty(feedback.current_difficulty)
        setCorrectStreak(feedback.correct_streak)
        if (feedback.is_correct) {
          setScore(s => s + 1)
        }
      } catch {
        // If API fails, fall back to local check
        const isCorrect = selectedText.trim().toLowerCase() === currentQuestion.answer.trim().toLowerCase()
        if (isCorrect) setScore(s => s + 1)
        setLastFeedback(null)
      }
    } else {
      // Local check for fallback questions
      const isCorrect = selectedText.trim().toLowerCase() === currentQuestion.answer.trim().toLowerCase()
      if (isCorrect) setScore(s => s + 1)
      setLastFeedback(null)
    }
    setIsSubmitting(false)
  }

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(i => i + 1)
      setSelectedOption(null)
      setIsAnswered(false)
      setLastFeedback(null)
    } else {
      setIsFinished(true)
    }
  }

  const isCorrectLocal = () => {
    if (!currentQuestion?.options || selectedOption === null) return false;
    if (lastFeedback) return lastFeedback.is_correct;
    return currentQuestion.options[selectedOption].trim().toLowerCase() === currentQuestion.answer.trim().toLowerCase()
  }

  // ── Loading state ───────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh] text-center">
        <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
        <p className="text-muted-foreground font-medium">Loading quiz questions...</p>
      </div>
    )
  }

  if (loadError && questions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh] text-center max-w-md mx-auto">
        <p className="text-red-400 font-medium mb-4">{loadError}</p>
        <Link href="/upload" className="px-6 py-3 rounded-xl font-bold bg-primary text-primary-foreground hover:opacity-90 transition-opacity">
          Upload a PDF First
        </Link>
      </div>
    )
  }

  // ── Results screen ─────────────────────────────────────────────
  if (isFinished) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh] text-center max-w-2xl mx-auto">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="glass-card p-12 rounded-3xl w-full relative overflow-hidden neon-border"
        >
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-32 bg-primary/20 blur-[100px] rounded-full pointer-events-none" />
          
          <h2 className="text-4xl font-bold mb-6">Quiz Completed!</h2>
          
          <div className="relative mb-12">
            <svg className="w-48 h-48 mx-auto" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="45" fill="none" className="stroke-secondary" strokeWidth="8" />
              <motion.circle 
                cx="50" cy="50" r="45" fill="none" 
                className="stroke-primary" 
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray="283"
                initial={{ strokeDashoffset: 283 }}
                animate={{ strokeDashoffset: 283 - (283 * (score / questions.length)) }}
                transition={{ duration: 1.5, ease: "easeOut" }}
                transform="rotate(-90 50 50)"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-5xl font-extrabold text-gradient">{Math.round((score/questions.length)*100)}%</span>
              <span className="text-sm text-muted-foreground font-medium uppercase tracking-wider mt-1">Accuracy</span>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 text-left mb-10">
            <div className="bg-background/40 p-4 rounded-xl border border-border/40">
              <span className="text-xs text-muted-foreground uppercase tracking-wider block mb-1">Correct</span>
              <span className="text-2xl font-bold text-neon-cyan">{score}</span>
            </div>
            <div className="bg-background/40 p-4 rounded-xl border border-border/40">
              <span className="text-xs text-muted-foreground uppercase tracking-wider block mb-1">Points</span>
              <span className="text-2xl font-bold text-neon-purple">+{score * 150}</span>
            </div>
            <div className="bg-background/40 p-4 rounded-xl border border-border/40">
              <span className="text-xs text-muted-foreground uppercase tracking-wider block mb-1">Difficulty</span>
              <span className="text-2xl font-bold text-primary capitalize">{currentDifficulty}</span>
            </div>
          </div>

          <div className="flex gap-4">
            <Link href="/upload" className="flex-1">
              <button className="w-full py-4 rounded-xl font-bold bg-primary text-primary-foreground hover:opacity-90 transition-opacity">
                Upload New PDF
              </button>
            </Link>
            <Link href="/dashboard" className="flex-1">
              <button className="w-full py-4 rounded-xl font-bold bg-secondary/80 hover:bg-secondary transition-colors">
                Dashboard
              </button>
            </Link>
          </div>
        </motion.div>
      </div>
    )
  }

  // ── Start screen ───────────────────────────────────────────────
  if (!hasStarted) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh] text-center max-w-2xl mx-auto">
        <Link href="/dashboard" className="self-start mb-8 text-muted-foreground hover:text-primary transition-colors flex items-center gap-2">
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </Link>
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="glass-card p-10 rounded-3xl w-full">
          <div className="inline-flex py-1 px-3 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-widest mb-6">
            {isRealBackend ? "AI Generated" : "Demo Quiz"}
          </div>
          <h1 className="text-4xl font-bold mb-4">
            {docId ? "Your Custom Quiz" : "Understanding AI Systems"}
          </h1>
          <p className="text-muted-foreground mb-8">
            {docId 
              ? "Questions generated from your uploaded PDF. The AI will adapt difficulty based on your performance."
              : "This quiz will test your knowledge on the core architectural components of the platform."
            }
          </p>
          
          <div className="flex justify-between items-center bg-background/50 p-6 rounded-2xl mb-8 border border-border/40">
            <div className="text-left">
              <span className="block text-sm text-muted-foreground mb-1">Questions</span>
              <span className="text-xl font-bold">{questions.length}</span>
            </div>
            <div className="text-left">
              <span className="block text-sm text-muted-foreground mb-1">Difficulty</span>
              <span className="text-xl font-bold capitalize">{currentDifficulty}</span>
            </div>
            <div className="text-left">
              <span className="block text-sm text-muted-foreground mb-1">Adaptive</span>
              <span className="text-xl font-bold text-neon-cyan">{isRealBackend ? "Yes" : "Demo"}</span>
            </div>
          </div>

          <button 
            onClick={handleStart}
            className="w-full py-4 rounded-xl font-bold text-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity flex items-center justify-center gap-2 drop-shadow-[0_0_12px_rgba(157,0,255,0.4)]"
          >
            <PlayCircle className="w-5 h-5" />
            Start Quiz
          </button>
        </motion.div>
      </div>
    )
  }

  // ── Quiz in progress ───────────────────────────────────────────
  return (
    <div className="max-w-3xl mx-auto pt-4 pb-12">
      <div className="flex items-center justify-between mb-8">
        <Link href="/dashboard" className="text-muted-foreground hover:text-primary transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1 px-8">
          <ProgressTracker current={currentIndex + 1} total={questions.length} />
        </div>
      </div>

      {/* Adaptive difficulty banner */}
      {lastFeedback && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }} 
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 flex items-center gap-3 px-4 py-2 rounded-lg bg-background/50 border border-border/40 text-sm"
        >
          <span className="text-muted-foreground">Current Difficulty:</span>
          <span className="font-bold capitalize text-primary">{currentDifficulty}</span>
          {correctStreak > 1 && (
            <span className="text-neon-cyan font-medium">🔥 {correctStreak} streak!</span>
          )}
        </motion.div>
      )}

      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          initial={{ x: 50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -50, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="glass-card p-8 sm:p-10 rounded-3xl"
        >
          <div className="flex justify-between items-start mb-8 pb-6 border-b border-border/40">
            <span className="text-sm font-bold text-primary tracking-widest uppercase">
              Question {currentIndex + 1}
            </span>
            <DifficultyMeter level={mapDifficulty(currentQuestion.difficulty)} />
          </div>

          <h2 className="text-2xl md:text-3xl font-bold leading-relaxed mb-10">
            {currentQuestion.question}
          </h2>

          <div className="space-y-4 mb-10">
            {currentQuestion.options?.map((option, idx) => {
              const letter = String.fromCharCode(65 + idx)
              let isCorrectState = null
              
              if (isAnswered) {
                if (lastFeedback) {
                  // Use server response
                  if (option.trim().toLowerCase() === lastFeedback.correct_answer.trim().toLowerCase()) isCorrectState = true
                  else if (idx === selectedOption) isCorrectState = false
                } else {
                  // Local check
                  if (option.trim().toLowerCase() === currentQuestion.answer.trim().toLowerCase()) isCorrectState = true
                  else if (idx === selectedOption) isCorrectState = false
                }
              }

              return (
                <QuizOptionButton
                  key={idx}
                  letter={letter}
                  optionText={option}
                  isSelected={selectedOption === idx}
                  isCorrect={isCorrectState}
                  onClick={() => handleSelectOption(idx)}
                  disabled={isAnswered || isSubmitting}
                />
              )
            })}
          </div>

          <div className="flex justify-between items-center pt-6 border-t border-border/40 min-h-[88px]">
            {isAnswered && (
              <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
                {isCorrectLocal() ? (
                  <div className="flex items-center gap-2 text-neon-cyan">
                    <Check className="w-5 h-5" />
                    <span className="font-bold">
                      Correct! +150 Points
                      {lastFeedback && lastFeedback.correct_streak > 2 && " 🔥 Difficulty increasing!"}
                    </span>
                  </div>
                ) : (
                  <div className="flex flex-col gap-1 text-neon-pink">
                    <span className="font-bold">
                      Incorrect.
                      {lastFeedback && " The AI will adjust difficulty."}
                    </span>
                    {lastFeedback && (
                      <span className="text-xs text-muted-foreground">
                        Correct answer: {lastFeedback.correct_answer}
                      </span>
                    )}
                  </div>
                )}
              </motion.div>
            )}

            {!isAnswered ? (
              <button
                onClick={handleSubmit}
                disabled={selectedOption === null || isSubmitting}
                className={`ml-auto px-8 py-3 rounded-xl font-bold transition-all flex items-center gap-2 ${
                  selectedOption !== null && !isSubmitting
                    ? "bg-primary text-primary-foreground shadow-[0_0_15px_rgba(157,0,255,0.4)]" 
                    : "bg-secondary text-muted-foreground opacity-50 cursor-not-allowed"
                }`}
              >
                {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
                Submit Answer
              </button>
            ) : (
              <button
                onClick={handleNext}
                className="ml-auto px-8 py-3 rounded-xl font-bold bg-foreground text-background hover:opacity-90 transition-all flex items-center gap-2"
              >
                {currentIndex < questions.length - 1 ? 'Next Question' : 'View Results'}
                <FastForward className="w-4 h-4" />
              </button>
            )}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

export default function QuizPage() {
  return (
    <Suspense fallback={
      <div className="flex flex-col items-center justify-center min-h-[70vh] text-center">
        <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
        <p className="text-muted-foreground font-medium">Loading...</p>
      </div>
    }>
      <QuizContent />
    </Suspense>
  )
}
