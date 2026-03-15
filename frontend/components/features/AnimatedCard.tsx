"use client"

import { motion } from "framer-motion"
import { ReactNode } from "react"
import { cn } from "@/lib/utils"

interface AnimatedCardProps {
  children: ReactNode;
  className?: string;
  delay?: number;
  glowOnHover?: boolean;
}

export function AnimatedCard({ children, className, delay = 0, glowOnHover = true }: AnimatedCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.23, 1, 0.32, 1] }}
      whileHover={{ y: -5, scale: 1.01 }}
      className={cn(
        "glass-card p-6 rounded-2xl relative group",
        glowOnHover && "neon-border",
        className
      )}
    >
      {children}
    </motion.div>
  )
}
