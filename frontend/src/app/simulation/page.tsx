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
import { GitCompareArrows, Play, AlertTriangle, CheckCircle, FlaskConical, UserX, CalendarX, Plus, Building2 } from "lucide-react";
import { Timetable, Simulation, Teacher, Classroom, Laboratory } from "@/types";
import toast from "react-hot-toast";

const simTypeMeta: Record<string, { label: string; icon: React.ReactNode }> = {
  teacher_unavailable: { label: "Teacher Unavailable", icon: <UserX size={16} /> },
  new_classroom: { label: "New Classroom Added", icon: <Building2 size={16} /> },
  holiday_declared: { label: "Holiday Declared", icon: <CalendarX size={16} /> },
  additional_section: { label: "Additional Section", icon: <Plus size={16} /> },
  faculty_resigned: { label: "Faculty Resigned", icon: <UserX size={16} /> },
  laboratory_unavailable: { label: "Lab Unavailable", icon: <FlaskConical size={16} /> },
};

export default function SimulationPage() {
  const [timetables, setTimetables] = useState<Timetable[]>([]);
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [labs, setLabs] = useState<Laboratory[]>([]);
  const [selectedTT, setSelectedTT] = useState("");
  const [simType, setSimType] = useState("teacher_unavailable");
  const [simName, setSimName] = useState("");
  const [teacherId, setTeacherId] = useState("");
  const [labId, setLabId] = useState("");
  const [holidayDay, setHolidayDay] = useState("");
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get<{ items: Timetable[]; total: number }>("/timetables"),
      api.get<{ items: Teacher[]; total: number }>("/teachers"),
      api.get<{ items: Laboratory[]; total: number }>("/laboratories"),
      api.get<{ items: Simulation[]; total: number }>("/simulation"),
    ]).then(([tt, tch, lb, sim]) => {
      setTimetables(tt.items);
      setTeachers(tch.items);
      setLabs(lb.items);
      setSimulations(sim.items);
    }).catch((e) => { console.error("API error:", e) }).finally(() => setLoading(false));
  }, []);

  const runSimulation = async () => {
    if (!selectedTT || !simName) return toast.error("Select timetable and name the simulation");
    setRunning(true);
    try {
      const params: Record<string, any> = { timetable_id: selectedTT, simulation_type: simType, name: simName };
      if (simType === "teacher_unavailable" || simType === "faculty_resigned") params.teacher_id = teacherId;
      if (simType === "laboratory_unavailable") params.laboratory_id = labId;
      if (simType === "holiday_declared") params.holiday_date = holidayDay;
      const result = await api.post<Simulation>("/simulation", undefined, params as Record<string, string | number | boolean | undefined | null>);
      setSimulations((prev) => [result, ...prev]);
      setSimName("");
      toast.success("Simulation complete");
    } catch (e: any) {
      toast.error(e.message || "Simulation failed");
    } finally {
      setRunning(false);
    }
  };

  const applySimulation = async (simId: string) => {
    try {
      const result = await api.post<{ message: string }>(`/simulation/${simId}/apply`);
      toast.success(result.message || "Applied");
      const data = await api.get<{ items: Simulation[]; total: number }>("/simulation");
      setSimulations(data.items);
    } catch (e: any) {
      toast.error(e.message || "Failed to apply");
    }
  };

  return (
    <RequirePermission permission="manage:timetables">
      <AppShell title="What-If Simulation">
        <div className="space-y-6 animate-fade-in">
          <Card className="bg-gradient-to-br from-primary/5 via-primary/0 to-info/5 border-primary/10">
            <CardContent className="flex items-center gap-4 p-6">
              <div className="p-3 rounded-xl bg-primary/10"><GitCompareArrows size={28} className="text-primary" /></div>
              <div>
                <h2 className="text-lg font-semibold">Schedule Simulation Engine</h2>
                <p className="text-sm text-muted-foreground">Simulate changes and preview impact before applying</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="text-sm">Run Simulation</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1 block">Timetable</label>
                  <select className="w-full h-9 rounded-lg border border-border bg-background px-3 text-sm"
                    value={selectedTT} onChange={(e) => setSelectedTT(e.target.value)}>
                    <option value="">-- Select --</option>
                    {timetables.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1 block">Simulation Name</label>
                  <Input value={simName} onChange={(e) => setSimName(e.target.value)} placeholder="e.g., Remove Dr. Smith" />
                </div>
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1 block">Type</label>
                  <select className="w-full h-9 rounded-lg border border-border bg-background px-3 text-sm"
                    value={simType} onChange={(e) => setSimType(e.target.value)}>
                    {Object.entries(simTypeMeta).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
                  </select>
                </div>
                {(simType === "teacher_unavailable" || simType === "faculty_resigned") && (
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-1 block">Teacher</label>
                    <select className="w-full h-9 rounded-lg border border-border bg-background px-3 text-sm"
                      value={teacherId} onChange={(e) => setTeacherId(e.target.value)}>
                      <option value="">-- Select --</option>
                      {teachers.map((t) => <option key={t.id} value={t.id}>{t.full_name}</option>)}
                    </select>
                  </div>
                )}
                {simType === "laboratory_unavailable" && (
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-1 block">Laboratory</label>
                    <select className="w-full h-9 rounded-lg border border-border bg-background px-3 text-sm"
                      value={labId} onChange={(e) => setLabId(e.target.value)}>
                      <option value="">-- Select --</option>
                      {labs.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
                    </select>
                  </div>
                )}
                {simType === "holiday_declared" && (
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-1 block">Day of Week</label>
                    <select className="w-full h-9 rounded-lg border border-border bg-background px-3 text-sm"
                      value={holidayDay} onChange={(e) => setHolidayDay(e.target.value)}>
                      <option value="">-- Select --</option>
                      {["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"].map((d) => <option key={d} value={d}>{d}</option>)}
                    </select>
                  </div>
                )}
              </div>
              <Button onClick={runSimulation} disabled={running || !selectedTT}>
                <Play size={16} className="mr-1" /> {running ? "Running..." : "Run Simulation"}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="text-sm">Simulation History</CardTitle></CardHeader>
            <CardContent>
              {loading ? <Skeleton className="h-32 w-full" /> : simulations.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-8">No simulations yet</p>
              ) : (
                <div className="space-y-3">
                  {simulations.map((sim) => (
                    <div key={sim.id} className="flex items-center justify-between p-3 rounded-lg border border-border/50 bg-muted/20">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="p-2 rounded-lg bg-primary/10 shrink-0">
                          {simTypeMeta[sim.simulation_type]?.icon || <GitCompareArrows size={16} className="text-primary" />}
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium">{sim.name}</p>
                          <p className="text-xs text-muted-foreground">
                            Score: {sim.original_score} → {sim.simulated_score}
                            {sim.applied && " (Applied)"}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <Badge variant={sim.applied ? "success" : "outline"}>{sim.applied ? "Applied" : "Draft"}</Badge>
                        {!sim.applied && (
                          <Button size="sm" variant="outline" onClick={() => applySimulation(sim.id)}>
                            <CheckCircle size={14} className="mr-1" /> Apply
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </AppShell>
    </RequirePermission>
  );
}

