"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api-client";
import { RequirePermission } from "@/components/auth/require-permission";
import { CalendarDays, Ban } from "lucide-react";

const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

interface Holiday {
  id: string;
  date: string;
  name: string;
  holiday_type: string;
}

interface CalendarEntry {
  id: string;
  term_name: string;
  academic_year: string;
  start_date: string;
  end_date: string;
}

const now = new Date();
const year = now.getFullYear();
const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const currentMonthLabel = `${monthNames[now.getMonth()]} ${year}`;

export default function CalendarPage() {
  const [calendars, setCalendars] = useState<CalendarEntry[]>([]);
  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get<{ items: CalendarEntry[]; total: number }>("/calendar"),
      api.get<{ items: Holiday[]; total: number }>("/holidays"),
    ])
      .then(([calData, holData]) => {
        setCalendars(calData.items);
        setHolidays(holData.items);
      })
      .catch((e) => { console.error("API error:", e) })
      .finally(() => setLoading(false));
  }, []);

  const daysInMonth = new Date(year, now.getMonth() + 1, 0).getDate();

  const getDayForDate = (d: number): string => {
    const dow = new Date(year, now.getMonth(), d).getDay();
    const map = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    return map[dow];
  };

  return (
    <RequirePermission permission="view:analytics">
      <AppShell title="Academic Calendar">
        <div className="space-y-6 animate-fade-in">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div className="flex items-center gap-3">
                <CalendarDays size={20} className="text-primary" />
                <CardTitle className="text-base">
                  {loading ? <Skeleton className="h-5 w-32 inline-block" /> : `${currentMonthLabel}${calendars.length > 0 ? ` — ${calendars[0].term_name}` : ""}`}
                </CardTitle>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">Working Days</Button>
                <Button variant="outline" size="sm">Holidays</Button>
                <Button size="sm">Add Event</Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="grid grid-cols-6 gap-2">
                  {Array.from({ length: 30 }).map((_, i) => <Skeleton key={i} className="h-20 rounded-lg" />)}
                </div>
              ) : (
                <div className="grid grid-cols-6 gap-2">
                  {days.map((day) => (
                    <div key={day} className="text-center text-xs font-medium text-muted-foreground py-2">{day}</div>
                  ))}
                  {Array.from({ length: daysInMonth }).map((_, i) => {
                    const date = i + 1;
                    const dayName = getDayForDate(date);
                    const holiday = holidays.find((h) => {
                      const hDate = new Date(h.date);
                      return hDate.getFullYear() === year && hDate.getMonth() === now.getMonth() && hDate.getDate() === date;
                    });
                    const isWeekend = dayName === "Sun" || dayName === "Sat";
                    const eventType = holiday ? "holiday" : isWeekend ? "holiday" : "working";
                    const eventName = holiday ? holiday.name : isWeekend ? "Weekend" : "";
                    return (
                      <div key={i} className={`min-h-[80px] rounded-lg border border-border/50 p-2 text-sm ${eventType === "holiday" ? "bg-destructive/5 border-destructive/20" : "bg-card"}`}>
                        <span className={`font-medium ${eventType === "holiday" ? "text-destructive" : ""}`}>{date}</span>
                        {eventName && (
                          <div className="mt-1">
                            <Badge variant="destructive" className="text-[10px] px-1 py-0">
                              <Ban size={10} className="mr-1" />
                              {holiday ? holiday.name.split(" ").slice(0, 2).join(" ") : "Weekend"}
                            </Badge>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </AppShell>
    </RequirePermission>
  );
}

