"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Server, Activity, Database, Globe } from "lucide-react";

const statuses = [
  { label: "API Server", value: "Operational", icon: Server, status: "success" as const },
  { label: "Database", value: "Connected", icon: Database, status: "success" as const },
  { label: "AI Engine", value: "Ready", icon: Activity, status: "success" as const },
  { label: "CDN", value: "Online", icon: Globe, status: "success" as const },
];

export function SystemStatus() {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm">System Status</CardTitle>
      </CardHeader>
      <CardContent className="p-3 pt-0 space-y-1.5">
        {statuses.map((s) => {
          const Icon = s.icon;
          return (
            <div key={s.label} className="flex items-center justify-between p-2 rounded-lg hover:bg-accent/30 transition-colors">
              <div className="flex items-center gap-2">
                <Icon size={14} className="text-muted-foreground" />
                <span className="text-xs">{s.label}</span>
              </div>
              <span className="flex items-center gap-1.5 text-xs text-success">
                <span className="w-1.5 h-1.5 rounded-full bg-success" />
                {s.value}
              </span>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
