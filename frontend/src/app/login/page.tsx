"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { motion } from "framer-motion";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Brain, Eye, EyeOff, AlertCircle, Shield, ArrowRight } from "lucide-react";
import { loginSchema, type LoginFormData } from "@/lib/schemas";
import { login as authLogin } from "@/lib/auth";
import { useAuthStore } from "@/stores/auth-store";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/dashboard";

  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "", remember: false },
  });

  const loginMutation = useMutation({
    mutationFn: ({ email, password, remember }: LoginFormData) =>
      authLogin(email, password, remember),
    onSuccess: () => {
      const user = useAuthStore.getState().user;
      if (!user?.college_id) {
        router.push("/select-institution");
      } else {
        router.push(redirectTo);
      }
    },
  });

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="relative w-full max-w-[440px]"
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="flex justify-center mb-8"
      >
        <Link href="/" className="flex items-center gap-3 group">
          <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-primary/10 group-hover:bg-primary/15 transition-colors">
            <Brain size={32} className="text-primary" />
          </div>
          <div className="flex flex-col">
            <span className="text-2xl font-bold tracking-tight">
              <span className="gradient-text">C</span>
              <span className="text-foreground/80">hronos</span>
              <span className="gradient-text">AI</span>
            </span>
            <span className="text-xs text-muted-foreground">Enterprise Academic Platform</span>
          </div>
        </Link>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="rounded-2xl border border-border/40 bg-card/60 backdrop-blur-2xl p-8 shadow-xl shadow-black/10"
      >
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold tracking-tight">Welcome back</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Sign in to access your workspace
          </p>
        </div>

        <form onSubmit={handleSubmit((data) => loginMutation.mutate(data))} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">Email</label>
            <Input
              id="email"
              type="email"
              placeholder="name@institution.edu"
              {...register("email")}
              disabled={loginMutation.isPending}
              autoComplete="email"
              autoFocus
              className="h-11"
            />
            {errors.email && (
              <p className="text-xs text-destructive flex items-center gap-1 mt-1">
                <AlertCircle size={10} />
                {errors.email.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label htmlFor="password" className="text-sm font-medium">Password</label>
              <Link href="/forgot-password" className="text-xs text-muted-foreground hover:text-primary transition-colors">
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                {...register("password")}
                disabled={loginMutation.isPending}
                autoComplete="current-password"
                className="h-11 pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.password && (
              <p className="text-xs text-destructive flex items-center gap-1 mt-1">
                <AlertCircle size={10} />
                {errors.password.message}
              </p>
            )}
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="remember"
              {...register("remember")}
              className="rounded border-border bg-transparent accent-primary"
            />
            <label htmlFor="remember" className="text-sm text-muted-foreground cursor-pointer select-none">
              Remember me
            </label>
          </div>

          {loginMutation.isError && (
            <motion.div
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 text-sm text-destructive bg-destructive/10 p-3 rounded-lg"
            >
              <AlertCircle size={14} className="shrink-0" />
              <span>{loginMutation.error instanceof Error
                ? loginMutation.error.message.includes("429") || loginMutation.error.message.includes("Too many")
                  ? "Too many login attempts. Please wait before trying again."
                  : loginMutation.error.message
                : "Login failed"}</span>
            </motion.div>
          )}

          <Button className="w-full h-11 text-base" type="submit" disabled={loginMutation.isPending}>
            {loginMutation.isPending ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 rounded-full border-2 border-background/30 border-t-background animate-spin" />
                Signing in...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                Sign In <ArrowRight size={16} />
              </span>
            )}
          </Button>
        </form>

        <div className="mt-6">
          <Separator />
          <div className="mt-4 flex items-center justify-center gap-2 text-xs text-muted-foreground">
            <Shield size={12} />
            <span>Enterprise-grade security • End-to-end encrypted</span>
          </div>
        </div>
      </motion.div>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="text-center text-xs text-muted-foreground mt-6"
      >
        Don&apos;t have an account?{" "}
        <Link href="/" className="text-primary hover:underline">Learn more</Link>
      </motion.p>
    </motion.div>
  );
}

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background overflow-hidden p-4">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/8 via-transparent to-info/8 pointer-events-none" />
      <div className="absolute top-1/3 left-1/4 w-[500px] h-[500px] rounded-full bg-primary/3 blur-[150px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full bg-info/3 blur-[120px] pointer-events-none" />
      <Suspense fallback={<div className="w-full max-w-[440px]"><div className="h-[500px] rounded-2xl bg-card/30 animate-pulse" /></div>}>
        <LoginForm />
      </Suspense>
    </div>
  );
}
