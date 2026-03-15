import Link from "next/link";
import { BrainCircuit } from "lucide-react";

export function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-border/40 h-16 flex items-center px-6 justify-between">
      <div className="flex items-center gap-2">
        <BrainCircuit className="w-8 h-8 text-primary animate-glow-pulse" />
        <span className="text-xl font-bold text-gradient">Lumina AI</span>
      </div>
      <div className="flex items-center gap-6">
        <Link href="/dashboard" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
          Dashboard
        </Link>
        <Link href="/upload" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
          Upload
        </Link>
        <Link href="/analytics" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
          Analytics
        </Link>
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-neon-purple p-[1px]">
          <div className="w-full h-full rounded-full bg-background" />
        </div>
      </div>
    </nav>
  );
}
