"use client";

import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BrainCircuit } from "lucide-react";

export default function PrivacyPage() {
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
        <h1 className="text-3xl font-bold mb-2">Privacy Policy</h1>
        <p className="text-sm text-muted-foreground mb-8">Last updated: July 2024</p>

        <Card><CardContent className="p-6 space-y-6 text-sm leading-relaxed">
          <section>
            <h2 className="text-lg font-semibold mb-2">1. Information We Collect</h2>
            <p>We collect information you provide directly: name, email address, institution details, and timetable data. We also collect usage data including page views, feature interactions, and API calls to improve service quality.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">2. How We Use Your Data</h2>
            <p>Your data is used solely to provide and improve the ChronosAI service: generating timetables, detecting conflicts, optimizing schedules, and providing analytics. We do not sell personal data to third parties.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">3. Data Storage & Security</h2>
            <p>All data is encrypted at rest (AES-256) and in transit (TLS 1.3). We use industry-standard security practices including regular audits, access controls, and automated backups. Data is stored in SOC 2-compliant data centers.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">4. Data Retention</h2>
            <p>We retain your data for the duration of your account plus 90 days. You may request deletion of your data at any time. Backups are retained for 30 days.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">5. Your Rights</h2>
            <p>You have the right to access, correct, export, or delete your data. Subject to applicable law, you may also restrict or object to processing. Contact support@chronosai.com to exercise these rights.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">6. Cookies</h2>
            <p>We use essential cookies for authentication and session management. Analytics cookies are used only with consent. You can manage cookie preferences in your browser settings.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">7. Third-Party Services</h2>
            <p>We integrate with cloud infrastructure providers for hosting and storage. These providers are contractually bound to process data only on our instructions and maintain equivalent security standards.</p>
          </section>
          <section>
            <h2 className="text-lg font-semibold mb-2">8. Contact</h2>
            <p>For privacy-related inquiries, contact our Data Protection Officer at privacy@chronosai.com or through our <Link href="/contact" className="text-primary hover:underline">contact page</Link>.</p>
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
