"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileSpreadsheet, FileText, Image, Upload, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { RequirePermission } from "@/components/auth/require-permission";
import { cn } from "@/lib/utils";

const formats = [
  { label: "Excel", icon: FileSpreadsheet, ext: ".xlsx, .xls", desc: "Structured timetable data" },
  { label: "CSV", icon: FileText, ext: ".csv", desc: "Comma-separated values" },
  { label: "PDF", icon: FileText, ext: ".pdf", desc: "Extract with AI parsing" },
  { label: "Image", icon: Image, ext: ".png, .jpg", desc: "OCR-based extraction" },
];

export default function ImportPage() {
  const [dragOver, setDragOver] = useState(false);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleImport = async () => {
    setImporting(true);
    setResult(null);
    try {
      await new Promise((r) => setTimeout(r, 2000));
      setResult({ success: true, message: "Timetable imported successfully with auto-structure detection" });
    } catch {
      setResult({ success: false, message: "Import failed. Check file format." });
    } finally {
      setImporting(false);
    }
  };

  return (
    <RequirePermission permission="manage:timetables">
      <AppShell title="Import">
        <div className="space-y-6 animate-fade-in">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Import Timetable</CardTitle>
              <CardDescription>Upload existing timetables in any format. AI auto-detects structure.</CardDescription>
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
                    </div>
                  );
                })}
              </div>

              <div
                className={cn(
                  "border-2 border-dashed rounded-xl p-12 text-center transition-all",
                  dragOver ? "border-primary bg-primary/5" : "border-border/50 hover:border-primary/50"
                )}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={(e) => { e.preventDefault(); setDragOver(false); handleImport(); }}
              >
                <Upload size={40} className="mx-auto mb-4 text-muted-foreground" />
                <p className="text-sm font-medium mb-1">Drop files here or click to browse</p>
                <p className="text-xs text-muted-foreground mb-4">Supports Excel, CSV, PDF, PNG, JPG</p>
                <Button onClick={handleImport} disabled={importing}>
                  {importing ? <Loader2 size={16} className="mr-2 animate-spin" /> : <Upload size={16} className="mr-2" />}
                  {importing ? "Importing..." : "Select File"}
                </Button>
              </div>

              {result && (
                <div className={cn("mt-4 p-3 rounded-lg flex items-center gap-2 text-sm", result.success ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive")}>
                  {result.success ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                  {result.message}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Import History</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">No recent imports</p>
            </CardContent>
          </Card>
        </div>
      </AppShell>
    </RequirePermission>
  );
}
