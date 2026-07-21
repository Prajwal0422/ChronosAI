"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { api } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";
import { updateProfile, isAuthenticated } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Brain, Building2, ArrowRight, LogOut } from "lucide-react";
import { logout as authLogout } from "@/lib/auth";

interface College {
  id: string;
  name: string;
  code: string;
  address: string | null;
  academic_year: string;
}

interface CollegesResponse {
  items: College[];
  total: number;
}

export default function SelectInstitutionPage() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
    }
  }, [router]);

  const { data, isLoading } = useQuery<CollegesResponse>({
    queryKey: ["colleges"],
    queryFn: () => api.get<CollegesResponse>("/colleges"),
    enabled: isAuthenticated(),
  });

  const selectMutation = useMutation({
    mutationFn: (collegeId: string) => updateProfile({ college_id: collegeId }),
    onSuccess: (updatedUser) => {
      useAuthStore.getState().setUser({
        id: updatedUser.id,
        email: updatedUser.email,
        full_name: updatedUser.full_name,
        role: updatedUser.role,
        college_id: updatedUser.college_id,
        department_id: updatedUser.department_id,
        is_active: updatedUser.is_active,
      });
      router.push("/dashboard");
    },
  });

  function handleLogout() {
    authLogout();
  }

  if (!isAuthenticated()) return null;

  return (
    <div className="min-h-screen flex items-center justify-center bg-background overflow-hidden p-4">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/8 via-transparent to-info/8 pointer-events-none" />
      <div className="absolute top-1/3 left-1/4 w-[500px] h-[500px] rounded-full bg-primary/3 blur-[150px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full bg-info/3 blur-[120px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="relative w-full max-w-2xl"
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="flex items-center justify-between mb-8"
        >
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-12 h-12 rounded-2xl bg-primary/10">
              <Brain size={28} className="text-primary" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold tracking-tight">
                <span className="gradient-text">C</span>hronos
                <span className="gradient-text">AI</span>
              </span>
              <span className="text-xs text-muted-foreground">Select Institution</span>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            <LogOut size={14} />
            Sign out
          </button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="rounded-2xl border border-border/40 bg-card/60 backdrop-blur-2xl p-8 shadow-xl shadow-black/10"
        >
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold tracking-tight">Choose your workspace</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Select an institution to manage its timetable and academic data
            </p>
          </div>

          {user && (
            <div className="flex items-center justify-center gap-2 mb-6 text-sm text-muted-foreground">
              <span>Signed in as</span>
              <span className="font-medium text-foreground">{user.email}</span>
              <span className="capitalize px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs">
                {user.role}
              </span>
            </div>
          )}

          <div className="space-y-3">
            {isLoading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="p-4 rounded-xl border border-border/30">
                  <Skeleton className="h-5 w-48 mb-2" />
                  <Skeleton className="h-3 w-64" />
                </div>
              ))
            ) : data?.items.length === 0 ? (
              <div className="text-center py-8">
                <Building2 size={40} className="mx-auto text-muted-foreground/40 mb-3" />
                <p className="text-sm text-muted-foreground">No institutions available</p>
                <p className="text-xs text-muted-foreground/60 mt-1">
                  Contact your administrator to get access
                </p>
              </div>
            ) : (
              data?.items.map((college, i) => (
                <motion.div
                  key={college.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.05 * i }}
                >
                  <button
                    onClick={() => selectMutation.mutate(college.id)}
                    disabled={selectMutation.isPending}
                    className="w-full text-left p-4 rounded-xl border border-border/30 bg-background/40 hover:bg-accent/30 hover:border-primary/30 transition-all duration-200 group"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-primary/5 group-hover:bg-primary/10 transition-colors">
                          <Building2 size={20} className="text-primary" />
                        </div>
                        <div>
                          <p className="font-medium">{college.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {college.address ?? college.code} &middot; AY {college.academic_year}
                          </p>
                        </div>
                      </div>
                      <ArrowRight size={16} className="text-muted-foreground group-hover:text-primary transition-colors" />
                    </div>
                  </button>
                </motion.div>
              ))
            )}
          </div>

          {selectMutation.isError && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm text-destructive text-center mt-4"
            >
              {selectMutation.error instanceof Error ? selectMutation.error.message : "Failed to select institution"}
            </motion.p>
          )}
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="text-center text-xs text-muted-foreground mt-6"
        >
          Don&apos;t see your institution?{" "}
          <a href="/contact" className="text-primary hover:underline">Contact support</a>
        </motion.p>
      </motion.div>
    </div>
  );
}
