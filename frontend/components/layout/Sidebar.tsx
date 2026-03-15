import Link from "next/link";
import { CopyPlus, LayoutDashboard, Brain, BarChart3, Settings } from "lucide-react";

export function Sidebar() {
  const navItems = [
    { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard" },
    { icon: CopyPlus, label: "Generate Quiz", href: "/upload" },
    { icon: Brain, label: "Adaptive Learning", href: "/quiz" },
    { icon: BarChart3, label: "Analytics", href: "/analytics" },
    { icon: Settings, label: "Settings", href: "/settings" },
  ];

  return (
    <aside className="fixed left-0 top-16 bottom-0 w-64 glass border-r border-border/40 flex flex-col p-4 z-40">
      <div className="space-y-2 mt-4 flex-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex items-center gap-3 px-4 py-3 rounded-lg text-muted-foreground hover:text-primary hover:bg-white/5 transition-all group relative"
          >
            <item.icon className="w-5 h-5 group-hover:text-primary group-hover:drop-shadow-[0_0_8px_rgba(157,0,255,0.8)] transition-all" />
            <span className="font-medium group-hover:text-foreground">{item.label}</span>
            <div className="absolute inset-y-0 left-0 w-1 bg-primary rounded-r-md opacity-0 group-hover:opacity-100 transition-opacity" />
          </Link>
        ))}
      </div>
      <div className="p-4 rounded-xl glass-card relative overflow-hidden mt-8">
        <div className="absolute -inset-2 bg-hero-glow opacity-30 animate-[spin_10s_linear_infinite]" />
        <div className="relative z-10">
          <h4 className="font-semibold text-sm text-foreground mb-1">PRO Membership</h4>
          <p className="text-xs text-muted-foreground mb-3">Unlock unlimited AI generations.</p>
          <button className="w-full py-2 bg-primary/20 hover:bg-primary/40 border border-primary/50 rounded-md text-sm font-semibold transition-all">
            Upgrade Now
          </button>
        </div>
      </div>
    </aside>
  );
}
