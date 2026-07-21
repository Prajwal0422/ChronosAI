"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CalendarDays } from "lucide-react";

const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const now = new Date();
const year = now.getFullYear();
const month = now.getMonth();
const daysInMonth = new Date(year, month + 1, 0).getDate();
const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const today = now.getDate();

export function CalendarWidget() {
  const firstDay = new Date(year, month, 1).getDay();
  const offset = firstDay === 0 ? 6 : firstDay - 1;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <CalendarDays size={16} className="text-primary" />
          <CardTitle className="text-sm">
            {monthNames[month]} {year}
          </CardTitle>
        </div>
      </CardHeader>
      <CardContent className="p-3 pt-0">
        <div className="grid grid-cols-6 gap-0.5 text-center text-[10px] font-medium text-muted-foreground mb-1">
          {days.map((d) => <div key={d} className="py-1">{d}</div>)}
        </div>
        <div className="grid grid-cols-6 gap-0.5 text-center text-xs">
          {Array.from({ length: offset }).map((_, i) => (
            <div key={`empty-${i}`} />
          ))}
          {Array.from({ length: daysInMonth }).map((_, i) => {
            const date = i + 1;
            const isToday = date === today;
            return (
              <div
                key={date}
                className={`py-1 rounded ${
                  isToday ? "bg-primary text-primary-foreground font-semibold" : "text-muted-foreground hover:bg-accent/50"
                }`}
              >
                {date}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
