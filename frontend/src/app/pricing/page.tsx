"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Check, X, BrainCircuit } from "lucide-react";

const plans = [
  {
    name: "Starter", price: "Free", period: "forever",
    features: ["1 Timetable", "50 Entries", "Basic Conflict Detection", "CSV Export", "Email Support"],
    missing: ["AI Optimization", "Advanced Analytics", "Role-Based Access", "API Access", "Priority Support"],
    popular: false,
  },
  {
    name: "Pro", price: "$29", period: "/month",
    features: ["10 Timetables", "5,000 Entries", "Advanced Conflict Resolution", "PDF/Excel Export", "AI-Powered Optimization", "Analytics Dashboard", "Role-Based Access", "Email + Chat Support"],
    missing: ["API Access", "Priority Support", "Custom Integration"],
    popular: true,
  },
  {
    name: "Enterprise", price: "$99", period: "/month",
    features: ["Unlimited Timetables", "Unlimited Entries", "Full AI Engine", "All Export Formats", "Global Search", "Version History", "Approval Workflows", "Audit Logs", "Full API Access", "Priority Support", "Custom Integration", "Dedicated Account Manager"],
    missing: [],
    popular: false,
  },
];

export default function PricingPage() {
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
            <Link href="/pricing" className="text-foreground font-medium">Pricing</Link>
            <Link href="/about" className="text-muted-foreground hover:text-foreground transition-colors">About</Link>
            <Link href="/login"><Button size="sm" variant="outline">Sign In</Button></Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-12 space-y-12">
          <section className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight">Simple, Transparent Pricing</h1>
            <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
              Choose the plan that fits your institution. Upgrade or downgrade at any time.
            </p>
          </section>

          <section className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {plans.map((p) => (
              <Card key={p.name} className={`relative ${p.popular ? 'border-primary/50 shadow-lg shadow-primary/5' : ''}`}>
                {p.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="px-3">Most Popular</Badge>
                  </div>
                )}
                <CardHeader className="text-center pb-4">
                  <CardTitle className="text-xl">{p.name}</CardTitle>
                  <div className="mt-3">
                    <span className="text-3xl font-bold">{p.price}</span>
                    <span className="text-muted-foreground text-sm">{p.period}</span>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    {p.features.map((f) => (
                      <div key={f} className="flex items-center gap-2 text-sm">
                        <Check size={14} className="text-green-500 shrink-0" />
                        <span>{f}</span>
                      </div>
                    ))}
                    {p.missing.map((f) => (
                      <div key={f} className="flex items-center gap-2 text-sm text-muted-foreground">
                        <X size={14} className="text-muted-foreground/40 shrink-0" />
                        <span className="line-through">{f}</span>
                      </div>
                    ))}
                  </div>
                  <Button className="w-full" variant={p.popular ? "default" : "outline"}>
                    {p.name === "Starter" ? "Get Started" : "Start Free Trial"}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </section>

          <section className="text-center">
            <Card className="max-w-2xl mx-auto bg-gradient-to-br from-primary/5 to-info/5 border-primary/10">
              <CardContent className="p-8">
                <h2 className="text-xl font-semibold mb-2">Need a Custom Plan?</h2>
                <p className="text-muted-foreground mb-4">Contact us for multi-campus deployments, custom integrations, or volume discounts.</p>
                <Link href="/contact"><Button variant="outline">Contact Sales</Button></Link>
              </CardContent>
            </Card>
          </section>
        </div>
      </main>

      <footer className="border-t border-border/30 py-6 text-center text-xs text-muted-foreground">
        &copy; {new Date().getFullYear()} ChronosAI. All rights reserved.
      </footer>
    </div>
  );
}
