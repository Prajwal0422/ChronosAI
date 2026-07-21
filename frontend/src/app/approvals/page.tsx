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
import { CheckCircle, Send, Eye, Archive, XCircle, Clock, Check, FileText } from "lucide-react";
import { Approval } from "@/types";
import toast from "react-hot-toast";

const statusBadge: Record<string, "outline" | "secondary" | "success" | "default" | "warning"> = {
  draft: "secondary", generated: "outline", under_review: "warning",
  approved: "success", published: "success", archived: "secondary",
};

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");

  const fetchApprovals = async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = {};
      if (filter) params.status = filter;
      const data = await api.get<{ items: Approval[]; total: number }>("/approvals", params);
      setApprovals(data.items);
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  };

  useEffect(() => { fetchApprovals() }, [filter]);

  const handleAction = async (id: string, action: string) => {
    try {
      const result = await api.post(`/approvals/${id}/${action}`);
      toast.success(`${action} successful`);
      fetchApprovals();
    } catch (e: any) {
      toast.error(e.message || `${action} failed`);
    }
  };

  return (
    <RequirePermission permission="manage:approvals">
      <AppShell title="Approval Workflow">
        <div className="space-y-6 animate-fade-in">
          <Card className="bg-gradient-to-br from-primary/5 via-primary/0 to-info/5 border-primary/10">
            <CardContent className="flex items-center gap-4 p-6">
              <div className="p-3 rounded-xl bg-primary/10"><CheckCircle size={28} className="text-primary" /></div>
              <div>
                <h2 className="text-lg font-semibold">Timetable Approval Workflow</h2>
                <p className="text-sm text-muted-foreground">Generated → Under Review → Approved → Published</p>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-2">
            {["", "draft", "generated", "under_review", "approved", "published", "archived"].map((s) => (
              <Button key={s} variant={filter === s ? "default" : "outline"} size="sm" onClick={() => setFilter(s)}>
                {s || "All"}
              </Button>
            ))}
          </div>

          <Card>
            <CardContent className="p-0">
              {loading ? (
                <div className="p-6 space-y-3">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-16 w-full" />)}</div>
              ) : approvals.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-12">No approvals found</p>
              ) : (
                <div className="divide-y divide-border/50">
                  {approvals.map((a) => (
                    <div key={a.id} className="flex items-center justify-between p-4">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="p-2 rounded-lg bg-primary/10 shrink-0">
                          <FileText size={18} className="text-primary" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium">Timetable {a.timetable_id.slice(0, 8)}...</p>
                          <div className="flex items-center gap-2 mt-0.5">
                            <Badge variant={statusBadge[a.status] || "outline"} className="text-[10px]">{a.status}</Badge>
                            {a.requested_at && <span className="text-[10px] text-muted-foreground">Requested: {new Date(a.requested_at).toLocaleDateString()}</span>}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-1 shrink-0">
                        {a.status === "generated" && (
                          <Button size="sm" variant="outline" onClick={() => handleAction(a.id, "submit-review")}>
                            <Send size={14} className="mr-1" /> Submit
                          </Button>
                        )}
                        {a.status === "under_review" && (
                          <>
                            <Button size="sm" variant="outline" onClick={() => handleAction(a.id, "approve")}>
                              <Check size={14} className="mr-1" /> Approve
                            </Button>
                          </>
                        )}
                        {a.status === "approved" && (
                          <Button size="sm" variant="outline" onClick={() => handleAction(a.id, "publish")}>
                            <Send size={14} className="mr-1" /> Publish
                          </Button>
                        )}
                        {(a.status === "published" || a.status === "approved") && (
                          <Button size="sm" variant="ghost" onClick={() => handleAction(a.id, "archive")}>
                            <Archive size={14} /> Archive
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
