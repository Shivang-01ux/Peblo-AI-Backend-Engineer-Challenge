"use client"

import { BrainCircuit, Clock, Trophy } from "lucide-react"
import { AnimatedCard } from "./AnimatedCard"

interface QuizCardProps {
  title: string;
  topic: string;
  questionsCount: number;
  estimatedTime: number; // in mins
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  index: number;
}

export function QuizCard({ title, topic, questionsCount, estimatedTime, difficulty, index }: QuizCardProps) {
  const difficultyColors = {
    Beginner: "text-neon-cyan drop-shadow-[0_0_8px_rgba(0,255,255,0.8)]",
    Intermediate: "text-neon-purple drop-shadow-[0_0_8px_rgba(157,0,255,0.8)]",
    Advanced: "text-neon-pink drop-shadow-[0_0_8px_rgba(255,0,234,0.8)]",
  }

  return (
    <AnimatedCard delay={index * 0.1} className="flex flex-col h-full hover:cursor-pointer">
      <div className="flex justify-between items-start mb-4">
        <div className="p-3 rounded-xl bg-primary/10 text-primary">
          <BrainCircuit className="w-6 h-6" />
        </div>
        <span className={`text-xs font-bold tracking-wider uppercase ${difficultyColors[difficulty]}`}>
          {difficulty}
        </span>
      </div>
      
      <h3 className="text-xl font-bold mb-2 text-foreground group-hover:text-primary transition-colors">
        {title}
      </h3>
      <p className="text-sm text-muted-foreground mb-6 flex-grow">
        Topic: <span className="text-foreground/80">{topic}</span>
      </p>

      <div className="flex items-center justify-between text-xs text-muted-foreground pt-4 border-t border-border/40">
        <div className="flex items-center gap-1.5">
          <Trophy className="w-4 h-4" />
          <span>{questionsCount} Qs</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Clock className="w-4 h-4" />
          <span>{estimatedTime}m</span>
        </div>
      </div>
    </AnimatedCard>
  )
}
