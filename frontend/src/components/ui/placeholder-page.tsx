"use client";

import Link from "next/link";
import { ArrowLeft, Construction } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface PlaceholderPageProps {
  title: string;
  description: string;
  breadcrumbs: { label: string; href: string }[];
}

export function PlaceholderPage({ title, description, breadcrumbs }: PlaceholderPageProps) {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="border-b border-border/30 bg-background/50 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
          <nav className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
            {breadcrumbs.map((crumb, i) => (
              <span key={crumb.label} className="flex items-center gap-2">
                {i > 0 && <span className="text-border">/</span>}
                {i === breadcrumbs.length - 1 ? (
                  <span className="text-foreground font-medium">{crumb.label}</span>
                ) : (
                  <Link href={crumb.href} className="hover:text-foreground transition-colors">
                    {crumb.label}
                  </Link>
                )}
              </span>
            ))}
          </nav>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="max-w-md w-full text-center">
          <div className="flex items-center justify-center w-20 h-20 rounded-2xl bg-primary/10 mx-auto mb-6">
            <Construction size={36} className="text-primary" />
          </div>

          <Badge variant="outline" className="mb-4 px-3 py-1 text-xs">
            Coming Soon
          </Badge>

          <h1 className="text-3xl font-bold tracking-tight mb-3">{title}</h1>
          <p className="text-muted-foreground mb-8 leading-relaxed">{description}</p>

          <Link href="/">
            <Button variant="outline" className="gap-2">
              <ArrowLeft size={15} />
              Back to Home
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
