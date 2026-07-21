"use client";

import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BrainCircuit } from "lucide-react";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="border-b border-border/30 bg-background/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <BrainCircuit size={22} className="text-primary" />
            <span className="font-bold text-lg">ChronosAI</span>
          </Link>
          <nav className="flex items-center gap-6 text-sm">
            <Link href="/login"><Button size="sm" variant="outline">Sign In</Button></Link>
          </nav>
        </div>
      </header>

      <main className="flex-1 mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold mb-2">Terms of Service</h1>
        <p className="text-sm text-muted-foreground mb-8">Last updated: July 2024</p>

        <Card><CardContent className="p-6 space-y-6 text-sm leading-relaxed">
          <section>
            <h2 className="text-lg font-semibold mb-2">1. Acceptance of Terms</h2>
            <p>By accessing or using ChronosAI, you agree to be bound by these Terms of Service. If you do not agree, do not use the service. These terms apply to all users, including administrators, faculty, and viewers.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">2. Service Description</h2>
            <p>ChronosAI provides AI-powered academic timetable generation, conflict detection, resource optimization, and enterprise scheduling tools. We reserve the right to modify or discontinue features with reasonable notice.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">3. User Responsibilities</h2>
            <p>You are responsible for maintaining the confidentiality of your account credentials, ensuring the accuracy of data you input, and using the service in compliance with applicable laws and institutional policies.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">4. Acceptable Use</h2>
            <p>You may not: reverse-engineer the AI engine, attempt to breach security, upload malicious content, exceed rate limits, or use the service for any unlawful purpose. Violations may result in immediate account termination.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">5. Intellectual Property</h2>
            <p>ChronosAI software, AI models, and brand assets are proprietary. Your timetable data remains your intellectual property. We claim no ownership over the schedules, courses, or institutional data you input.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">6. Service Level</h2>
            <p>We strive for 99.9% uptime for Enterprise plans. Scheduled maintenance is announced 48 hours in advance. The service is provided "as is" without warranty of uninterrupted or error-free operation.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">7. Limitation of Liability</h2>
            <p>ChronosAI shall not be liable for indirect damages including scheduling conflicts arising from inaccurate input data, lost productivity, or decisions based on AI-generated suggestions. Maximum liability is limited to fees paid in the last 12 months.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">8. Termination</h2>
            <p>Either party may terminate the agreement with 30 days written notice. Upon termination, you may export your data within 90 days. After 90 days, data is permanently deleted.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">9. Changes to Terms</h2>
            <p>We notify users of material changes via email and in-app notification 30 days before they take effect. Continued use after changes constitute acceptance of the updated terms.</p>
          </section>
        </CardContent></Card>

        <div className="mt-6 text-center">
          <Link href="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors">← Back to Home</Link>
        </div>
      </main>

      <footer className="border-t border-border/30 py-6 text-center text-xs text-muted-foreground">
        &copy; {new Date().getFullYear()} ChronosAI. All rights reserved.
      </footer>
    </div>
  );
}
