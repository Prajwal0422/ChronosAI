"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { DataTable, Column } from "@/components/ui/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useCrud } from "@/hooks/use-crud";
import { RequirePermission } from "@/components/auth/require-permission";
import { Timetable } from "@/types";
import { Brain, Download, Play, Sparkles } from "lucide-react";

const statusVariant: Record<string, "outline" | "secondary" | "success" | "default"> = {
  draft: "secondary",
  generated: "outline",
  published: "success",
  archived: "default",
};

const columns: Column<Timetable>[] = [
  { key: "name", label: "Name", sortable: true },
  { key: "version", label: "Version", sortable: true },
  { key: "status", label: "Status", sortable: true, render: (t) => <Badge variant={statusVariant[t.status] || "outline"}>{t.status}</Badge> },
  { key: "quality_score", label: "Score", sortable: true, render: (t) => t.quality_score !== null ? `${t.quality_score}%` : "-" },
  { key: "section_id", label: "Section ID" },
];

export default function TimetablesPage() {
  const crud = useCrud<Timetable>({ endpoint: "/timetables" });
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await new Promise((r) => setTimeout(r, 2000));
      await crud.fetch();
    } finally {
      setGenerating(false);
    }
  };

  return (
    <RequirePermission permission="manage:timetables">
      <AppShell title="AI Timetable Generator">
        <div className="space-y-6 animate-fade-in">
          <Card className="bg-gradient-to-br from-primary/5 via-primary/0 to-info/5 border-primary/10">
            <CardContent className="flex items-center justify-between p-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-primary/10">
                  <Brain size={32} className="text-primary" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold">AI-Powered Generation</h2>
                  <p className="text-sm text-muted-foreground">CSP backtracking with MRV heuristic + scoring</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button size="lg" onClick={handleGenerate} disabled={generating}>
                  <Sparkles size={18} className="mr-2" />
                  {generating ? "Generating..." : "Generate Now"}
                </Button>
                <Button variant="outline" size="lg">
                  <Play size={18} className="mr-2" /> Preview
                </Button>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-2">
            <Button variant="outline" size="sm"><Download size={16} className="mr-1" /> Export</Button>
            <Button variant="outline" size="sm">Schedule Gen</Button>
          </div>

          <DataTable title="Generated Timetables" columns={columns} data={crud.data} loading={crud.loading} total={crud.total} onSearch={crud.handleSearch} onPageChange={crud.handlePageChange} page={crud.page} />
        </div>
      </AppShell>
    </RequirePermission>
  );
}
