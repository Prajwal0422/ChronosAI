"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { api } from "@/lib/api-client";
import { RequirePermission } from "@/components/auth/require-permission";
import {
  Brain, Clock, Users, CalendarDays, TrendingUp, TrendingDown,
  BarChart3, Building2, Monitor, FlaskConical, GraduationCap,
} from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend,
} from "recharts";

const COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#ec4899"];

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<any>(null);
  const [facultyWorkload, setFacultyWorkload] = useState<any[]>([]);
  const [dailyOccupancy, setDailyOccupancy] = useState<any[]>([]);
  const [resourceUsage, setResourceUsage] = useState<any>(null);
  const [roomUtil, setRoomUtil] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"overview" | "faculty" | "rooms" | "daily">("overview");

  useEffect(() => {
    Promise.all([
      api.get("/analytics/overview"),
      api.get("/analytics/faculty-workload"),
      api.get("/analytics/daily-occupancy"),
      api.get("/analytics/resource-usage"),
      api.get("/analytics/room-utilization"),
    ]).then(([ov, fw, doc, ru, rutil]) => {
      setOverview(ov);
      setFacultyWorkload((fw as any).items || []);
      setDailyOccupancy((doc as any).items || []);
      setResourceUsage(ru);
      setRoomUtil((rutil as any).items || []);
    }).catch((e) => { console.error("API error:", e) }).finally(() => setLoading(false));
  }, []);

  return (
    <RequirePermission permission="view:analytics">
      <AppShell title="Analytics Dashboard">
        <div className="space-y-6 animate-fade-in">
          <div className="flex gap-2 flex-wrap">
            {(["overview", "faculty", "rooms", "daily"] as const).map((t) => (
              <Button key={t} variant={tab === t ? "default" : "outline"} size="sm" onClick={() => setTab(t)}>
                {t === "overview" && <BarChart3 size={14} className="mr-1" />}
                {t === "faculty" && <GraduationCap size={14} className="mr-1" />}
                {t === "rooms" && <Monitor size={14} className="mr-1" />}
                {t === "daily" && <CalendarDays size={14} className="mr-1" />}
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </Button>
            ))}
          </div>

          {tab === "overview" && (
            <>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {loading ? Array.from({ length: 4 }).map((_, i) => (
                  <Card key={i}><CardHeader className="pb-2"><Skeleton className="h-4 w-24" /></CardHeader><CardContent><Skeleton className="h-8 w-16" /></CardContent></Card>
                )) : overview && [
                  { label: "Avg Quality Score", value: `${overview.average_quality_score}%`, icon: Brain, change: `${overview.published_timetables} published` },
                  { label: "Timetables", value: String(overview.total_timetables), icon: CalendarDays, change: `${overview.total_entries} entries` },
                  { label: "Conflicts", value: String(overview.total_conflicts), icon: Clock, change: `${overview.conflict_resolution_rate}% resolved` },
                  { label: "Teachers", value: String(overview.total_teachers), icon: Users, change: "active faculty" },
                ].map((s) => {
                  const Icon = s.icon;
                  return (
                    <Card key={s.label}>
                      <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">{s.label}</CardTitle>
                        <Icon size={18} className="text-primary" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{s.value}</div>
                        <p className="text-xs text-muted-foreground mt-1">{s.change}</p>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {resourceUsage && (
                <div className="grid gap-4 md:grid-cols-3">
                  <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Room Usage</CardTitle></CardHeader>
                    <CardContent><div className="text-2xl font-bold">{resourceUsage.room_usage_pct}%</div>
                      <p className="text-xs text-muted-foreground">{resourceUsage.rooms_used}/{resourceUsage.total_rooms} rooms used</p></CardContent></Card>
                  <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Lab Usage</CardTitle></CardHeader>
                    <CardContent><div className="text-2xl font-bold">{resourceUsage.lab_usage_pct}%</div>
                      <p className="text-xs text-muted-foreground">{resourceUsage.labs_used}/{resourceUsage.total_labs} labs used</p></CardContent></Card>
                  <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Overall Usage</CardTitle></CardHeader>
                    <CardContent><div className="text-2xl font-bold">{resourceUsage.overall_usage_pct}%</div>
                      <p className="text-xs text-muted-foreground">Resource utilization rate</p></CardContent></Card>
                </div>
              )}
            </>
          )}

          {tab === "faculty" && (
            <Card>
              <CardHeader><CardTitle>Faculty Workload Distribution</CardTitle></CardHeader>
              <CardContent>
                {loading ? <Skeleton className="h-64 w-full" /> : (
                  <ResponsiveContainer width="100%" height={350}>
                    <BarChart data={facultyWorkload.slice(0, 15)} margin={{ bottom: 60 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="full_name" angle={-45} textAnchor="end" tick={{ fontSize: 10 }} height={80} />
                      <YAxis />
                      <Tooltip contentStyle={{ background: "rgba(0,0,0,0.8)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8 }} />
                      <Bar dataKey="total_entries" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Entries" />
                      <Bar dataKey="utilization_pct" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Utilization %" />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          )}

          {tab === "rooms" && (
            <Card>
              <CardHeader><CardTitle>Room & Lab Utilization</CardTitle></CardHeader>
              <CardContent>
                {loading ? <Skeleton className="h-64 w-full" /> : (
                  <ResponsiveContainer width="100%" height={350}>
                    <BarChart data={roomUtil.slice(0, 15)} layout="vertical" margin={{ left: 80 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis type="number" />
                      <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={100} />
                      <Tooltip contentStyle={{ background: "rgba(0,0,0,0.8)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8 }} />
                      <Bar dataKey="usage_count" fill="#10b981" radius={[0, 4, 4, 0]} name="Usage Count" />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          )}

          {tab === "daily" && (
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader><CardTitle>Daily Occupancy</CardTitle></CardHeader>
                <CardContent>
                  {loading ? <Skeleton className="h-64 w-full" /> : (
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie data={dailyOccupancy} dataKey="count" nameKey="day" cx="50%" cy="50%" outerRadius={100} label={({ day, count }) => `${day.slice(0, 3)}: ${count}`}>
                          {dailyOccupancy.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                        </Pie>
                        <Tooltip contentStyle={{ background: "rgba(0,0,0,0.8)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8 }} />
                      </PieChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardHeader><CardTitle>Day-wise Trend</CardTitle></CardHeader>
                <CardContent>
                  {loading ? <Skeleton className="h-64 w-full" /> : (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={dailyOccupancy}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                        <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                        <YAxis />
                        <Tooltip contentStyle={{ background: "rgba(0,0,0,0.8)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8 }} />
                        <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} dot={{ fill: "#3b82f6" }} />
                      </LineChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </AppShell>
    </RequirePermission>
  );
}

