"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Shield, Server, Cpu, BrainCircuit } from "lucide-react";

const techStack = [
  { name: "Next.js 14", role: "Frontend Framework", icon: Server },
  { name: "FastAPI", role: "Backend API", icon: Cpu },
  { name: "PostgreSQL", role: "Database", icon: Shield },
  { name: "SQLAlchemy 2.0", role: "ORM", icon: Server },
  { name: "Tailwind CSS", role: "Styling", icon: Server },
  { name: "Python 3.11", role: "AI Engine", icon: BrainCircuit },
];

const team = [
  { name: "ChronosAI Team", role: "Core Engineering", initials: "CA" },
  { name: "Research Lab", role: "AI & Optimization", initials: "RL" },
  { name: "Enterprise Solutions", role: "Integration", initials: "ES" },
];

const stats = [
  { label: "Timetables Generated", value: "12,000+" },
  { label: "Conflicts Resolved", value: "45,000+" },
  { label: "Institutions Served", value: "150+" },
  { label: "AI Model Version", value: "3.2" },
];

export default function AboutPage() {
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
            <Link href="/about" className="text-foreground font-medium">About</Link>
            <Link href="/login"><Button size="sm" variant="outline">Sign In</Button></Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-12 space-y-12">
          <section className="text-center space-y-4">
            <Badge variant="outline" className="px-3 py-1">v1.0.0</Badge>
            <h1 className="text-4xl font-bold tracking-tight">About ChronosAI</h1>
            <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
              Enterprise-grade academic scheduling platform powered by AI. We eliminate scheduling conflicts and optimize resource utilization for institutions worldwide.
            </p>
          </section>

          <section>
            <Card className="bg-gradient-to-br from-primary/5 via-primary/0 to-info/5 border-primary/10">
              <CardContent className="p-8">
                <p className="text-lg leading-relaxed">
                  ChronosAI combines constraint satisfaction algorithms with machine learning to generate optimal timetables.
                  Founded to solve the complex scheduling needs of modern educational institutions, the platform supports
                  everything from single-department schedules to multi-campus university-wide timetables.
                </p>
              </CardContent>
            </Card>
          </section>

          <section className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {stats.map((s) => (
              <Card key={s.label} className="text-center">
                <CardContent className="p-6">
                  <p className="text-2xl font-bold text-primary">{s.value}</p>
                  <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
                </CardContent>
              </Card>
            ))}
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-6">Technology Stack</h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {techStack.map((t) => (
                <Card key={t.name}>
                  <CardHeader className="flex flex-row items-center gap-3 p-4">
                    <div className="p-2 rounded-lg bg-primary/5"><t.icon size={18} className="text-primary" /></div>
                    <div><CardTitle className="text-sm">{t.name}</CardTitle><p className="text-xs text-muted-foreground">{t.role}</p></div>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-6">System Information</h2>
            <Card>
              <CardContent className="p-6 space-y-3">
                {[
                  ["Version", "1.0.0 (Build 2024)"],
                  ["AI Engine", "Constraint Propagation + Genetic Algorithm v3.2"],
                  ["API", "RESTful (FastAPI) — Swagger docs at /docs"],
                  ["Database", "PostgreSQL 16 (SQLite for development)"],
                  ["Authentication", "JWT with refresh token rotation"],
                  ["License", "Enterprise — All Rights Reserved"],
                ].map(([k, v]) => (
                  <div key={k} className="flex items-start gap-4 py-2 border-b border-border/20 last:border-0">
                    <span className="text-sm font-medium text-muted-foreground w-28 shrink-0">{k}</span>
                    <span className="text-sm">{v}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-6">Team</h2>
            <div className="grid sm:grid-cols-3 gap-4">
              {team.map((m) => (
                <Card key={m.name}>
                  <CardContent className="p-6 flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-sm font-bold text-primary">{m.initials}</div>
                    <div><p className="text-sm font-medium">{m.name}</p><p className="text-xs text-muted-foreground">{m.role}</p></div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>
        </div>
      </main>

      <footer className="border-t border-border/30 py-6 text-center text-xs text-muted-foreground">
        &copy; {new Date().getFullYear()} ChronosAI. All rights reserved.
      </footer>
    </div>
  );
}
