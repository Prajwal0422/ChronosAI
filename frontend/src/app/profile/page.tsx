"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { toast } from "react-hot-toast";
import { api } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";
import { Shield, Calendar } from "lucide-react";

interface ProfileData {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string | null;
}

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("en-US", { year: "numeric", month: "long" });
}

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user);
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [fullName, setFullName] = useState("");

  useEffect(() => {
    api.get<ProfileData>("/profile")
      .then((data) => {
        setProfile(data);
        setFullName(data.full_name);
      })
      .catch((e) => { console.error("API error:", e) })
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put("/profile", { full_name: fullName });
      setProfile((prev) => prev ? { ...prev, full_name: fullName } : null);
      toast.success("Profile updated");
    } catch {
      toast.error("Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  return (
    <AppShell title="Profile">
      <div className="space-y-6 animate-fade-in max-w-2xl">
        <Card>
          <CardContent className="p-6">
            {loading ? (
              <div className="flex items-center gap-4">
                <Skeleton className="w-16 h-16 rounded-full" />
                <div className="space-y-2"><Skeleton className="h-5 w-40" /><Skeleton className="h-4 w-24" /></div>
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary text-xl font-bold">
                  {profile ? getInitials(profile.full_name) : "?"}
                </div>
                <div>
                  <h2 className="text-xl font-semibold">{profile?.full_name || "—"}</h2>
                  <p className="text-sm text-muted-foreground capitalize">{profile?.role || "—"}</p>
                  <Badge variant={profile?.is_active ? "outline" : "secondary"} className="mt-1">
                    {profile?.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Personal Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {loading ? (
              <div className="grid grid-cols-2 gap-4">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="space-y-2"><Skeleton className="h-4 w-16" /><Skeleton className="h-9 w-full" /></div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Full Name</label>
                  <Input value={fullName} onChange={(e) => setFullName(e.target.value)} />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Employee Code</label>
                  <Input defaultValue={profile?.id?.split("-")?.[0]?.toUpperCase() || "—"} disabled />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Email</label>
                  <Input type="email" defaultValue={profile?.email || "—"} disabled />
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Account Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Shield size={16} className="text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">Role</p>
                  <p className="text-xs text-muted-foreground capitalize">{profile?.role || "—"}</p>
                </div>
              </div>
              <Badge>{profile?.role === "admin" ? "Full Access" : "Limited"}</Badge>
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Calendar size={16} className="text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">Member Since</p>
                  <p className="text-xs text-muted-foreground">{formatDate(profile?.created_at || null)}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-3">
          <Button variant="outline">Change Password</Button>
          <Button onClick={handleSave} disabled={saving || loading}>
            {saving ? "Saving..." : "Save Profile"}
          </Button>
        </div>
      </div>
    </AppShell>
  );
}

