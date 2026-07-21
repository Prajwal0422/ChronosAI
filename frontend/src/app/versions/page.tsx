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
import { History, RotateCcw, GitCompare, Plus, Download } from "lucide-react";
import { Timetable, VersionSnapshot } from "@/types";
import toast from "react-hot-toast";

export default function VersionsPage() {
  const [timetables, setTimetables] = useState<Timetable[]>([]);
  const [versions, setVersions] = useState<VersionSnapshot[]>([]);
  const [selectedTT, setSelectedTT] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [restoring, setRestoring] = useState<string | null>(null);
  const [compareA, setCompareA] = useState("");
  const [compareB, setCompareB] = useState("");
  const [comparison, setComparison] = useState<any>(null);

  useEffect(() => {
    Promise.all([
      api.get<{ items: Timetable[]; total: number }>("/timetables"),
      api.get<{ items: VersionSnapshot[]; total: number }>("/versions"),
    ]).then(([tt, v]) => {
      setTimetables(tt.items);
      setVersions(v.items);
    }).catch((e) => { console.error("API error:", e) }).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedTT) {
      api.get<{ items: VersionSnapshot[]; total: number }>("/versions", { timetable_id: selectedTT })
        .then((d) => setVersions(d.items))
        .catch((e) => { console.error("API error:", e) });
    }
  }, [selectedTT]);

  const saveSnapshot = async () => {
    if (!selectedTT) return toast.error("Select a timetable");
    setSaving(true);
    try {
      const result = await api.post<VersionSnapshot>("/versions", undefined, { timetable_id: selectedTT });
      setVersions((prev) => [result, ...prev]);
      toast.success("Snapshot saved");
    } catch (e: any) {
      toast.error(e.message || "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const restoreVersion = async (verId: string) => {
    setRestoring(verId);
    try {
      const result = await api.post<{ message: string }>(`/versions/${verId}/restore`);
      toast.success(result.message || "Restored");
    } catch (e: any) {
      toast.error(e.message || "Restore failed");
    } finally {
      setRestoring(null);
    }
  };

  const compareVersions = async () => {
    if (!compareA || !compareB) return toast.error("Select two versions");
    try {
      const result = await api.post<{ added: number; removed: number; common: number; score_diff: number; added_items: any[]; removed_items: any[] }>(
        "/versions/compare", undefined, { version_id_1: compareA, version_id_2: compareB }
      );
      setComparison(result);
    } catch (e: any) {
      toast.error(e.message || "Compare failed");
    }
  };

  return (
    <RequirePermission permission="manage:timetables">
      <AppShell title="Version History">
        <div className="space-y-6 animate-fade-in">
          <Card className="bg-gradient-to-br from-primary/5 via-primary/0 to-info/5 border-primary/10">
            <CardContent className="flex items-center gap-4 p-6">
              <div className="p-3 rounded-xl bg-primary/10"><History size={28} className="text-primary" /></div>
              <div>
                <h2 className="text-lg font-semibold">Timetable Version History</h2>
                <p className="text-sm text-muted-foreground">Save snapshots, restore previous versions, and compare changes</p>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="text-xs font-medium text-muted-foreground mb-1 block">Timetable</label>
              <select className="w-full h-9 rounded-lg border border-border bg-background px-3 text-sm"
                value={selectedTT} onChange={(e) => setSelectedTT(e.target.value)}>
                <option value="">All Timetables</option>
                {timetables.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>
            <Button onClick={saveSnapshot} disabled={!selectedTT || saving}><Plus size={16} className="mr-1" /> {saving ? "Saving..." : "Save Snapshot"}</Button>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader><CardTitle className="text-sm">Versions</CardTitle></CardHeader>
              <CardContent>
                {loading ? <Skeleton className="h-32 w-full" /> : versions.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-8">No versions saved</p>
                ) : (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {versions.map((v) => (
                      <div key={v.id} className="flex items-center justify-between p-2.5 rounded-lg border border-border/50 bg-muted/20">
                        <div>
                          <p className="text-sm font-medium">v{v.version_number} {v.label && `- ${v.label}`}</p>
                          <p className="text-xs text-muted-foreground">Score: {v.quality_score ?? "N/A"} · {v.entry_count} entries{v.is_restored ? " (restored)" : ""}</p>
                        </div>
                        <div className="flex gap-1">
                          <Button size="sm" variant="ghost" onClick={() => restoreVersion(v.id)} disabled={restoring === v.id}>
                            <RotateCcw size={14} />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle className="text-sm">Compare Versions</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1 block">Version A</label>
                  <select className="w-full h-9 rounded-lg border border-border bg-background px-3 text-sm"
                    value={compareA} onChange={(e) => setCompareA(e.target.value)}>
                    <option value="">-- Select --</option>
                    {versions.map((v) => <option key={v.id} value={v.id}>v{v.version_number} {v.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1 block">Version B</label>
                  <select className="w-full h-9 rounded-lg border border-border bg-background px-3 text-sm"
                    value={compareB} onChange={(e) => setCompareB(e.target.value)}>
                    <option value="">-- Select --</option>
                    {versions.map((v) => <option key={v.id} value={v.id}>v{v.version_number} {v.label}</option>)}
                  </select>
                </div>
                <Button onClick={compareVersions} disabled={!compareA || !compareB}><GitCompare size={16} className="mr-1" /> Compare</Button>

                {comparison && (
                  <div className="p-3 rounded-lg border border-border/50 bg-muted/20 space-y-1 mt-2">
                    <p className="text-xs text-muted-foreground">{comparison.change_summary}</p>
                    <div className="flex gap-4 text-xs">
                      <span>Added: <strong className="text-green-400">{comparison.added}</strong></span>
                      <span>Removed: <strong className="text-red-400">{comparison.removed}</strong></span>
                      <span>Score: {comparison.score_change > 0 ? "+" : ""}{comparison.score_change}</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </AppShell>
    </RequirePermission>
  );
}

