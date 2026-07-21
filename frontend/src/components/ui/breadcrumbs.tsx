"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, LayoutDashboard } from "lucide-react";

const routeLabels: Record<string, string> = {
  dashboard: "Dashboard",
  colleges: "Colleges",
  departments: "Departments",
  teachers: "Teachers",
  subjects: "Subjects",
  classrooms: "Classrooms",
  laboratories: "Laboratories",
  "time-slots": "Time Slots",
  calendar: "Calendar",
  constraints: "Constraints",
  timetables: "Timetables",
  import: "Import",
  export: "Export",
  analytics: "Analytics",
  settings: "Settings",
  profile: "Profile",
};

export function Breadcrumbs() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  if (segments.length === 0) return null;

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-xs text-muted-foreground">
      <Link href="/dashboard" className="hover:text-foreground transition-colors">
        <LayoutDashboard size={12} />
      </Link>
      {segments.map((segment, i) => {
        const href = "/" + segments.slice(0, i + 1).join("/");
        const label = routeLabels[segment] || segment.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
        const isLast = i === segments.length - 1;
        return (
          <span key={segment} className="flex items-center gap-1.5">
            <ChevronRight size={10} />
            {isLast ? (
              <span className="text-foreground/80 font-medium">{label}</span>
            ) : (
              <Link href={href} className="hover:text-foreground transition-colors">
                {label}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
