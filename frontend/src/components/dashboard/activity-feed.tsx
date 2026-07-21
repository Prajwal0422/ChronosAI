"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { CheckCircle2, AlertTriangle, ArrowUpRight } from "lucide-react";

interface ActivityItem {
  action: string;
  entity_type: string;
  timestamp: string | null;
}

interface ActivityFeedProps {
  activities: ActivityItem[];
  loading?: boolean;
}

function formatTimeAgo(timestamp: string | null): string {
  if (!timestamp) return "";
  const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function getStatus(action: string): "success" | "warning" | "info" {
  const lower = action.toLowerCase();
  if (lower.includes("conflict")) return "warning";
  if (lower.includes("generat") || lower.includes("publish") || lower.includes("create")) return "success";
  return "info";
}

export function ActivityFeed({ activities, loading }: ActivityFeedProps) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent className="p-3 pt-0">
        {loading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
          </div>
        ) : activities.length === 0 ? (
          <p className="text-xs text-muted-foreground py-6 text-center">No recent activity</p>
        ) : (
          <div className="space-y-1">
            {activities.slice(0, 6).map((activity, i) => {
              const status = getStatus(activity.action);
              return (
                <div key={i} className="flex items-start gap-2.5 p-2 rounded-lg hover:bg-accent/30 transition-colors">
                  <div className={`p-1 rounded-full mt-0.5 ${
                    status === "success" ? "bg-success/10 text-success" :
                    status === "warning" ? "bg-warning/10 text-warning" :
                    "bg-info/10 text-info"
                  }`}>
                    {status === "success" ? <CheckCircle2 size={12} /> :
                     status === "warning" ? <AlertTriangle size={12} /> :
                     <ArrowUpRight size={12} />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium capitalize">{activity.action.replace(/_/g, " ")}</p>
                    <p className="text-[10px] text-muted-foreground truncate">{activity.entity_type}</p>
                  </div>
                  <span className="text-[10px] text-muted-foreground whitespace-nowrap">{formatTimeAgo(activity.timestamp)}</span>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
