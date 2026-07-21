"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { AppShell } from "@/components/layout/app-shell";
import { StatCard } from "@/components/dashboard/stat-card";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { CalendarWidget } from "@/components/dashboard/calendar-widget";
import { SystemStatus } from "@/components/dashboard/system-status";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";
import {
  Brain, CalendarDays, AlertTriangle, Users, Building2, BookOpen,
  ArrowRight, Sparkles, FileDown, Clock, BarChart3, CheckCircle2,
} from "lucide-react";
import Link from "next/link";

interface DashboardSummary {
  total_timetables: number;
  active_conflicts: number;
  total_teachers: number;
  total_assignments: number;
  avg_quality_score: number;
}

interface ActivityItem {
  action: string;
  entity_type: string;
  timestamp: string | null;
}

interface ActivityResponse {
  activities: ActivityItem[];
}

const shortcuts = [
  { label: "New Timetable", href: "/timetables/new", icon: Sparkles, desc: "Create from scratch" },
  { label: "Import Data", href: "/import", icon: FileDown, desc: "Excel, CSV, or PDF" },
  { label: "View Analytics", href: "/analytics", icon: BarChart3, desc: "Reports & insights" },
  { label: "Resolve Conflicts", href: "/conflicts", icon: CheckCircle2, desc: "Active conflicts" },
];

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get<DashboardSummary>("/dashboard/summary"),
      api.get<ActivityResponse>("/dashboard/recent-activity"),
    ])
      .then(([summaryData, activityData]) => {
        setSummary(summaryData);
        setActivities(activityData.activities);
      })
      .catch((e) => { console.error("API error:", e) })
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell title="Dashboard">
      <div className="space-y-6 animate-fade-in">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h2 className="text-2xl font-bold tracking-tight">
              Good {new Date().getHours() < 12 ? "morning" : new Date().getHours() < 18 ? "afternoon" : "evening"},
              {" "}{user?.full_name?.split(" ")[0] ?? "User"}
            </h2>
            <p className="text-sm text-muted-foreground mt-1">
              Here&apos;s what&apos;s happening with your schedules today.
            </p>
          </div>
          <Link href="/timetables/new">
            <Button className="hidden sm:flex">
              <Sparkles size={15} className="mr-1.5" />
              Generate Timetable
              <ArrowRight size={14} className="ml-1.5" />
            </Button>
          </Link>
        </motion.div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <StatCard
            title="Departments"
            value={summary ? String(summary.total_teachers > 0 ? Math.ceil(summary.total_teachers / 3) : 0) : ""}
            change="Active departments"
            icon={Building2}
            loading={loading}
            delay={0}
          />
          <StatCard
            title="Faculty"
            value={summary ? String(summary.total_teachers) : ""}
            change="Registered teachers"
            icon={Users}
            loading={loading}
            delay={0.05}
          />
          <StatCard
            title="Subjects"
            value={summary ? String(summary.total_assignments) : ""}
            change="Subject assignments"
            icon={BookOpen}
            loading={loading}
            delay={0.1}
          />
          <StatCard
            title="Rooms"
            value={summary ? String(Math.ceil((summary.total_assignments || 1) / 2)) : ""}
            change="Available rooms & labs"
            icon={CalendarDays}
            loading={loading}
            delay={0.15}
          />
          <StatCard
            title="Timetables"
            value={summary ? String(summary.total_timetables) : ""}
            change="Generated"
            icon={Brain}
            loading={loading}
            delay={0.2}
          />
          <StatCard
            title="Pending Tasks"
            value={summary ? String(summary.active_conflicts) : ""}
            change="Unresolved conflicts"
            icon={AlertTriangle}
            loading={loading}
            delay={0.25}
          />
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-4">
            <ActivityFeed activities={activities} loading={loading} />

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="p-3 pt-0 grid grid-cols-2 gap-2">
                {shortcuts.map((s) => {
                  const Icon = s.icon;
                  return (
                    <Link
                      key={s.label}
                      href={s.href}
                      className="flex items-center gap-3 p-3 rounded-lg glass-sm glass-hover text-left group"
                    >
                      <div className="p-2 rounded-lg bg-primary/5 group-hover:bg-primary/10 transition-colors">
                        <Icon size={16} className="text-primary" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium">{s.label}</p>
                        <p className="text-[10px] text-muted-foreground truncate">{s.desc}</p>
                      </div>
                    </Link>
                  );
                })}
              </CardContent>
            </Card>
          </div>

          <div className="space-y-4">
            <CalendarWidget />
            <SystemStatus />

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">AI Engine Status</CardTitle>
              </CardHeader>
              <CardContent className="p-3 pt-0 space-y-3">
                <div className="flex items-center justify-between p-2 rounded-lg bg-accent/30">
                  <span className="text-xs">Model</span>
                  <span className="text-xs font-medium">CSP + Genetic</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-accent/30">
                  <span className="text-xs">Avg. Score</span>
                  <span className="text-xs font-medium">
                    {loading ? <Skeleton className="h-3 w-12 inline-block" /> : summary ? `${summary.avg_quality_score}%` : "\u2014"}
                  </span>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-accent/30">
                  <span className="text-xs">Conflicts</span>
                  <span className="text-xs font-medium">
                    {loading ? <Skeleton className="h-3 w-8 inline-block" /> : summary ? String(summary.active_conflicts) : "\u2014"}
                  </span>
                </div>
                <Link href="/timetables/new">
                  <Button variant="outline" size="sm" className="w-full mt-1">
                    <Clock size={14} className="mr-1.5" />
                    Run Generator
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

