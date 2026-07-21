"use client";

import Link from "next/link";
import { Github, Mail, ExternalLink } from "lucide-react";

const footerLinks = [
  {
    title: "Product",
    links: [
      { label: "Features", href: "/#features" },
      { label: "AI Engine", href: "/#workflow" },
      { label: "Documentation", href: "/documentation" },
      { label: "Pricing", href: "/pricing" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About", href: "/about" },
      { label: "Contact", href: "/contact" },
      { label: "Privacy Policy", href: "/privacy" },
      { label: "Terms", href: "/terms" },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "GitHub", href: "https://github.com", icon: ExternalLink },
      { label: "API Reference", href: "/documentation" },
      { label: "Status", href: "/" },
      { label: "Changelog", href: "/changelog" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="relative border-t border-border/30 bg-background/50 backdrop-blur-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div className="lg:col-span-1">
            <div className="flex items-center gap-2 mb-3">
              <Link href="/" className="text-xl font-bold tracking-tight">
                <span className="gradient-text">C</span>
                <span className="text-foreground/80">hronos</span>
                <span className="gradient-text">AI</span>
              </Link>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed max-w-xs">
              Enterprise-grade AI-powered academic timetable generation platform for modern institutions.
            </p>
            <div className="flex items-center gap-3 mt-5">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub"
                className="flex items-center justify-center w-9 h-9 rounded-lg border border-border/30 text-muted-foreground hover:text-foreground hover:border-border/60 transition-colors"
              >
                <Github size={16} />
              </a>
              <a
                href="mailto:info@chronosai.dev"
                aria-label="Email ChronosAI"
                className="flex items-center justify-center w-9 h-9 rounded-lg border border-border/30 text-muted-foreground hover:text-foreground hover:border-border/60 transition-colors"
              >
                <Mail size={16} />
              </a>
            </div>
          </div>

          {footerLinks.map((group) => (
            <div key={group.title}>
              <h4 className="text-sm font-semibold mb-3">{group.title}</h4>
              <ul className="space-y-2.5">
                {group.links.map((link) => (
                  <li key={link.label}>
                    {link.href.startsWith("http") ? (
                      <a
                        href={link.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-muted-foreground hover:text-foreground transition-colors inline-flex items-center gap-1"
                      >
                        {link.label}
                        {link.icon && <ExternalLink size={10} />}
                      </a>
                    ) : (
                      <Link
                        href={link.href}
                        className="text-sm text-muted-foreground hover:text-foreground transition-colors inline-flex items-center gap-1"
                      >
                        {link.label}
                        {link.icon && <ExternalLink size={10} />}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-10 pt-6 border-t border-border/20 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} ChronosAI. All rights reserved.</p>
          <p>Version 1.0.0</p>
        </div>
      </div>
    </footer>
  );
}
