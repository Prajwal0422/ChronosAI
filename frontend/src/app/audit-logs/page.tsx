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
import { ClipboardList, Search, Filter } from "lucide-react";
import { AuditLog } from "@/types";

const actionColors: Record<string, "info" | "success" | "destructive" | "warning" | "outline" | "secondary"> = {
  login: "info", create: "success", update: "warning", delete: "destructive",
  generate: "info", export: "outline", import: "outline", publish: "success",
  archive: "secondary", approve: "success",
};

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState("");
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = { offset: page * 50, limit: 50 };
      if (actionFilter) params.action = actionFilter;
      const data = await api.get<{ items: AuditLog[]; total: number }>("/audit-logs", params);
      setLogs(data.items);
      setTotal(data.total);
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  };

  useEffect(() => { fetchLogs() }, [page, actionFilter]);

  return (
    <RequirePermission permission="view:audit_logs">
      <AppShell title="Audit Logs">
        <div className="space-y-6 animate-fade-in">
          <Card className="bg-gradient-to-br from-primary/5 via-primary/0 to-info/5 border-primary/10">
            <CardContent className="flex items-center gap-4 p-6">
              <div className="p-3 rounded-xl bg-primary/10"><ClipboardList size={28} className="text-primary" /></div>
              <div>
                <h2 className="text-lg font-semibold">Audit Logs</h2>
                <p className="text-sm text-muted-foreground">Complete event history for all actions across the platform</p>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-2 flex-wrap items-center">
            <Filter size={14} className="text-muted-foreground" />
            {["", "login", "create", "update", "delete", "generate", "export", "import", "publish", "approve"].map((a) => (
              <Button key={a} variant={actionFilter === a ? "default" : "outline"} size="sm" onClick={() => { setActionFilter(a); setPage(0) }}>
                {a || "All"}
              </Button>
            ))}
          </div>

          <Card>
            <CardContent className="p-0">
              {loading ? (
                <div className="p-6 space-y-3">{Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}</div>
              ) : logs.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-12">No audit logs found</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left text-xs font-medium text-muted-foreground p-3">Action</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-3">Entity</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-3">User</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-3">Timestamp</th>
                        <th className="text-left text-xs font-medium text-muted-foreground p-3">Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      {logs.map((log) => (
                        <tr key={log.id} className="border-b border-border/50 last:border-0 hover:bg-muted/20">
                          <td className="p-3"><Badge variant={actionColors[log.action] || "outline"} className="text-[10px]">{log.action}</Badge></td>
                          <td className="p-3 text-sm">{log.entity_type}</td>
                          <td className="p-3 text-xs text-muted-foreground">{log.user_id ? log.user_id.slice(0, 8) + "..." : "System"}</td>
                          <td className="p-3 text-xs text-muted-foreground">{log.timestamp ? new Date(log.timestamp).toLocaleString() : ""}</td>
                          <td className="p-3 text-xs text-muted-foreground max-w-[200px] truncate">{log.entity_id || "-"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Total: {total} entries</span>
            <div className="flex gap-1">
              <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Prev</Button>
              <Button variant="outline" size="sm" disabled={(page + 1) * 50 >= total} onClick={() => setPage(page + 1)}>Next</Button>
            </div>
          </div>
        </div>
      </AppShell>
    </RequirePermission>
  );
}
