"use client"

import { PDFUploader } from "@/components/features/PDFUploader"
import { AnimatedCard } from "@/components/features/AnimatedCard"
import { FileText, Cpu, Zap } from "lucide-react"

export default function UploadPage() {
  return (
    <div className="max-w-5xl mx-auto pb-12 pt-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">
          Generate <span className="text-gradient">AI Quizzes</span>
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Upload any PDF document. Our advanced AI engine will analyze the content, extract key learning objectives, and dynamically generate an adaptive assessment.
        </p>
      </div>

      <div className="mb-16">
        <PDFUploader />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
        <AnimatedCard delay={0.2} glowOnHover={false} className="bg-background/40">
          <div className="p-3 w-fit rounded-xl bg-neon-cyan/10 text-neon-cyan mb-4">
            <Cpu className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold mb-2">Deep Analysis</h3>
          <p className="text-sm text-muted-foreground">
            The system chunks your document and identifies core semantic concepts to test against.
          </p>
        </AnimatedCard>
        
        <AnimatedCard delay={0.3} glowOnHover={false} className="bg-background/40">
          <div className="p-3 w-fit rounded-xl bg-neon-purple/10 text-neon-purple mb-4">
            <Zap className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold mb-2">Instant Generation</h3>
          <p className="text-sm text-muted-foreground">
            Questions are generated in seconds using large language models perfectly calibrated for education.
          </p>
        </AnimatedCard>

        <AnimatedCard delay={0.4} glowOnHover={false} className="bg-background/40">
          <div className="p-3 w-fit rounded-xl bg-neon-pink/10 text-neon-pink mb-4">
            <FileText className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold mb-2">Multiple Formats</h3>
          <p className="text-sm text-muted-foreground">
            Generates multiple choice, true/false, and open-ended questions based on context.
          </p>
        </AnimatedCard>
      </div>
    </div>
  )
}
