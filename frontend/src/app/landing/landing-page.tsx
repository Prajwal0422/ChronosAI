"use client";

import { useState, useEffect } from "react";
import { AnimatePresence } from "framer-motion";
import { LoadingScreen } from "./loading-screen";
import { Navbar } from "./navbar";
import { HeroSection } from "./hero-section";
import { ActionCards } from "./action-cards";
import { FeaturesSection } from "./features-section";
import { AiWorkflow } from "./ai-workflow";
import { Footer } from "./footer";

export function LandingPage() {
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <AnimatePresence mode="wait">
      {loading ? (
        <LoadingScreen key="loading" onComplete={() => setLoading(false)} />
      ) : (
        <div key="content" className="min-h-screen bg-background">
          <Navbar />
          <main>
            <HeroSection />
            <ActionCards />
            <FeaturesSection />
            <AiWorkflow />
          </main>
          <Footer />
        </div>
      )}
    </AnimatePresence>
  );
}
