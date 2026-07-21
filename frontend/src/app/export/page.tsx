"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RequirePermission } from "@/components/auth/require-permission";
import { Download, FileSpreadsheet, FileText, FileImage, CheckCircle2 } from "lucide-react";

const formats = [
  { label: "Excel", icon: FileSpreadsheet, ext: ".xlsx", desc: "Full timetable with formatting" },
  { label: "PDF", icon: FileText, ext: ".pdf", desc: "Print-ready document" },
  { label: "CSV", icon: FileText, ext: ".csv", desc: "Raw data export" },
  { label: "Image", icon: FileImage, ext: ".png", desc: "Visual snapshot" },
];

const recentExports = [
  { name: "CSE_SectionA_v3.xlsx", format: "Excel", date: "2 hours ago", size: "245 KB" },
  { name: "ECE_SectionB_v2.pdf", format: "PDF", date: "Yesterday", size: "1.2 MB" },
  { name: "ME_SectionA_v1.csv", format: "CSV", date: "2 days ago", size: "89 KB" },
];

export default function ExportPage() {
  return (
    <RequirePermission permission="manage:timetables">
      <AppShell title="Export">
        <div className="space-y-6 animate-fade-in">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Export Timetable</CardTitle>
              <CardDescription>Download generated timetables in your preferred format.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-4 gap-4 mb-6">
                {formats.map((f) => {
                  const Icon = f.icon;
                  return (
                    <div key={f.label} className="flex flex-col items-center gap-2 p-4 rounded-lg border border-border/50 bg-card/50">
                      <Icon size={28} className="text-primary" />
                      <span className="text-sm font-medium">{f.label}</span>
                      <span className="text-xs text-muted-foreground">{f.ext}</span>
                      <span className="text-[10px] text-muted-foreground text-center">{f.desc}</span>
                      <Button variant="outline" size="sm" className="mt-2 w-full">
                        <Download size={14} className="mr-1" /> Export
                      </Button>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Recent Exports</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentExports.map((exp) => (
                  <div key={exp.name} className="flex items-center justify-between p-3 rounded-lg border border-border/50">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/5">
                        <FileSpreadsheet size={16} className="text-primary" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{exp.name}</p>
                        <p className="text-xs text-muted-foreground">{exp.date} &middot; {exp.size}</p>
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" className="h-8 w-8"><Download size={14} /></Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </AppShell>
    </RequirePermission>
  );
}
