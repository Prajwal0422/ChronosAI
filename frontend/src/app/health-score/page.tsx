"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { api } from "@/lib/api-client";
import { RequirePermission } from "@/components/auth/require-permission";
import { Activity, TrendingUp, TrendingDown, Minus, Sparkles, AlertTriangle, CheckCircle, Info } from "lucide-react";
import { Timetable } from "@/types";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const gradeColor: Record<string, string> = {
  "A+": "text-green-400", "A": "text-green-300", "B+": "text-blue-400",
  "B": "text-blue-300", "C+": "text-yellow-400", "C": "text-yellow-300",
  "D": "text-orange-400", "F": "text-red-400",
};

export default function HealthScorePage() {
  const [timetables, setTimetables] = useState<Timetable[]>([]);
  const [selectedTT, setSelectedTT] = useState("");
  const [score, setScore] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [loadingTT, setLoadingTT] = useState(true);

  useEffect(() => {
    api.get<{ items: Timetable[]; total: number }>("/timetables")
      .then((d) => setTimetables(d.items))
      .catch((e) => { console.error("API error:", e) })
      .finally(() => setLoadingTT(false));
  }, []);

  const fetchScore = async () => {
    if (!selectedTT) return;
    setLoading(true);
    try {
      const data = await api.get(`/health-score/${selectedTT}`);
      setScore(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <RequirePermission permission="view:analytics">
      <AppShell title="Timetable Health Score">
        <div className="space-y-6 animate-fade-in">
          <Card className="bg-gradient-to-br from-primary/5 via-primary/0 to-info/5 border-primary/10">
            <CardContent className="flex items-center gap-4 p-6">
              <div className="p-3 rounded-xl bg-primary/10"><Activity size={28} className="text-primary" /></div>
              <div>
                <h2 className="text-lg font-semibold">Timetable Health Score</h2>
                <p className="text-sm text-muted-foreground">Multi-metric scoring with letter grade and improvement suggestions</p>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="text-xs font-medium text-muted-foreground mb-1 block">Select Timetable</label>
              <select className="w-full h-9 rounded-lg border border-border bg-background px-3 text-sm"
                value={selectedTT} onChange={(e) => setSelectedTT(e.target.value)}>
                <option value="">-- Select --</option>
                {timetables.map((t) => (
                  <option key={t.id} value={t.id}>{t.name} (v{t.version})</option>
                ))}
              </select>
            </div>
            <Button onClick={fetchScore} disabled={!selectedTT || loading}>
              <Activity size={16} className="mr-1" /> {loading ? "Scoring..." : "Score"}
            </Button>
          </div>

          {loading && <Skeleton className="h-64 w-full" />}

          {score && !loading && (
            <>
              <div className="grid gap-4 md:grid-cols-3">
                <Card className="md:col-span-1">
                  <CardContent className="p-6 flex flex-col items-center justify-center h-full">
                    <div className={`text-5xl font-bold mb-2 ${gradeColor[score.grade] || "text-muted-foreground"}`}>
                      {score.grade}
                    </div>
                    <div className="text-3xl font-light mb-1">{score.overall_score}</div>
                    <p className="text-xs text-muted-foreground">out of 100</p>
                    <Badge variant="outline" className="mt-3 text-xs">{score.entry_count} entries</Badge>
                  </CardContent>
                </Card>
                <Card className="md:col-span-2">
                  <CardHeader><CardTitle className="text-sm">Metric Breakdown</CardTitle></CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={Object.entries(score.metrics || {}).map(([k, v]) => ({ metric: k.replace(/_/g, ' '), value: v }))} layout="vertical" margin={{ left: 100 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                        <XAxis type="number" domain={[0, 100]} />
                        <YAxis type="category" dataKey="metric" tick={{ fontSize: 10 }} width={110} />
                        <Tooltip contentStyle={{ background: "rgba(0,0,0,0.8)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8 }} />
                        <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>

              {score.improvement_suggestions && score.improvement_suggestions.length > 0 && (
                <Card>
                  <CardHeader><CardTitle className="text-sm flex items-center gap-2"><Sparkles size={16} /> Improvement Suggestions</CardTitle></CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {score.improvement_suggestions.map((s: string, i: number) => (
                        <li key={i} className="flex items-start gap-2 text-sm">
                          <Info size={14} className="mt-0.5 shrink-0 text-primary" />
                          <span className="text-muted-foreground">{s}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </>
          )}

          {!loading && !score && !loadingTT && (
            <Card><CardContent className="p-12 text-center text-muted-foreground">
              <Activity size={40} className="mx-auto mb-3 opacity-30" />
              <p>Select a timetable to score its health.</p>
            </CardContent></Card>
          )}
        </div>
      </AppShell>
    </RequirePermission>
  );
}

