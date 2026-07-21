"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BrainCircuit, Sparkles, Bug, Plus, ArrowUpRight } from "lucide-react";

const releases = [
  {
    version: "1.0.0", date: "July 2024", badge: "Major",
    items: [
      { icon: Sparkles, text: "Enterprise Academic Intelligence Suite with 10 new modules" },
      { icon: Sparkles, text: "AI-powered insights engine with 6 detection types" },
      { icon: Sparkles, text: "Health score system with 6 weighted metrics" },
      { icon: Sparkles, text: "What-if simulation with 6 scenario types" },
      { icon: Sparkles, text: "Version history with snapshot restore and compare" },
      { icon: Sparkles, text: "Approval workflow with full lifecycle management" },
      { icon: Sparkles, text: "Audit logging with action filtering and summary stats" },
      { icon: Sparkles, text: "Notification center with role-targeted alerts" },
      { icon: Sparkles, text: "Global search across 5 entity types" },
      { icon: Sparkles, text: "Enterprise settings with 7 configuration groups" },
      { icon: Sparkles, text: "Analytics dashboard with Recharts (bar, pie, line)" },
      { icon: Sparkles, text: "RBAC extended with 10 new permissions" },
    ],
  },
  {
    version: "0.9.0", date: "June 2024", badge: "Feature",
    items: [
      { icon: Sparkles, text: "AI generator with constraint propagation + genetic algorithm" },
      { icon: Sparkles, text: "Conflict detection and resolution engine" },
      { icon: Sparkles, text: "Real-time calendar view" },
      { icon: Sparkles, text: "PDF/Excel export with formatting" },
      { icon: Sparkles, text: "OCR import from scanned documents" },
    ],
  },
  {
    version: "0.8.0", date: "May 2024", badge: "Feature",
    items: [
      { icon: Plus, text: "CRUD management for all entities (colleges, departments, teachers, etc.)" },
      { icon: Plus, text: "Constraint manager with hard/soft rule configuration" },
      { icon: Plus, text: "Dashboard with stat cards, activity feed, calendar widget" },
      { icon: Plus, text: "Authentication with JWT + refresh token rotation" },
      { icon: Plus, text: "Role-based access control with 6 roles" },
    ],
  },
  {
    version: "0.5.0", date: "April 2024", badge: "Beta",
    items: [
      { icon: Bug, text: "Fixed room overlap detection in AI engine" },
      { icon: Bug, text: "Fixed tutorial slot type assignment" },
      { icon: Bug, text: "Fixed teacher unavailability conflict resolution" },
      { icon: Plus, text: "Landing page with hero, features, and AI workflow visualization" },
      { icon: Plus, text: "Dark glassmorphism theme system" },
      { icon: Plus, text: "Placeholder pages for upcoming modules" },
    ],
  },
  {
    version: "0.3.0", date: "March 2024", badge: "Alpha",
    items: [
      { icon: Plus, text: "Initial AI engine prototype with basic constraint solving" },
      { icon: Bug, text: "Fixed UUID parse errors in API" },
      { icon: Bug, text: "Fixed refresh-token rotation edge cases" },
    ],
  },
];

export default function ChangelogPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="border-b border-border/30 bg-background/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <BrainCircuit size={22} className="text-primary" />
            <span className="font-bold text-lg">ChronosAI</span>
          </Link>
          <nav className="flex items-center gap-6 text-sm">
            <Link href="/documentation" className="text-muted-foreground hover:text-foreground transition-colors">Docs</Link>
            <Link href="/pricing" className="text-muted-foreground hover:text-foreground transition-colors">Pricing</Link>
            <Link href="/about" className="text-muted-foreground hover:text-foreground transition-colors">About</Link>
            <Link href="/login"><Button size="sm" variant="outline">Sign In</Button></Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-12 space-y-12">
          <section className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight">Changelog</h1>
            <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
              Track every update, improvement, and fix across ChronosAI releases.
            </p>
          </section>

          <div className="relative">
            <div className="absolute left-6 top-0 bottom-0 w-px bg-border/50" />
            <div className="space-y-8">
              {releases.map((r) => (
                <Card key={r.version} className="relative ml-16">
                  <div className="absolute -left-16 top-6 w-8 h-8 rounded-full bg-background border-2 border-primary/30 flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-primary" />
                  </div>
                  <CardHeader className="pb-2">
                    <div className="flex items-center gap-3">
                      <CardTitle className="text-lg">v{r.version}</CardTitle>
                      <Badge variant={r.badge === "Major" ? "default" : r.badge === "Feature" ? "secondary" : "outline"}>{r.badge}</Badge>
                      <span className="text-xs text-muted-foreground">{r.date}</span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {r.items.map((item, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm">
                          <item.icon size={14} className="mt-0.5 shrink-0 text-primary" />
                          <span>{item.text}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-border/30 py-6 text-center text-xs text-muted-foreground">
        &copy; {new Date().getFullYear()} ChronosAI. All rights reserved.
      </footer>
    </div>
  );
}
