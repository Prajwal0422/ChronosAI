"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { BrainCircuit, Mail, MessageSquare, Clock, MapPin, Send, CheckCircle } from "lucide-react";
import { useState } from "react";

export default function ContactPage() {
  const [sent, setSent] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSent(true);
    setTimeout(() => setSent(false), 5000);
  };

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
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-12 space-y-12">
          <section className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight">Contact Us</h1>
            <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
              Have questions or need assistance? Reach out — we typically respond within 24 hours.
            </p>
          </section>

          <section className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Mail, label: "Email", value: "support@chronosai.com" },
              { icon: MessageSquare, label: "Live Chat", value: "Available 9am-5pm EST" },
              { icon: Clock, label: "Response Time", value: "Within 24 hours" },
            ].map((c) => (
              <Card key={c.label}>
                <CardContent className="p-6 flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-primary/5"><c.icon size={18} className="text-primary" /></div>
                  <div><p className="text-sm font-medium">{c.label}</p><p className="text-xs text-muted-foreground">{c.value}</p></div>
                </CardContent>
              </Card>
            ))}
          </section>

          <section className="grid md:grid-cols-5 gap-8">
            <Card className="md:col-span-3">
              <CardHeader><CardTitle>Send a Message</CardTitle></CardHeader>
              <CardContent>
                {sent ? (
                  <div className="text-center py-12">
                    <CheckCircle size={40} className="mx-auto mb-3 text-green-500" />
                    <p className="font-medium">Message sent!</p>
                    <p className="text-sm text-muted-foreground">We'll get back to you within 24 hours.</p>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid sm:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Name</label>
                        <Input placeholder="Your name" required />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Email</label>
                        <Input type="email" placeholder="you@institution.edu" required />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Subject</label>
                      <Input placeholder="How can we help?" required />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Message</label>
                      <Textarea rows={5} placeholder="Describe your question or issue..." required />
                    </div>
                    <Button type="submit" className="gap-2"><Send size={14} />Send Message</Button>
                  </form>
                )}
              </CardContent>
            </Card>

            <Card className="md:col-span-2">
              <CardHeader><CardTitle>Support Resources</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 rounded-lg bg-primary/5 space-y-2">
                  <p className="text-sm font-medium">📖 Documentation</p>
                  <p className="text-xs text-muted-foreground">Browse our comprehensive guides and API reference.</p>
                  <Link href="/documentation"><Button size="sm" variant="link" className="px-0">View Docs →</Button></Link>
                </div>
                <div className="p-4 rounded-lg bg-info/5 space-y-2">
                  <p className="text-sm font-medium">🐛 Report a Bug</p>
                  <p className="text-xs text-muted-foreground">Found an issue? Let us know and we'll fix it promptly.</p>
                  <Button size="sm" variant="link" className="px-0">Report Bug →</Button>
                </div>
                <div className="p-4 rounded-lg bg-success/5 space-y-2">
                  <p className="text-sm font-medium">💡 Feature Request</p>
                  <p className="text-xs text-muted-foreground">Have an idea? We'd love to hear your suggestions.</p>
                  <Button size="sm" variant="link" className="px-0">Suggest Feature →</Button>
                </div>
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
