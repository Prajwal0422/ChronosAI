"use client";

import { motion } from "framer-motion";
import {
  Brain, AlertTriangle, Users, Building2, DoorOpen, Beaker,
  BarChart3, FileDown, Scan, Zap,
} from "lucide-react";

const features = [
  { icon: Brain, title: "AI Constraint Solver", description: "Advanced CSP algorithms with MRV backtracking for optimal schedule generation." },
  { icon: AlertTriangle, title: "Conflict Detection", description: "Real-time detection and resolution of scheduling conflicts across all resources." },
  { icon: Users, title: "Faculty Management", description: "Manage teacher workloads, preferences, availability, and specializations." },
  { icon: Building2, title: "Department Management", description: "Multi-department support with independent scheduling and resource allocation." },
  { icon: DoorOpen, title: "Classroom Allocation", description: "Intelligent room assignment based on capacity, equipment, and location." },
  { icon: Beaker, title: "Laboratory Scheduling", description: "Specialized scheduling for lab sessions with duration and equipment requirements." },
  { icon: BarChart3, title: "Analytics", description: "Comprehensive insights into utilization, performance metrics, and trends." },
  { icon: FileDown, title: "Export to PDF/Excel", description: "Generate professional reports and share timetables in multiple formats." },
  { icon: Scan, title: "OCR Import", description: "Import existing timetables from scanned documents, images, or spreadsheets." },
  { icon: Zap, title: "Timetable Optimization", description: "Continuous improvement with genetic refinement and quality scoring." },
];

export function FeaturesSection() {
  return (
    <section id="features" className="relative py-20 sm:py-28">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/[0.02] to-transparent pointer-events-none" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
            Everything You Need to{" "}
            <span className="gradient-text">Schedule Smarter</span>
          </h2>
          <p className="mt-3 text-muted-foreground max-w-xl mx-auto">
            Enterprise-grade features designed for modern academic institutions.
          </p>
        </motion.div>

        <div className="grid gap-4 sm:gap-5 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {features.map((feature, i) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.4, delay: i * 0.05 }}
                className="group flex flex-col items-center text-center p-5 rounded-xl border border-border/20 bg-card/30 hover:bg-card/60 hover:border-border/40 transition-all duration-300"
              >
                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10 text-primary mb-3 group-hover:bg-primary/20 transition-colors">
                  <Icon size={18} />
                </div>
                <h3 className="text-sm font-semibold mb-1.5">{feature.title}</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">{feature.description}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
