"use client"

import { motion } from "framer-motion"
import { Check, X } from "lucide-react"

interface QuizOptionButtonProps {
  optionText: string;
  isCorrect?: boolean | null;
  isSelected: boolean;
  onClick: () => void;
  disabled?: boolean;
  letter: string;
}

export function QuizOptionButton({ optionText, isCorrect, isSelected, onClick, disabled, letter }: QuizOptionButtonProps) {
  let stateClasses = "border-border/60 hover:border-primary/50 bg-secondary/30"
  
  if (isSelected && isCorrect === null) {
    stateClasses = "border-primary bg-primary/20 drop-shadow-[0_0_12px_rgba(157,0,255,0.3)]"
  } else if (isCorrect === true) {
    stateClasses = "border-neon-cyan bg-neon-cyan/20 drop-shadow-[0_0_12px_rgba(0,255,255,0.4)]"
  } else if (isCorrect === false && isSelected) {
    stateClasses = "border-neon-pink bg-neon-pink/20 drop-shadow-[0_0_12px_rgba(255,0,234,0.4)]"
  }

  return (
    <motion.button
      whileHover={!disabled ? { scale: 1.02 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      onClick={onClick}
      disabled={disabled}
      className={`w-full text-left p-5 rounded-xl border-2 transition-all flex items-center justify-between glass ${stateClasses}`}
    >
      <div className="flex items-center gap-4">
        <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-background/50 font-bold text-sm border border-border/40 text-muted-foreground">
          {letter}
        </span>
        <span className="font-medium text-lg text-foreground">{optionText}</span>
      </div>
      
      {isCorrect === true && (
        <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="text-neon-cyan bg-neon-cyan/10 p-1 rounded-full">
          <Check className="w-5 h-5" />
        </motion.div>
      )}
      
      {isCorrect === false && isSelected && (
        <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="text-neon-pink bg-neon-pink/10 p-1 rounded-full">
          <X className="w-5 h-5" />
        </motion.div>
      )}
    </motion.button>
  )
}
