"use client"

import { motion } from "framer-motion"

interface ProgressTrackerProps {
  current: number;
  total: number;
  label?: string;
}

export function ProgressTracker({ current, total, label }: ProgressTrackerProps) {
  const percentage = Math.round((current / total) * 100);

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="flex justify-between items-end mb-2">
        {label && <span className="text-sm font-medium text-muted-foreground">{label}</span>}
        <span className="text-lg font-bold text-gradient">{percentage}%</span>
      </div>
      <div className="h-3 w-full bg-secondary/50 rounded-full overflow-hidden relative border border-border/40">
        <motion.div
          className="absolute top-0 left-0 bottom-0 bg-gradient-to-r from-primary to-neon-purple"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
        {/* Glow effect */}
        <motion.div
          className="absolute top-0 left-0 bottom-0 bg-white/30 blur-sm"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
      <div className="flex justify-between mt-1 text-xs text-muted-foreground">
        <span>Question {current} of {total}</span>
      </div>
    </div>
  )
}
