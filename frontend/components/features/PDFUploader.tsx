"use client"

import { useState, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { UploadCloud, File, X, CheckCircle2, BrainCircuit, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import { ingestPDF, generateQuiz } from "@/services/api"
import type { QuizQuestion } from "@/services/api"

interface PDFUploaderProps {
  onQuizReady?: (questions: QuizQuestion[], documentId: number) => void;
}

export function PDFUploader({ onQuizReady }: PDFUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [uploadStatus, setUploadStatus] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [generatedCount, setGeneratedCount] = useState(0)
  const [documentId, setDocumentId] = useState<number | null>(null)
  const [questions, setQuestions] = useState<QuizQuestion[]>([])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files?.[0]
    if (droppedFile && droppedFile.type === "application/pdf") {
      setFile(droppedFile)
      setError(null)
    }
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true)
    setError(null)
    
    try {
      // Step 1: Ingest the PDF
      setUploadStatus("Uploading and processing PDF...")
      const title = file.name.replace(/\.pdf$/i, "")
      const ingestResult = await ingestPDF(file, title)
      
      setUploadStatus("Generating adaptive quiz questions...")
      setDocumentId(ingestResult.document_id)
      
      // Step 2: Generate quiz from the ingested document
      const quizResult = await generateQuiz(ingestResult.document_id, "medium")
      
      setGeneratedCount(quizResult.questions_generated)
      setQuestions(quizResult.questions)
      setIsUploading(false)
      setIsSuccess(true)
      
      // Notify parent if callback provided
      if (onQuizReady) {
        onQuizReady(quizResult.questions, ingestResult.document_id)
      }
    } catch (err) {
      setIsUploading(false)
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.")
    }
  }

  const handleTakeQuiz = () => {
    // Navigate to quiz page with document context
    if (documentId && questions.length > 0) {
      // Store questions in sessionStorage so the quiz page can read them
      sessionStorage.setItem("quiz_questions", JSON.stringify(questions))
      sessionStorage.setItem("quiz_document_id", String(documentId))
      window.location.href = `/quiz?docId=${documentId}`
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <AnimatePresence mode="wait">
        {!file ? (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={cn(
              "border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-300 relative overflow-hidden group glass cursor-pointer",
              isDragging ? "border-primary bg-primary/5 scale-105" : "border-border/60 hover:border-primary/50"
            )}
          >
            <input 
              type="file" 
              accept=".pdf" 
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
              onChange={handleFileChange}
            />
            {isDragging && <div className="absolute inset-0 bg-primary/10 animate-pulse" />}
            
            <div className="relative z-20 flex flex-col items-center">
              <div className="w-20 h-20 rounded-full bg-secondary/80 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-[0_0_30px_rgba(157,0,255,0.2)]">
                <UploadCloud className={cn("w-10 h-10 transition-colors", isDragging ? "text-primary drop-shadow-[0_0_8px_rgba(157,0,255,0.8)]" : "text-muted-foreground group-hover:text-primary")} />
              </div>
              <h3 className="text-2xl font-bold mb-2">Upload Material</h3>
              <p className="text-muted-foreground mb-6 max-w-sm mx-auto">
                Drag and drop your PDF course material here, or click to browse. AI will analyze it to generate custom quizzes.
              </p>
              <span className="text-xs font-semibold px-3 py-1 bg-secondary rounded-full text-muted-foreground">
                Supported: PDF only (Max 10MB)
              </span>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="file-preview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-2xl p-8 neon-border before:opacity-30"
          >
            <div className="flex items-start justify-between mb-8 pb-6 border-b border-border/40">
              <div className="flex items-center gap-4">
                <div className="p-4 rounded-xl bg-neon-cyan/10 text-neon-cyan">
                  <File className="w-8 h-8" />
                </div>
                <div>
                  <h4 className="font-bold text-lg mb-1">{file.name}</h4>
                  <p className="text-sm text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
              {!isUploading && !isSuccess && (
                <button 
                  onClick={() => { setFile(null); setError(null); }}
                  className="p-2 hover:bg-secondary rounded-full transition-colors text-muted-foreground hover:text-white"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>

            {error && (
              <motion.div 
                initial={{ opacity: 0, y: -10 }} 
                animate={{ opacity: 1, y: 0 }}
                className="flex items-start gap-3 p-4 mb-6 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400"
              >
                <AlertCircle className="w-5 h-5 mt-0.5 shrink-0" />
                <div>
                  <h4 className="font-semibold text-sm mb-1">Upload Failed</h4>
                  <p className="text-sm opacity-80">{error}</p>
                </div>
              </motion.div>
            )}

            {isUploading && (
              <div className="py-6 text-center">
                <div className="w-16 h-16 border-4 border-secondary border-t-primary rounded-full animate-spin mx-auto mb-4 drop-shadow-[0_0_12px_rgba(157,0,255,0.6)]" />
                <h4 className="text-lg font-semibold animate-pulse">{uploadStatus}</h4>
                <p className="text-sm text-muted-foreground mt-2">Extracting key concepts, facts, and relations.</p>
              </div>
            )}

            {isSuccess && (
              <motion.div 
                initial={{ scale: 0.8, opacity: 0 }} 
                animate={{ scale: 1, opacity: 1 }} 
                className="py-6 text-center"
              >
                <CheckCircle2 className="w-16 h-16 text-neon-cyan mx-auto mb-4 drop-shadow-[0_0_12px_rgba(0,255,255,0.8)]" />
                <h4 className="text-xl font-bold text-gradient mb-2">Document Processed!</h4>
                <p className="text-muted-foreground">AI has created <strong className="text-foreground">{generatedCount}</strong> adaptive questions from your content.</p>
                <div className="mt-8 flex justify-center gap-4">
                  <button 
                    onClick={handleTakeQuiz}
                    className="px-6 py-2.5 rounded-lg font-semibold bg-primary hover:bg-primary/80 transition-opacity drop-shadow-[0_0_12px_rgba(157,0,255,0.4)]"
                  >
                    Take Quiz Now
                  </button>
                  <button onClick={() => { setFile(null); setIsSuccess(false); setError(null); }} className="px-6 py-2.5 rounded-lg font-semibold border border-border/50 hover:bg-secondary transition-colors">
                    Upload Another
                  </button>
                </div>
              </motion.div>
            )}

            {!isUploading && !isSuccess && !error && (
              <button 
                onClick={handleUpload}
                className="w-full py-4 rounded-xl font-semibold bg-primary text-primary-foreground hover:opacity-90 transition-opacity flex items-center justify-center gap-2 drop-shadow-[0_0_12px_rgba(157,0,255,0.4)]"
              >
                <BrainCircuit className="w-5 h-5" />
                Generate Quiz
              </button>
            )}

            {error && !isUploading && (
              <button 
                onClick={handleUpload}
                className="w-full py-4 rounded-xl font-semibold bg-primary text-primary-foreground hover:opacity-90 transition-opacity flex items-center justify-center gap-2 drop-shadow-[0_0_12px_rgba(157,0,255,0.4)]"
              >
                <BrainCircuit className="w-5 h-5" />
                Retry Upload
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
