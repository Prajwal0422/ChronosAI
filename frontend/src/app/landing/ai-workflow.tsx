"use client";

import { motion } from "framer-motion";
import { Upload, Brain, SlidersHorizontal, CheckCircle2, FileSpreadsheet, Download } from "lucide-react";

const steps = [
  { icon: Upload, label: "Upload", description: "Import subject data, teacher info, and classroom details." },
  { icon: Brain, label: "AI Analysis", description: "Our engine analyzes constraints and relationships." },
  { icon: SlidersHorizontal, label: "Constraint Optimization", description: "Applies hard and soft constraints with priority scoring." },
  { icon: CheckCircle2, label: "Conflict Resolution", description: "Detects and resolves scheduling conflicts automatically." },
  { icon: FileSpreadsheet, label: "Generate Timetable", description: "Produces conflict-free timetables with quality scores." },
  { icon: Download, label: "Export", description: "Download in PDF, Excel, or publish instantly." },
];

export function AiWorkflow() {
  return (
    <section id="workflow" className="relative py-20 sm:py-28 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/[0.03] to-transparent pointer-events-none" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
            From Data to{" "}
            <span className="gradient-text">Optimized Schedule</span>
          </h2>
          <p className="mt-3 text-muted-foreground max-w-xl mx-auto">
            See how ChronosAI transforms raw data into a polished, conflict-free academic timetable.
          </p>
        </motion.div>

        <div className="relative">
          <div className="hidden lg:block absolute top-1/2 left-[10%] right-[10%] h-0.5 bg-gradient-to-r from-primary/20 via-info/20 to-primary/20 -translate-y-1/2" />

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
            {steps.map((step, i) => {
              const Icon = step.icon;
              return (
                <motion.div
                  key={step.label}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ duration: 0.5, delay: i * 0.1 }}
                  className="relative flex flex-col items-center text-center group"
                >
                  <div className="relative z-10 flex items-center justify-center w-14 h-14 rounded-2xl bg-card border border-border/40 shadow-sm mb-4 group-hover:border-primary/30 group-hover:shadow-primary/5 transition-all duration-300">
                    <Icon size={22} className="text-primary" />
                  </div>
                  <div className="absolute top-7 left-1/2 -translate-x-1/2 w-14 h-14 rounded-2xl bg-primary/5 blur-lg group-hover:bg-primary/10 transition-all duration-300" />
                  <h3 className="text-sm font-semibold mb-1.5">{step.label}</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed max-w-[180px]">{step.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
