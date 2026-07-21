"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import { can } from "@/lib/rbac";
import type { Permission } from "@/lib/rbac";
import { logout } from "@/lib/auth";
import {
  LayoutDashboard, School, Building2, BookOpen, Users, GraduationCap,
  Monitor, FlaskConical, Clock, Calendar, AlertTriangle, Brain,
  FileSpreadsheet, Download, BarChart3, Settings, UserCircle,
  ChevronLeft, ChevronRight, LogOut, Lightbulb, Activity,
  GitCompareArrows, History, CheckCircle, ClipboardList, Bell,
  Search,
} from "lucide-react";
import { useState, useEffect, useCallback } from "react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
  permission?: Permission;
  section?: string;
}

const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: <LayoutDashboard size={18} /> },
  { label: "Colleges", href: "/colleges", icon: <School size={18} />, permission: "manage:colleges" },
  { label: "Departments", href: "/departments", icon: <Building2 size={18} />, permission: "manage:departments" },
  { label: "Semesters", href: "/semesters", icon: <BookOpen size={18} /> },
  { label: "Sections", href: "/sections", icon: <Users size={18} /> },
  { label: "Teachers", href: "/teachers", icon: <GraduationCap size={18} />, permission: "manage:teachers" },
  { label: "Subjects", href: "/subjects", icon: <BookOpen size={18} />, permission: "manage:subjects" },
  { label: "Classrooms", href: "/classrooms", icon: <Monitor size={18} />, permission: "manage:classrooms" },
  { label: "Laboratories", href: "/laboratories", icon: <FlaskConical size={18} />, permission: "manage:laboratories" },
  { label: "Time Slots", href: "/time-slots", icon: <Clock size={18} /> },
  { label: "Calendar", href: "/calendar", icon: <Calendar size={18} /> },
  { label: "Constraints", href: "/constraints", icon: <AlertTriangle size={18} /> },
  { label: "AI Generator", href: "/timetables", icon: <Brain size={18} />, permission: "manage:timetables" },
  { label: "Import", href: "/import", icon: <FileSpreadsheet size={18} /> },
  { label: "Export", href: "/export", icon: <Download size={18} /> },
  { label: "Analytics", href: "/analytics", icon: <BarChart3 size={18} />, permission: "view:analytics" },
  { label: "AI Insights", href: "/insights", icon: <Lightbulb size={18} />, permission: "view:analytics" },
  { label: "Health Score", href: "/health-score", icon: <Activity size={18} />, permission: "view:analytics" },
  { label: "Simulation", href: "/simulation", icon: <GitCompareArrows size={18} />, permission: "manage:timetables" },
  { label: "Version History", href: "/versions", icon: <History size={18} />, permission: "manage:timetables" },
  { label: "Approvals", href: "/approvals", icon: <CheckCircle size={18} />, permission: "manage:approvals" },
  { label: "Audit Logs", href: "/audit-logs", icon: <ClipboardList size={18} />, permission: "view:audit_logs" },
  { label: "Notifications", href: "/notifications", icon: <Bell size={18} />, permission: "manage:notifications" },
  { label: "Search", href: "/search", icon: <Search size={18} />, permission: "view:search" },
  { label: "Settings", href: "/settings", icon: <Settings size={18} />, permission: "manage:settings" },
  { label: "Profile", href: "/profile", icon: <UserCircle size={18} /> },
];

interface SidebarProps {
  onCollapse?: (collapsed: boolean) => void;
}

function getInitials(name: string): string {
  return name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);
}

export function Sidebar({ onCollapse }: SidebarProps) {
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const [collapsed, setCollapsed] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("sidebar_collapsed") === "true";
    }
    return false;
  });

  const toggle = useCallback(() => {
    setCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem("sidebar_collapsed", String(next));
      onCollapse?.(next);
      return next;
    });
  }, [onCollapse]);

  useEffect(() => {
    onCollapse?.(collapsed);
  }, []);

  const visibleItems = navItems.filter((item) => {
    if (!item.permission) return true;
    return can(user?.role ?? "", item.permission);
  });

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen bg-sidebar border-r border-sidebar-border transition-all duration-300 flex flex-col",
        collapsed ? "w-[68px]" : "w-[240px]"
      )}
    >
      <div className="flex items-center gap-3 px-4 h-16 border-b border-sidebar-border">
        <Link href="/dashboard" className="flex items-center gap-3 min-w-0">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary/10 shrink-0">
            <Brain size={18} className="text-primary" />
          </div>
          {!collapsed && (
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-semibold text-sidebar-accent-foreground truncate">
                ChronosAI
              </span>
              <span className="text-[10px] text-muted-foreground truncate">Enterprise Platform</span>
            </div>
          )}
        </Link>
      </div>

      <nav className="flex-1 overflow-y-auto scrollbar-hide px-2 py-4 space-y-1" aria-label="Sidebar navigation">
        {visibleItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "nav-link",
                isActive ? "nav-link-active" : "nav-link-inactive",
                collapsed && "justify-center px-2"
              )}
              title={collapsed ? item.label : undefined}
            >
              {item.icon}
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      <div className="p-2 border-t border-sidebar-border space-y-1">
        {user && !collapsed && (
          <div className="px-3 py-2 flex items-center gap-3">
            <div className="flex items-center justify-center w-7 h-7 rounded-full bg-primary/10 text-primary text-[10px] font-semibold shrink-0">
              {getInitials(user.full_name)}
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-xs font-medium truncate">{user.full_name}</span>
              <span className="text-[10px] text-muted-foreground capitalize truncate">{user.role}</span>
            </div>
          </div>
        )}
        <button
          onClick={logout}
          className={cn(
            "nav-link w-full text-sidebar-foreground hover:text-sidebar-accent-foreground hover:bg-sidebar-accent/50",
            collapsed && "justify-center px-2"
          )}
          aria-label="Logout"
        >
          <LogOut size={18} />
          {!collapsed && <span>Logout</span>}
        </button>
        <button
          onClick={toggle}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="flex items-center justify-center w-full h-8 rounded-lg text-sidebar-foreground hover:text-sidebar-accent-foreground hover:bg-sidebar-accent/50 transition-all duration-200"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>
    </aside>
  );
}
