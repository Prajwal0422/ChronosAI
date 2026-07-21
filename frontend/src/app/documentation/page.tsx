"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { BrainCircuit, Search, ChevronRight, BookOpen, Cpu, Shield, Users, Settings, Download, ExternalLink } from "lucide-react";

const sections = [
  {
    id: "getting-started", title: "Getting Started", icon: BookOpen,
    items: [
      { title: "Quick Start Guide", desc: "Set up your first timetable in 5 minutes" },
      { title: "Installation", desc: "Deploy ChronosAI on your infrastructure" },
      { title: "Configuration", desc: "Configure institutions, departments, and settings" },
      { title: "Authentication", desc: "User roles, permissions, and SSO setup" },
    ],
  },
  {
    id: "ai-engine", title: "AI Engine", icon: Cpu,
    items: [
      { title: "Constraint Propagation", desc: "How the solver assigns slots with hard/soft constraints" },
      { title: "Genetic Algorithm", desc: "Evolutionary optimization for timetable quality" },
      { title: "Conflict Detection", desc: "Real-time conflict identification and resolution" },
      { title: "Health Scoring", desc: "6-metric evaluation system (A+ to F)" },
    ],
  },
  {
    id: "enterprise", title: "Enterprise Features", icon: Shield,
    items: [
      { title: "Analytics Dashboard", desc: "Visualize workload, utilization, and trends" },
      { title: "AI Insights", desc: "Automated suggestions to improve timetable quality" },
      { title: "What-If Simulation", desc: "Test scheduling changes before applying them" },
      { title: "Version History", desc: "Snapshot, restore, and compare timetables" },
      { title: "Approval Workflow", desc: "Submit, review, approve, and publish cycles" },
      { title: "Audit Logs", desc: "Complete action trail for compliance" },
      { title: "Notifications", desc: "Real-time alerts for system events" },
      { title: "Global Search", desc: "Instant search across all entities" },
    ],
  },
  {
    id: "api", title: "API Reference", icon: Settings,
    items: [
      { title: "Authentication", desc: "JWT tokens, refresh rotation, and API keys" },
      { title: "Timetables", desc: "CRUD operations, generation, and export" },
      { title: "Entities", desc: "Teachers, subjects, rooms, labs, and more" },
      { title: "Analytics", desc: "8 analytical endpoints with aggregation" },
      { title: "Webhooks", desc: "Event-driven integration with external systems" },
    ],
  },
  {
    id: "guides", title: "Integration Guides", icon: Users,
    items: [
      { title: "REST API Tutorial", desc: "Build custom integrations with ChronosAI" },
      { title: "Bulk Import", desc: "Import data from CSV, Excel, or OCR" },
      { title: "Export & Reports", desc: "Generate PDF/Excel reports programmatically" },
      { title: "Webhook Setup", desc: "Configure event notifications for external services" },
    ],
  },
];

export default function DocumentationPage() {
  const [searchQuery, setSearchQuery] = useState("");

  const filtered = searchQuery.trim()
    ? sections.map(s => ({
        ...s,
        items: s.items.filter(i => i.title.toLowerCase().includes(searchQuery.toLowerCase()) || i.desc.toLowerCase().includes(searchQuery.toLowerCase())),
      })).filter(s => s.items.length > 0)
    : sections;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="border-b border-border/30 bg-background/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <BrainCircuit size={22} className="text-primary" />
            <span className="font-bold text-lg">ChronosAI</span>
          </Link>
          <nav className="flex items-center gap-6 text-sm">
            <Link href="/documentation" className="text-foreground font-medium">Docs</Link>
            <Link href="/pricing" className="text-muted-foreground hover:text-foreground transition-colors">Pricing</Link>
            <Link href="/about" className="text-muted-foreground hover:text-foreground transition-colors">About</Link>
            <Link href="/login"><Button size="sm" variant="outline">Sign In</Button></Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-12 space-y-8">
          <section className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight">Documentation</h1>
            <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
              Comprehensive guides, API references, and integration tutorials.
            </p>
            <div className="relative max-w-md mx-auto">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search documentation..."
                className="pl-9"
              />
            </div>
          </section>

          <div className="grid md:grid-cols-5 gap-8">
            <nav className="md:col-span-1 space-y-1 sticky top-20 self-start">
              {sections.map((s) => (
                <a key={s.id} href={`#${s.id}`} className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-muted/30 transition-colors">
                  <s.icon size={14} />
                  <span>{s.title}</span>
                </a>
              ))}
            </nav>

            <div className="md:col-span-4 space-y-10">
              {filtered.length === 0 ? (
                <Card><CardContent className="p-12 text-center text-muted-foreground">
                  <Search size={32} className="mx-auto mb-3 opacity-30" />
                  <p>No documentation found for "{searchQuery}"</p>
                </CardContent></Card>
              ) : filtered.map((s) => (
                <section key={s.id} id={s.id}>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 rounded-lg bg-primary/5"><s.icon size={20} className="text-primary" /></div>
                    <h2 className="text-2xl font-semibold">{s.title}</h2>
                  </div>
                  <div className="grid sm:grid-cols-2 gap-3">
                    {s.items.map((item) => (
                      <Card key={item.title} className="hover:bg-muted/20 transition-colors cursor-pointer group">
                        <CardContent className="p-4 flex items-start justify-between">
                          <div>
                            <p className="text-sm font-medium group-hover:text-primary transition-colors">{item.title}</p>
                            <p className="text-xs text-muted-foreground mt-0.5">{item.desc}</p>
                          </div>
                          <ChevronRight size={14} className="mt-1 text-muted-foreground group-hover:text-primary transition-colors shrink-0" />
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </section>
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
