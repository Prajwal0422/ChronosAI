"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api-client";
import { RequirePermission } from "@/components/auth/require-permission";
import { Lightbulb, AlertTriangle, Info, AlertCircle, Sparkles } from "lucide-react";
import { Timetable } from "@/types";

const severityIcon: Record<string, React.ReactNode> = {
  high: <AlertCircle size={16} className="text-destructive" />,
  medium: <AlertTriangle size={16} className="text-warning" />,
  low: <Info size={16} className="text-info" />,
};
const severityVariant: Record<string, "destructive" | "warning" | "info"> = {
  high: "destructive", medium: "warning", low: "info",
};

export default function InsightsPage() {
  const [timetables, setTimetables] = useState<Timetable[]>([]);
  const [selectedTT, setSelectedTT] = useState("");
  const [insights, setInsights] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [loadingTT, setLoadingTT] = useState(true);

  useEffect(() => {
    api.get<{ items: Timetable[]; total: number }>("/timetables")
      .then((d) => setTimetables(d.items))
      .catch((e) => { console.error("API error:", e) })
      .finally(() => setLoadingTT(false));
  }, []);

  const fetchInsights = async () => {
    if (!selectedTT) return;
    setLoading(true);
    try {
      const data = await api.get(`/insights/${selectedTT}`);
      setInsights(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <RequirePermission permission="view:analytics">
      <AppShell title="AI Insights">
        <div className="space-y-6 animate-fade-in">
          <Card className="bg-gradient-to-br from-primary/5 via-primary/0 to-info/5 border-primary/10">
            <CardContent className="flex items-center gap-4 p-6">
              <div className="p-3 rounded-xl bg-primary/10">
                <Lightbulb size={28} className="text-primary" />
              </div>
              <div className="flex-1">
                <h2 className="text-lg font-semibold">AI-Powered Timetable Insights</h2>
                <p className="text-sm text-muted-foreground">Automated analysis of workload, utilization, distribution, and conflicts</p>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="text-xs font-medium text-muted-foreground mb-1 block">Select Timetable</label>
              <select
                className="w-full h-9 rounded-lg border border-border bg-background px-3 text-sm"
                value={selectedTT}
                onChange={(e) => setSelectedTT(e.target.value)}
              >
                <option value="">-- Select --</option>
                {timetables.map((t) => (
                  <option key={t.id} value={t.id}>{t.name} (v{t.version})</option>
                ))}
              </select>
            </div>
            <Button onClick={fetchInsights} disabled={!selectedTT || loading}>
              <Sparkles size={16} className="mr-1" /> {loading ? "Analyzing..." : "Analyze"}
            </Button>
          </div>

          {loading && Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-24 w-full" />)}

          {insights && !loading && (
            <>
              {insights.summary && (
                <Card className="bg-muted/30">
                  <CardContent className="p-4 text-sm text-muted-foreground">{insights.summary}</CardContent>
                </Card>
              )}

              <div className="grid gap-3">
                {(insights.insights || []).map((insight: any, i: number) => (
                  <Card key={i}>
                    <CardContent className="p-4 flex gap-3">
                      <div className="mt-0.5">{severityIcon[insight.severity] || <Info size={16} />}</div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-sm font-semibold">{insight.title}</h3>
                          <Badge variant={severityVariant[insight.severity] || "outline"} className="text-[10px]">{insight.severity}</Badge>
                        </div>
                        <p className="text-xs text-muted-foreground mb-2">{insight.description}</p>
                        <div className="flex items-start gap-1.5 text-xs text-primary">
                          <Sparkles size={12} className="mt-0.5 shrink-0" />
                          <span>{insight.suggestion}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {(!insights.insights || insights.insights.length === 0) && (
                <Card>
                  <CardContent className="p-12 text-center text-muted-foreground">
                    <Lightbulb size={32} className="mx-auto mb-2 opacity-50" />
                    <p>No insights found for this timetable.</p>
                  </CardContent>
                </Card>
              )}
            </>
          )}

          {!loading && !insights && !loadingTT && (
            <Card>
              <CardContent className="p-12 text-center text-muted-foreground">
                <Lightbulb size={40} className="mx-auto mb-3 opacity-30" />
                <p>Select a timetable and click "Analyze" to generate AI insights.</p>
              </CardContent>
            </Card>
          )}
        </div>
      </AppShell>
    </RequirePermission>
  );
}

