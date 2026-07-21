"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api-client";
import { RequirePermission } from "@/components/auth/require-permission";
import { Bell, CheckCheck, Trash2, Mail, MailOpen, Sparkles, AlertTriangle, CheckCircle, Info, Calendar } from "lucide-react";
import { Notification } from "@/types";
import toast from "react-hot-toast";

const typeIcon: Record<string, React.ReactNode> = {
  generation_completed: <Sparkles size={16} className="text-primary" />,
  conflict_detected: <AlertTriangle size={16} className="text-destructive" />,
  approval_requested: <Bell size={16} className="text-warning" />,
  approval_approved: <CheckCircle size={16} className="text-success" />,
  schedule_changed: <Calendar size={16} className="text-info" />,
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "unread">("all");

  const fetchNotifs = async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = {};
      if (filter === "unread") params.unread_only = true;
      const data = await api.get<{ items: Notification[]; total: number }>("/notifications", params);
      setNotifications(data.items);
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  };

  useEffect(() => { fetchNotifs() }, [filter]);

  const markRead = async (id: string) => {
    try {
      await api.post(`/notifications/${id}/read`);
      setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, is_read: true } : n));
    } catch (e: any) { toast.error(e.message) }
  };

  const markAllRead = async () => {
    try {
      await api.post("/notifications/read-all");
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      toast.success("All marked as read");
    } catch (e: any) { toast.error(e.message) }
  };

  const deleteNotif = async (id: string) => {
    try {
      await api.delete(`/notifications/${id}`);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    } catch (e: any) { toast.error(e.message) }
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <RequirePermission permission="manage:notifications">
      <AppShell title="Notification Center">
        <div className="space-y-6 animate-fade-in">
          <Card className="bg-gradient-to-br from-primary/5 via-primary/0 to-info/5 border-primary/10">
            <CardContent className="flex items-center justify-between p-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-primary/10"><Bell size={28} className="text-primary" /></div>
                <div>
                  <h2 className="text-lg font-semibold">Notification Center</h2>
                  <p className="text-sm text-muted-foreground">{unreadCount} unread notifications</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={markAllRead} disabled={unreadCount === 0}>
                  <CheckCheck size={14} className="mr-1" /> Mark All Read
                </Button>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-2">
            <Button variant={filter === "all" ? "default" : "outline"} size="sm" onClick={() => setFilter("all")}>All</Button>
            <Button variant={filter === "unread" ? "default" : "outline"} size="sm" onClick={() => setFilter("unread")}>Unread ({unreadCount})</Button>
          </div>

          <div className="space-y-2">
            {loading ? Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-20 w-full" />)
            : notifications.length === 0 ? (
              <Card><CardContent className="p-12 text-center text-muted-foreground">
                <Bell size={40} className="mx-auto mb-3 opacity-30" />
                <p>No notifications</p>
              </CardContent></Card>
            ) : notifications.map((n) => (
              <Card key={n.id} className={`transition-all ${!n.is_read ? 'border-primary/30 bg-primary/5' : ''}`}>
                <CardContent className="p-4 flex items-start gap-3">
                  <div className="mt-0.5">{typeIcon[n.notification_type] || <Info size={16} />}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-medium">{n.title}</h3>
                      {!n.is_read && <Badge variant="info" className="text-[9px] h-4">New</Badge>}
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">{n.message}</p>
                    <p className="text-[10px] text-muted-foreground/60 mt-1">
                      {n.created_at ? new Date(n.created_at).toLocaleString() : ""}
                    </p>
                  </div>
                  <div className="flex gap-1 shrink-0">
                    {!n.is_read && (
                      <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => markRead(n.id)} aria-label="Mark as read">
                        <MailOpen size={14} />
                      </Button>
                    )}
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive" onClick={() => deleteNotif(n.id)} aria-label="Delete">
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </AppShell>
    </RequirePermission>
  );
}
