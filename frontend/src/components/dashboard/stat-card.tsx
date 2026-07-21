"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string;
  change?: string;
  icon: LucideIcon;
  loading?: boolean;
  delay?: number;
}

export function StatCard({ title, value, change, icon: Icon, loading, delay = 0 }: StatCardProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader className="pb-2"><Skeleton className="h-4 w-24" /></CardHeader>
        <CardContent><Skeleton className="h-8 w-16" /></CardContent>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
    >
      <Card className="card-hover">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
          <div className="p-2 rounded-lg bg-primary/5">
            <Icon size={18} className="text-primary" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{value}</div>
          {change && <p className="text-xs text-muted-foreground mt-1">{change}</p>}
        </CardContent>
      </Card>
    </motion.div>
  );
}
