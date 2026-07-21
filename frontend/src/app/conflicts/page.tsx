"use client";

import { AppShell } from "@/components/layout/app-shell";
import { DataTable, Column } from "@/components/ui/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useCrud } from "@/hooks/use-crud";
import { RequirePermission } from "@/components/auth/require-permission";
import { ConflictRecord } from "@/types";
import { CheckCircle2, AlertTriangle, XCircle, Info } from "lucide-react";

const columns: Column<ConflictRecord>[] = [
  { key: "conflict_type", label: "Type", sortable: true, render: (c) => <Badge variant="outline">{c.conflict_type}</Badge> },
  { key: "severity", label: "Severity", sortable: true, render: (c) => <Badge variant={c.severity === "critical" ? "destructive" : c.severity === "warning" ? "warning" : "outline"}>{c.severity}</Badge> },
  { key: "description", label: "Description" },
  { key: "resolved", label: "Status", sortable: true, render: (c) => c.resolved ? <Badge variant="outline" className="text-success"><CheckCircle2 size={12} className="mr-1" /> Resolved</Badge> : <Badge variant="secondary"><AlertTriangle size={12} className="mr-1" /> Open</Badge> },
];

export default function ConflictsPage() {
  const crud = useCrud<ConflictRecord>({ endpoint: "/conflicts" });

  const summaryCards = [
    { label: "Total Conflicts", value: crud.total, icon: AlertTriangle, color: "text-warning" },
    { label: "Critical", value: "3", icon: XCircle, color: "text-destructive" },
    { label: "Warning", value: "4", icon: Info, color: "text-info" },
    { label: "Resolved", value: "12", icon: CheckCircle2, color: "text-success" },
  ];

  return (
    <RequirePermission permission="manage:timetables">
      <AppShell title="Conflict Detection">
        <div className="space-y-6 animate-fade-in">
          <div className="grid gap-4 grid-cols-4">
            {summaryCards.map((card) => {
              const Icon = card.icon;
              return (
                <Card key={card.label}>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">{card.label}</CardTitle>
                    <Icon size={18} className={card.color} />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{card.value}</div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <div className="flex gap-2">
            <Button size="sm"><AlertTriangle size={16} className="mr-1" /> Auto-Validate</Button>
            <Button variant="outline" size="sm"><CheckCircle2 size={16} className="mr-1" /> Resolve All</Button>
          </div>

          <DataTable title="Conflict Records" columns={columns} data={crud.data} loading={crud.loading} total={crud.total} onSearch={crud.handleSearch} onPageChange={crud.handlePageChange} page={crud.page} />
        </div>
      </AppShell>
    </RequirePermission>
  );
}
