import type { Metadata } from "next";
import { Toaster } from "react-hot-toast";
import { Providers } from "@/components/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Timetable Generator",
  description: "Enterprise-grade academic timetable generation system",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body>
        <a href="#main-content" className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-background focus:text-foreground focus:rounded-lg focus:border focus:border-border">
          Skip to main content
        </a>
        <Providers>
          <div id="main-content">
            {children}
          </div>
        </Providers>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: "hsl(240 10% 5.9%)",
              color: "hsl(0 0% 98%)",
              border: "1px solid hsl(240 5% 20%)",
              borderRadius: "0.75rem",
            },
            success: {
              iconTheme: { primary: "hsl(142 71% 45%)", secondary: "hsl(0 0% 98%)" },
            },
            error: {
              iconTheme: { primary: "hsl(0 62.8% 50.6%)", secondary: "hsl(0 0% 98%)" },
            },
          }}
        />
      </body>
    </html>
  );
}
