"use client"

import { useState, useEffect } from "react"
import { ProgressTracker } from "@/components/features/ProgressTracker"
import { AnimatedCard } from "@/components/features/AnimatedCard"
import { getProgress } from "@/services/api"
import type { StudentProgress } from "@/services/api"
import { Loader2 } from "lucide-react"
import Link from "next/link"

const STUDENT_ID = "student_01"

export default function Dashboard() {
  const [progress, setProgress] = useState<StudentProgress | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Fetch real-time progress from backend
  useEffect(() => {
    async function fetchProgress() {
      try {
        const data = await getProgress(STUDENT_ID)
        setProgress(data)
      } catch {
        // No progress yet — that's fine
      } finally {
        setIsLoading(false)
      }
    }
    fetchProgress()
    // Refresh every 10 seconds for real-time updates
    const interval = setInterval(fetchProgress, 10000)
    return () => clearInterval(interval)
  }, [])

  const accuracy = progress?.accuracy ?? 0
  const totalAnswered = progress?.total_answered ?? 0
  const totalCorrect = progress?.total_correct ?? 0
  const currentDifficulty = progress?.current_difficulty ?? "easy"
  const correctStreak = progress?.correct_streak ?? 0
  const wrongStreak = progress?.wrong_streak ?? 0

  return (
    <div className="max-w-6xl mx-auto pb-12">
      <div className="mb-10">
        <h1 className="text-4xl font-bold mb-2">Welcome Back, <span className="text-gradient">Student</span></h1>
        <p className="text-muted-foreground">Here is your real-time AI-driven learning dashboard.</p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
            <AnimatedCard delay={0.1} className="col-span-1 lg:col-span-2">
              <h3 className="text-xl font-bold mb-6">Overall Progress</h3>
              <ProgressTracker 
                current={totalCorrect} 
                total={Math.max(totalAnswered, 1)} 
                label="Accuracy" 
              />
              
              <div className="flex justify-between mt-8 pt-6 border-t border-border/40">
                <div className="text-center">
                  <span className="block text-2xl font-bold text-neon-cyan">{totalAnswered}</span>
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">Questions Answered</span>
                </div>
                <div className="text-center">
                  <span className="block text-2xl font-bold text-neon-purple">
                    {accuracy !== null ? `${Math.round(accuracy)}%` : "—"}
                  </span>
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">Accuracy</span>
                </div>
                <div className="text-center">
                  <span className="block text-2xl font-bold text-neon-pink capitalize">{currentDifficulty}</span>
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">Difficulty</span>
                </div>
              </div>
            </AnimatedCard>

            <AnimatedCard delay={0.2} className="bg-primary/5 border-primary/20">
              <h3 className="text-xl font-bold mb-4">Current Streak</h3>
              <div className="flex flex-col items-center justify-center py-4">
                <div className="relative mb-4">
                  <div className="w-24 h-24 rounded-full border-4 border-neon-cyan/20 flex items-center justify-center relative z-10 bg-background/50 backdrop-blur-sm">
                    <span className="text-4xl font-bold text-neon-cyan drop-shadow-[0_0_8px_rgba(0,255,255,0.8)]">
                      {correctStreak > 0 ? correctStreak : wrongStreak}
                    </span>
                  </div>
                  <div className="absolute inset-0 bg-neon-cyan/20 blur-xl rounded-full z-0 animate-pulse" />
                </div>
                <span className="text-sm font-medium text-muted-foreground">
                  {correctStreak > 0 
                    ? `🔥 ${correctStreak} correct in a row!` 
                    : wrongStreak > 0 
                      ? `${wrongStreak} wrong — keep trying!`
                      : "Start a quiz to begin!"
                  }
                </span>
              </div>
            </AnimatedCard>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            <AnimatedCard delay={0.3} glowOnHover={false} className="bg-background/40">
              <span className="block text-sm text-muted-foreground mb-1">Total Correct</span>
              <span className="text-3xl font-bold text-neon-cyan">{totalCorrect}</span>
            </AnimatedCard>
            <AnimatedCard delay={0.35} glowOnHover={false} className="bg-background/40">
              <span className="block text-sm text-muted-foreground mb-1">Total Answered</span>
              <span className="text-3xl font-bold text-neon-purple">{totalAnswered}</span>
            </AnimatedCard>
            <AnimatedCard delay={0.4} glowOnHover={false} className="bg-background/40">
              <span className="block text-sm text-muted-foreground mb-1">Points Earned</span>
              <span className="text-3xl font-bold text-neon-pink">{totalCorrect * 150}</span>
            </AnimatedCard>
          </div>

          <div className="flex justify-between items-end mb-6">
            <div>
              <h2 className="text-2xl font-bold">Quick Actions</h2>
              <p className="text-sm text-muted-foreground">Jump into a quiz or upload new content.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Link href="/upload">
              <AnimatedCard delay={0.5} className="hover:border-primary/50 transition-colors cursor-pointer">
                <h3 className="text-lg font-bold mb-2">📄 Upload New PDF</h3>
                <p className="text-sm text-muted-foreground">Upload study material and generate an AI-adaptive quiz.</p>
              </AnimatedCard>
            </Link>
            <Link href="/quiz">
              <AnimatedCard delay={0.6} className="hover:border-primary/50 transition-colors cursor-pointer">
                <h3 className="text-lg font-bold mb-2">🧠 Take a Quiz</h3>
                <p className="text-sm text-muted-foreground">Test your knowledge with previously generated questions.</p>
              </AnimatedCard>
            </Link>
          </div>
        </>
      )}
    </div>
  )
}
