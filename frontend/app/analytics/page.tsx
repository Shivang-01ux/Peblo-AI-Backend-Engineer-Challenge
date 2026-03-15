"use client"

import { useState, useEffect } from "react"
import { AnimatedCard } from "@/components/features/AnimatedCard"
import { BrainCircuit, Target, Zap, TrendingUp } from "lucide-react"
import { getProgress } from "@/services/api"
import type { StudentProgress } from "@/services/api"
import { Loader2 } from "lucide-react"

const STUDENT_ID = "student_01"

export default function AnalyticsPage() {
  const [progress, setProgress] = useState<StudentProgress | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getProgress(STUDENT_ID)
        setProgress(data)
      } catch {
        // No data yet
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
    // Auto-refresh every 10 seconds for real-time updates
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  const accuracy = progress?.accuracy ?? 0
  const totalAnswered = progress?.total_answered ?? 0
  const totalCorrect = progress?.total_correct ?? 0
  const currentDifficulty = progress?.current_difficulty ?? "easy"
  const correctStreak = progress?.correct_streak ?? 0

  // Compute difficulty distribution from progress
  const difficultyLevel = currentDifficulty === "hard" ? 100 : currentDifficulty === "medium" ? 60 : 30

  return (
    <div className="max-w-6xl mx-auto pb-12 pt-4">
      <div className="mb-10">
        <h1 className="text-4xl font-bold mb-2">Detailed <span className="text-gradient">Analytics</span></h1>
        <p className="text-muted-foreground">Real-time AI-driven insights into your learning patterns and performance.</p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            {[
              { icon: Target, label: "Accuracy Rate", value: accuracy !== null ? `${Math.round(accuracy)}%` : "—", color: "text-neon-cyan" },
              { icon: BrainCircuit, label: "Questions Answered", value: String(totalAnswered), color: "text-primary" },
              { icon: TrendingUp, label: "Correct Answers", value: String(totalCorrect), color: "text-neon-pink" },
              { icon: Zap, label: "Current Streak", value: correctStreak > 0 ? `🔥 ${correctStreak}` : "0", color: "text-neon-purple" },
            ].map((stat, i) => (
              <AnimatedCard key={i} delay={i * 0.1} glowOnHover={false} className="bg-background/40">
                <div className={`p-3 w-fit rounded-xl bg-background/50 border border-border/40 mb-3 ${stat.color}`}>
                  <stat.icon className="w-5 h-5 drop-shadow-[0_0_8px_currentColor]" />
                </div>
                <span className="block text-sm text-muted-foreground mb-1">{stat.label}</span>
                <span className={`text-2xl font-bold ${stat.color}`}>{stat.value}</span>
              </AnimatedCard>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <AnimatedCard delay={0.4} className="flex flex-col border-border/40">
              <h3 className="text-lg font-bold mb-6">Performance Summary</h3>
              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 rounded-xl bg-background/50 border border-border/40">
                  <div>
                    <span className="block text-sm text-muted-foreground mb-1">Current Difficulty Level</span>
                    <span className="text-2xl font-bold capitalize text-primary">{currentDifficulty}</span>
                  </div>
                  <div className="text-right">
                    <span className="block text-sm text-muted-foreground mb-1">Adaptive Status</span>
                    <span className="text-sm font-semibold text-neon-cyan">
                      {correctStreak >= 2 ? "📈 Ready to level up!" : 
                       progress?.wrong_streak && progress.wrong_streak >= 2 ? "📉 Adjusting down" :
                       "⚡ Tracking performance"}
                    </span>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="font-medium text-muted-foreground">Score Progress</span>
                    <span className="font-bold">{totalCorrect} / {totalAnswered}</span>
                  </div>
                  <div className="h-3 w-full bg-secondary/50 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-neon-cyan to-primary rounded-full transition-all duration-500"
                      style={{ width: `${totalAnswered > 0 ? (totalCorrect / totalAnswered) * 100 : 0}%` }} 
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="font-medium text-muted-foreground">Difficulty Progress</span>
                    <span className="font-bold capitalize">{currentDifficulty}</span>
                  </div>
                  <div className="h-3 w-full bg-secondary/50 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-500 ${
                        difficultyLevel > 85 ? 'bg-neon-pink' : 
                        difficultyLevel > 50 ? 'bg-primary' : 'bg-neon-cyan'
                      }`}
                      style={{ width: `${difficultyLevel}%` }} 
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="font-medium text-muted-foreground">Points Earned</span>
                    <span className="font-bold text-neon-purple">{totalCorrect * 150} pts</span>
                  </div>
                  <div className="h-3 w-full bg-secondary/50 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-neon-purple rounded-full transition-all duration-500"
                      style={{ width: `${Math.min((totalCorrect * 150) / 1500 * 100, 100)}%` }} 
                    />
                  </div>
                </div>
              </div>
            </AnimatedCard>
            
            <AnimatedCard delay={0.5} className="flex flex-col border-border/40">
              <h3 className="text-lg font-bold mb-6">Adaptive Learning Insights</h3>
              
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-neon-cyan/5 border border-neon-cyan/20">
                  <h4 className="font-semibold text-neon-cyan mb-2">🧠 How Adaptive Difficulty Works</h4>
                  <p className="text-sm text-muted-foreground">
                    The AI tracks your answer streaks. <strong className="text-foreground">2 correct answers in a row</strong> increases 
                    difficulty. <strong className="text-foreground">2 wrong answers in a row</strong> decreases it. This ensures 
                    you&apos;re always challenged at the right level.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-background/50 border border-border/40">
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-sm text-muted-foreground">Correct Streak</span>
                    <span className="font-bold text-neon-cyan">{correctStreak}</span>
                  </div>
                  <div className="flex gap-1">
                    {[0, 1].map(i => (
                      <div 
                        key={i} 
                        className={`h-2 flex-1 rounded-full ${
                          i < correctStreak ? 'bg-neon-cyan' : 'bg-secondary/50'
                        }`} 
                      />
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    {correctStreak >= 2 ? "Level up triggered! ⬆️" : `${2 - correctStreak} more correct to level up`}
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-background/50 border border-border/40">
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-sm text-muted-foreground">Wrong Streak</span>
                    <span className="font-bold text-neon-pink">{progress?.wrong_streak ?? 0}</span>
                  </div>
                  <div className="flex gap-1">
                    {[0, 1].map(i => (
                      <div 
                        key={i} 
                        className={`h-2 flex-1 rounded-full ${
                          i < (progress?.wrong_streak ?? 0) ? 'bg-neon-pink' : 'bg-secondary/50'
                        }`} 
                      />
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    {(progress?.wrong_streak ?? 0) >= 2 ? "Level down triggered! ⬇️" : `${2 - (progress?.wrong_streak ?? 0)} more wrong to level down`}
                  </p>
                </div>
              </div>
            </AnimatedCard>
          </div>
        </>
      )}
    </div>
  )
}
