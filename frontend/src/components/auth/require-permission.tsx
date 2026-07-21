"use client";

import { useAuthStore } from "@/stores/auth-store";
import { can, type Permission } from "@/lib/rbac";
import { Card, CardContent } from "@/components/ui/card";
import { ShieldAlert } from "lucide-react";

interface RequirePermissionProps {
  permission: Permission;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function RequirePermission({ permission, children, fallback }: RequirePermissionProps) {
  const { user, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
      </div>
    );
  }

  if (!user || !can(user.role, permission)) {
    if (fallback) return <>{fallback}</>;
    return (
      <div className="flex items-center justify-center min-h-[400px] p-8">
        <Card className="max-w-md w-full text-center">
          <CardContent className="py-12">
            <ShieldAlert size={48} className="mx-auto mb-4 text-muted-foreground" />
            <h2 className="text-lg font-semibold mb-2">Access Denied</h2>
            <p className="text-sm text-muted-foreground">
              You don&apos;t have the required permissions to access this page.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return <>{children}</>;
}
