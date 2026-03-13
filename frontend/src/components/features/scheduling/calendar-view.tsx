"use client";

import { useState, useMemo } from "react";
import {
  format,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  addDays,
  isSameMonth,
  isToday,
  addMonths,
  subMonths,
} from "date-fns";
import { Appointment } from "@/types/appointment";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { APPOINTMENT_STATUSES } from "@/lib/constants";

interface CalendarViewProps {
  appointments: Appointment[];
  onDateClick: (date: Date) => void;
  onAppointmentClick: (appointment: Appointment) => void;
}

const statusColors: Record<string, string> = {
  scheduled: "bg-blue-500",
  confirmed: "bg-green-500",
  completed: "bg-gray-400",
  cancelled: "bg-red-400",
  no_show: "bg-orange-400",
};

export function CalendarView({
  appointments,
  onDateClick,
  onAppointmentClick,
}: CalendarViewProps) {
  const [currentMonth, setCurrentMonth] = useState(new Date());

  const calendarDays = useMemo(() => {
    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(monthStart);
    const calStart = startOfWeek(monthStart);
    const calEnd = endOfWeek(monthEnd);

    const days: Date[] = [];
    let day = calStart;
    while (day <= calEnd) {
      days.push(day);
      day = addDays(day, 1);
    }
    return days;
  }, [currentMonth]);

  const appointmentsByDate = useMemo(() => {
    const map = new Map<string, Appointment[]>();
    appointments.forEach((apt) => {
      const dateKey = format(new Date(apt.start_time), "yyyy-MM-dd");
      const existing = map.get(dateKey) || [];
      existing.push(apt);
      map.set(dateKey, existing);
    });
    return map;
  }, [appointments]);

  const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  return (
    <div className="rounded-lg border bg-card">
      <div className="flex items-center justify-between border-b p-4">
        <h2 className="text-lg font-semibold">
          {format(currentMonth, "MMMM yyyy")}
        </h2>
        <div className="flex items-center gap-1">
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentMonth(new Date())}
          >
            Today
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-7">
        {weekDays.map((day) => (
          <div
            key={day}
            className="border-b px-2 py-2 text-center text-xs font-medium text-muted-foreground"
          >
            {day}
          </div>
        ))}

        {calendarDays.map((day, index) => {
          const dateKey = format(day, "yyyy-MM-dd");
          const dayAppointments = appointmentsByDate.get(dateKey) || [];
          const inCurrentMonth = isSameMonth(day, currentMonth);
          const today = isToday(day);

          return (
            <div
              key={index}
              className={cn(
                "min-h-[100px] border-b border-r p-1 cursor-pointer hover:bg-accent/50 transition-colors",
                !inCurrentMonth && "bg-muted/30",
                index % 7 === 0 && "border-l"
              )}
              onClick={() => onDateClick(day)}
            >
              <div className="flex justify-end">
                <span
                  className={cn(
                    "flex h-6 w-6 items-center justify-center rounded-full text-xs",
                    today && "bg-primary text-primary-foreground font-bold",
                    !inCurrentMonth && "text-muted-foreground"
                  )}
                >
                  {format(day, "d")}
                </span>
              </div>
              <div className="mt-1 space-y-0.5">
                {dayAppointments.slice(0, 3).map((apt) => (
                  <button
                    key={apt.id}
                    className={cn(
                      "flex w-full items-center gap-1 rounded px-1 py-0.5 text-left text-[10px] leading-tight text-white truncate",
                      statusColors[apt.status] || "bg-blue-500"
                    )}
                    onClick={(e) => {
                      e.stopPropagation();
                      onAppointmentClick(apt);
                    }}
                    title={`${format(new Date(apt.start_time), "h:mm a")} - ${apt.title}`}
                  >
                    <span className="truncate">
                      {format(new Date(apt.start_time), "h:mm")} {apt.title}
                    </span>
                  </button>
                ))}
                {dayAppointments.length > 3 && (
                  <span className="block text-[10px] text-muted-foreground pl-1">
                    +{dayAppointments.length - 3} more
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex items-center gap-4 border-t p-3">
        {Object.entries(APPOINTMENT_STATUSES).map(([key, config]) => (
          <div key={key} className="flex items-center gap-1.5">
            <div
              className={cn(
                "h-2.5 w-2.5 rounded-full",
                statusColors[key] || "bg-gray-400"
              )}
            />
            <span className="text-xs text-muted-foreground">
              {config.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
