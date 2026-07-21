"use client";

import { useState, useRef, useEffect } from "react";
import { Bell, Search, User, ChevronDown, LogOut, Settings as SettingsIcon, Moon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/stores/auth-store";
import { logout } from "@/lib/auth";
import { api } from "@/lib/api-client";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface NavbarProps {
  title?: string;
  children?: React.ReactNode;
}

function getInitials(name: string): string {
  return name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);
}

export function Navbar({ title = "Dashboard", children }: NavbarProps) {
  const user = useAuthStore((s) => s.user);
  const [profileOpen, setProfileOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const profileRef = useRef<HTMLDivElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    api.get<{ unread_count: number }>("/notifications/unread-count")
      .then((d) => setUnreadCount(d.unread_count))
      .catch(() => {});
    const interval = setInterval(() => {
      api.get<{ unread_count: number }>("/notifications/unread-count")
        .then((d) => setUnreadCount(d.unread_count))
        .catch(() => {});
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) setProfileOpen(false);
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) setNotifOpen(false);
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && e.currentTarget.value.trim()) {
      router.push(`/search?q=${encodeURIComponent(e.currentTarget.value.trim())}`);
    }
  };

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-6 border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="flex items-center gap-4 min-w-0">
        <div className="flex flex-col min-w-0">
          <h1 className="text-lg font-semibold truncate">{title}</h1>
          {children}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <div className="relative hidden md:block">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search..."
            aria-label="Search"
            className="w-56 lg:w-72 pl-9 h-9 bg-secondary/50 border-0 focus-visible:bg-secondary/80"
            onKeyDown={handleSearchKeyDown}
          />
        </div>

        <div ref={notifRef} className="relative">
          <Link href="/notifications">
            <Button
              variant="ghost"
              size="icon"
              className="relative"
              aria-label="Notifications"
            >
              <Bell size={18} />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-destructive text-destructive-foreground text-[9px] font-bold rounded-full flex items-center justify-center">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </Button>
          </Link>
        </div>

        <Button variant="ghost" size="icon" aria-label="Dark mode" disabled>
          <Moon size={18} />
        </Button>

        <div ref={profileRef} className="relative">
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="flex items-center gap-2 pl-3 border-l border-border/50 hover:bg-accent/50 rounded-lg p-1.5 transition-colors"
            aria-label="User menu"
          >
            <div className="flex items-center justify-center w-7 h-7 rounded-full bg-primary/10 text-primary text-[10px] font-semibold">
              {user ? getInitials(user.full_name) : "?"}
            </div>
            <div className="hidden md:block text-left">
              <p className="text-sm font-medium leading-tight">{user?.full_name ?? "User"}</p>
              <p className="text-[10px] text-muted-foreground capitalize">{user?.role ?? ""}</p>
            </div>
            <ChevronDown size={14} className="text-muted-foreground hidden md:block" />
          </button>

          {profileOpen && (
            <div className="absolute right-0 top-full mt-2 w-56 rounded-xl border border-border/50 bg-card/95 backdrop-blur-xl shadow-xl shadow-black/10 p-2">
              <div className="px-3 py-2 border-b border-border/30 mb-1">
                <p className="text-sm font-medium">{user?.full_name}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
              <Link
                href="/profile"
                onClick={() => setProfileOpen(false)}
                className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-accent/50 transition-colors"
              >
                <User size={15} />
                Profile
              </Link>
              <Link
                href="/settings"
                onClick={() => setProfileOpen(false)}
                className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-accent/50 transition-colors"
              >
                <SettingsIcon size={15} />
                Settings
              </Link>
              <div className="border-t border-border/30 mt-1 pt-1">
                <button
                  onClick={logout}
                  className="flex items-center gap-2.5 w-full px-3 py-2 rounded-lg text-sm text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                >
                  <LogOut size={15} />
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
