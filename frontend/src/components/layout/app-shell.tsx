"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Sidebar } from "./sidebar";
import { Navbar } from "./navbar";
import { Breadcrumbs } from "@/components/ui/breadcrumbs";
import { useAuthStore } from "@/stores/auth-store";
import { initAuth, isAuthenticated, needsWorkspace } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface AppShellProps {
  children: React.ReactNode;
  title?: string;
}

export function AppShell({ children, title }: AppShellProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { isLoading } = useAuthStore();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    initAuth();
  }, []);

  useEffect(() => {
    if (isLoading) return;
    if (!isAuthenticated()) {
      router.push("/login");
    } else if (needsWorkspace() && pathname !== "/select-institution") {
      router.push("/select-institution");
    }
  }, [isLoading, pathname, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
          <p className="text-sm text-muted-foreground">Loading workspace...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated() || needsWorkspace()) return null;

  return (
    <div className="min-h-screen bg-background">
      <Sidebar onCollapse={setSidebarCollapsed} />
      <div className={cn("transition-all duration-300", sidebarCollapsed ? "pl-[68px]" : "pl-[240px]")}>
        <Navbar title={title}>
          <Breadcrumbs />
        </Navbar>
        <main className="flex-1 p-6 pt-4">{children}</main>
      </div>
    </div>
  );
}
