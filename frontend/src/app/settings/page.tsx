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
import { Settings, Building2, Palette, Calendar, AlertTriangle, Cpu, Moon, Sun, Save } from "lucide-react";
import toast from "react-hot-toast";

const SETTING_GROUPS = [
  { key: "institution", label: "Institution", icon: <Building2 size={18} /> },
  { key: "branding", label: "Branding", icon: <Palette size={18} /> },
  { key: "academic_year", label: "Academic Year", icon: <Calendar size={18} /> },
  { key: "working_days", label: "Working Days", icon: <Calendar size={18} /> },
  { key: "constraints", label: "Default Constraints", icon: <AlertTriangle size={18} /> },
  { key: "ai_preferences", label: "AI Preferences", icon: <Cpu size={18} /> },
  { key: "theme", label: "Theme", icon: <Moon size={18} /> },
];

export default function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeGroup, setActiveGroup] = useState("institution");

  useEffect(() => {
    api.get<Record<string, string>>("/settings")
      .then((data) => setSettings(data))
      .catch((e) => { console.error("API error:", e) })
      .finally(() => setLoading(false));
  }, []);

  const updateSetting = (key: string, value: string) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      await Promise.all(
        Object.entries(settings).map(([key, value]) =>
          api.put(`/settings/${key}`, { value })
        )
      );
      toast.success("Settings saved");
    } catch (e: any) {
      toast.error(e.message || "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const filteredSettings = Object.entries(settings).filter(([k]) => k.startsWith(activeGroup));

  return (
    <RequirePermission permission="manage:settings">
      <AppShell title="Enterprise Settings">
        <div className="space-y-6 animate-fade-in">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-primary/10"><Settings size={24} className="text-primary" /></div>
              <div>
                <h2 className="text-lg font-semibold">Settings</h2>
                <p className="text-sm text-muted-foreground">Configure institution, branding, and AI preferences</p>
              </div>
            </div>
            <Button onClick={saveSettings} disabled={saving}>
              <Save size={16} className="mr-1" /> {saving ? "Saving..." : "Save All"}
            </Button>
          </div>

          <div className="flex gap-1 flex-wrap">
            {SETTING_GROUPS.map((g) => (
              <Button key={g.key} variant={activeGroup === g.key ? "default" : "outline"} size="sm" onClick={() => setActiveGroup(g.key)}>
                {g.icon} {g.label}
              </Button>
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                {SETTING_GROUPS.find((g) => g.key === activeGroup)?.icon}
                {SETTING_GROUPS.find((g) => g.key === activeGroup)?.label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}</div>
              ) : filteredSettings.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-8">No settings in this group</p>
              ) : (
                <div className="space-y-4">
                  {filteredSettings.map(([key, value]) => (
                    <div key={key} className="grid grid-cols-3 gap-4 items-center">
                      <label className="text-sm font-medium text-muted-foreground col-span-1">
                        {key.replace(`${activeGroup}_`, "").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                      </label>
                      <Input
                        className="col-span-2"
                        value={value || ""}
                        onChange={(e) => updateSetting(key, e.target.value)}
                      />
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

