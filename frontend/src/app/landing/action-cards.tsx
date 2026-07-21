"use client";

import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ArrowRight, Upload, Shield, Sparkles } from "lucide-react";

const cards = [
  {
    icon: Sparkles,
    title: "Generate Timetable",
    description: "Create a brand-new timetable using AI optimization.",
    buttonLabel: "Start Generation",
    href: "/timetables/new",
    variant: "default" as const,
  },
  {
    icon: Upload,
    title: "Generate Using Existing Data",
    description: "Import PDF, Excel, CSV, or images. AI understands your existing timetable and recreates it automatically.",
    buttonLabel: "Import Files",
    href: "/import",
    variant: "default" as const,
  },
  {
    icon: Shield,
    title: "Administrator Login",
    description: "Secure portal for administrators, timetable coordinators, principals, and department heads.",
    buttonLabel: "Sign In",
    href: "/login",
    variant: "outline" as const,
  },
];

export function ActionCards() {
  const router = useRouter();

  return (
    <section className="relative py-20 sm:py-28">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
            Get Started in{" "}
            <span className="gradient-text">Seconds</span>
          </h2>
          <p className="mt-3 text-muted-foreground max-w-lg mx-auto">
            Choose how you want to begin — whether from scratch, from existing data, or by signing in.
          </p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-3">
          {cards.map((card, i) => {
            const Icon = card.icon;
            return (
              <motion.div
                key={card.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-80px" }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="group relative flex flex-col rounded-xl border border-border/40 bg-card/50 backdrop-blur-sm p-6 sm:p-8 hover:bg-card/80 hover:border-border/60 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300"
              >
                <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-primary/10 text-primary mb-5 group-hover:bg-primary/15 transition-colors">
                  <Icon size={22} />
                </div>

                <h3 className="text-lg font-semibold mb-2">{card.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed mb-6 flex-1">
                  {card.description}
                </p>

                <Button
                  variant={card.variant}
                  className="w-full"
                  onClick={() => router.push(card.href)}
                >
                  {card.buttonLabel}
                  <ArrowRight size={14} className="ml-2" />
                </Button>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
