"use client"

import { AnimatedCard } from "@/components/features/AnimatedCard"
import { Settings2, Bell, Shield, User, CreditCard } from "lucide-react"

export default function SettingsPage() {
  return (
    <div className="max-w-4xl mx-auto pb-12 pt-4">
      <div className="mb-10">
        <h1 className="text-4xl font-bold mb-2">Platform <span className="text-gradient">Settings</span></h1>
        <p className="text-muted-foreground">Manage your account, preferences, and subscription.</p>
      </div>

      <div className="grid gap-6">
        <AnimatedCard delay={0.1} glowOnHover={false} className="bg-background/40">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-neon-cyan/10 text-neon-cyan">
              <User className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-bold mb-1">Profile Information</h3>
              <p className="text-sm text-muted-foreground mb-4">Update your personal details and learning goals.</p>
              <div className="space-y-4">
                <div className="flex flex-col gap-1.5">
                  <label className="text-sm font-medium">Display Name</label>
                  <input type="text" defaultValue="Student_01" className="bg-background border border-border/50 rounded-lg px-4 py-2 focus:outline-none focus:border-primary transition-colors hover:border-border/80" />
                </div>
                <button className="px-4 py-2 bg-primary/20 hover:bg-primary/30 text-primary font-medium rounded-lg transition-colors border border-primary/20">
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </AnimatedCard>

        <AnimatedCard delay={0.2} glowOnHover={false} className="bg-background/40">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-neon-purple/10 text-neon-purple">
              <Bell className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-bold mb-1">Notifications</h3>
              <p className="text-sm text-muted-foreground mb-4">Choose what you want to be notified about.</p>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 rounded-lg border border-border/40 bg-secondary/20">
                  <div>
                    <h4 className="font-medium">Daily Reminders</h4>
                    <p className="text-xs text-muted-foreground">Get reminded to keep your learning streak.</p>
                  </div>
                  <div className="w-10 h-6 bg-primary rounded-full relative cursor-pointer opacity-80 hover:opacity-100 transition-opacity">
                    <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full" />
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg border border-border/40 bg-secondary/20">
                  <div>
                    <h4 className="font-medium">New Quizzes</h4>
                    <p className="text-xs text-muted-foreground">When AI finishes generating an uploaded PDF.</p>
                  </div>
                  <div className="w-10 h-6 bg-primary rounded-full relative cursor-pointer opacity-80 hover:opacity-100 transition-opacity">
                    <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </AnimatedCard>

        <AnimatedCard delay={0.3} glowOnHover={false} className="bg-background/40">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-neon-pink/10 text-neon-pink">
              <CreditCard className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-bold mb-1">Subscription</h3>
              <p className="text-sm text-muted-foreground mb-4">Manage your Lumina AI PRO membership.</p>
              <div className="p-4 rounded-xl border border-primary/30 bg-primary/5 flexitems-center justify-between relative overflow-hidden">
                <div className="absolute -inset-4 bg-hero-glow opacity-20 animate-[spin_10s_linear_infinite]" />
                <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <h4 className="font-bold text-lg">PRO Tier</h4>
                    <p className="text-sm text-muted-foreground">Unlimited generates & advanced analytics.</p>
                  </div>
                  <button className="px-6 py-2 bg-background border border-border/60 rounded-lg font-medium hover:bg-secondary transition-colors">
                    Manage Billing
                  </button>
                </div>
              </div>
            </div>
          </div>
        </AnimatedCard>
      </div>
    </div>
  )
}
