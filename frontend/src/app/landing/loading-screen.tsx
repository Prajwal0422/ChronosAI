"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const loadingMessages = [
  { text: "Initializing ChronosAI", duration: 800 },
  { text: "Loading AI Scheduler", duration: 700 },
  { text: "Preparing Workspace", duration: 600 },
  { text: "Ready", duration: 400 },
];

interface LoadingScreenProps {
  onComplete: () => void;
}

export function LoadingScreen({ onComplete }: LoadingScreenProps) {
  const [step, setStep] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const totalDuration = loadingMessages.reduce((sum, m) => sum + m.duration, 0);
    let elapsed = 0;

    const intervals = loadingMessages.map((msg, i) => {
      return setTimeout(() => {
        setStep(i);
        elapsed += msg.duration;
        setProgress(Math.min((elapsed / totalDuration) * 100, 100));
        if (i === loadingMessages.length - 1) {
          setTimeout(onComplete, 300);
        }
      }, elapsed);
    });

    return () => intervals.forEach(clearTimeout);
  }, [onComplete]);

  return (
    <motion.div
      className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-background"
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5, ease: "easeInOut" }}
    >
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="flex flex-col items-center gap-8"
      >
        <div className="relative">
          <div className="text-5xl font-bold tracking-tight">
            <span className="gradient-text">C</span>
            <span className="text-foreground/80">hronos</span>
            <span className="gradient-text">AI</span>
          </div>
          <motion.div
            className="absolute -inset-4 rounded-full bg-primary/5 blur-2xl"
            animate={{ opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          />
        </div>

        <div className="flex flex-col items-center gap-3">
          <div role="status" aria-live="polite">
            <AnimatePresence mode="wait">
              <motion.p
                key={step}
                initial={{ y: 10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: -10, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="text-sm text-muted-foreground"
              >
                {loadingMessages[step].text}
              </motion.p>
            </AnimatePresence>
          </div>

          <div className="w-48 h-1 rounded-full bg-secondary overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-primary via-info to-primary"
              style={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
