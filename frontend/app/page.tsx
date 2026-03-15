"use client"

import { motion } from "framer-motion"
import Link from "next/link"
import { BrainCircuit, Sparkles, BookOpen, ChevronRight } from "lucide-react"
import { AnimatedCard } from "@/components/features/AnimatedCard"

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen items-center justify-center -mt-16 text-center z-10 relative">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="max-w-4xl mx-auto space-y-8"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-primary/30 text-primary text-sm font-medium mb-4">
          <Sparkles className="w-4 h-4" />
          <span>Next-Gen AI Learning Platform</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight">
          Master Any Subject <br />
          <span className="text-gradient">At Your Own Pace</span>
        </h1>
        
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          Upload any document. Our AI instantly generates adaptive quizzes, analyzes your weaknesses, and creates a personalized learning path just for you.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-8">
          <Link href="/upload">
            <button className="px-8 py-4 rounded-xl font-bold text-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-all hover:scale-105 active:scale-95 drop-shadow-[0_0_20px_rgba(157,0,255,0.5)] flex items-center gap-2">
              <BrainCircuit className="w-6 h-6" />
              Start Learning Now
            </button>
          </Link>
          <Link href="/dashboard">
            <button className="px-8 py-4 rounded-xl font-bold text-lg border-2 border-border/80 hover:border-primary/50 hover:bg-secondary/50 transition-all glass flex items-center gap-2">
              View Dashboard
              <ChevronRight className="w-5 h-5" />
            </button>
          </Link>
        </div>
      </motion.div>

      {/* Feature Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-24 max-w-5xl mx-auto px-6 w-full">
        {[
          { icon: BookOpen, title: "Smart Ingestion", desc: "Upload PDFs and instantly get structured learning materials." },
          { icon: BrainCircuit, title: "Adaptive Quizzes", desc: "Questions adapt in real-time based on your performance." },
          { icon: Sparkles, title: "AI Analytics", desc: "Detailed insights into your knowledge gaps and strengths." }
        ].map((feat, i) => (
          <AnimatedCard key={i} delay={0.4 + i * 0.1} className="text-left bg-background/40">
            <div className="p-3 w-fit rounded-xl bg-primary/10 text-primary mb-4">
              <feat.icon className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold mb-2">{feat.title}</h3>
            <p className="text-muted-foreground">{feat.desc}</p>
          </AnimatedCard>
        ))}
      </div>
    </div>
  )
}
