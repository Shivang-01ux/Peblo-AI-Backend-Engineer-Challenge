"use client"

import { motion } from "framer-motion"

interface DifficultyMeterProps {
  level: "Beginner" | "Intermediate" | "Advanced";
}

export function DifficultyMeter({ level }: DifficultyMeterProps) {
  const levels = ["Beginner", "Intermediate", "Advanced"]
  const activeIndex = levels.indexOf(level)

  const getColors = (index: number) => {
    if (index > activeIndex) return "bg-secondary/50 border-border/40"
    if (level === "Beginner") return "bg-neon-cyan border-neon-cyan drop-shadow-[0_0_8px_rgba(0,255,255,0.6)]"
    if (level === "Intermediate") return "bg-neon-purple border-neon-purple drop-shadow-[0_0_8px_rgba(157,0,255,0.6)]"
    return "bg-neon-pink border-neon-pink drop-shadow-[0_0_8px_rgba(255,0,234,0.6)]"
  }

  return (
    <div className="flex flex-col gap-2 w-full max-w-[200px]">
      <div className="flex justify-between text-xs font-semibold text-muted-foreground uppercase tracking-wider">
        <span>Difficulty</span>
        <span className={
          level === "Beginner" ? "text-neon-cyan" : 
          level === "Intermediate" ? "text-neon-purple" : 
          "text-neon-pink"
        }>
          {level}
        </span>
      </div>
      <div className="flex gap-1 h-2">
        {levels.map((_, i) => (
          <motion.div
            key={i}
            initial={{ scaleY: 0 }}
            animate={{ scaleY: 1 }}
            transition={{ delay: i * 0.1 + 0.5, duration: 0.3 }}
            className={`flex-1 rounded-full border ${getColors(i)}`}
          />
        ))}
      </div>
    </div>
  )
}
