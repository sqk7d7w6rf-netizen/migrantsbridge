"use client";

import { useState, useEffect } from "react";
import { useAvailability, useUpdateAvailability } from "@/hooks/queries/use-appointments";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Save } from "lucide-react";

const DAYS = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
];

const TIME_SLOTS = Array.from({ length: 24 }, (_, i) => {
  const hour = Math.floor(i / 2) + 8;
  const minutes = i % 2 === 0 ? "00" : "30";
  if (hour > 19) return null;
  return `${hour.toString().padStart(2, "0")}:${minutes}`;
}).filter(Boolean) as string[];

interface SlotState {
  [key: string]: boolean;
}

export default function AvailabilityPage() {
  const { data: availability, isLoading } = useAvailability();
  const updateAvailability = useUpdateAvailability();
  const [slots, setSlots] = useState<SlotState>({});
  const [isDragging, setIsDragging] = useState(false);
  const [dragValue, setDragValue] = useState(false);

  useEffect(() => {
    if (availability) {
      const initial: SlotState = {};
      availability.forEach((slot) => {
        const start = slot.start_time.substring(0, 5);
        const end = slot.end_time.substring(0, 5);
        TIME_SLOTS.forEach((time) => {
          if (time >= start && time < end) {
            initial[`${slot.day_of_week}-${time}`] = true;
          }
        });
      });
      setSlots(initial);
    }
  }, [availability]);

  const getSlotKey = (day: number, time: string) => `${day}-${time}`;

  const handleMouseDown = (day: number, time: string) => {
    const key = getSlotKey(day, time);
    const newValue = !slots[key];
    setIsDragging(true);
    setDragValue(newValue);
    setSlots((prev) => ({ ...prev, [key]: newValue }));
  };

  const handleMouseEnter = (day: number, time: string) => {
    if (!isDragging) return;
    const key = getSlotKey(day, time);
    setSlots((prev) => ({ ...prev, [key]: dragValue }));
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleSave = () => {
    const slotsByDay = new Map<number, string[]>();

    Object.entries(slots).forEach(([key, isAvailable]) => {
      if (!isAvailable) return;
      const [dayStr, time] = key.split("-");
      const day = parseInt(dayStr, 10);
      const existing = slotsByDay.get(day) || [];
      existing.push(time);
      slotsByDay.set(day, existing);
    });

    const availabilitySlots = Array.from(slotsByDay.entries()).flatMap(
      ([day, times]) => {
        times.sort();
        const ranges: { start: string; end: string }[] = [];
        let rangeStart = times[0];
        let prevTime = times[0];

        for (let i = 1; i < times.length; i++) {
          const expectedNext =
            prevTime.endsWith("00")
              ? prevTime.replace("00", "30")
              : `${(parseInt(prevTime.split(":")[0], 10) + 1).toString().padStart(2, "0")}:00`;

          if (times[i] !== expectedNext) {
            ranges.push({ start: rangeStart, end: addThirtyMinutes(prevTime) });
            rangeStart = times[i];
          }
          prevTime = times[i];
        }
        ranges.push({ start: rangeStart, end: addThirtyMinutes(prevTime) });

        return ranges.map((range) => ({
          user_id: "",
          day_of_week: day,
          start_time: range.start,
          end_time: range.end,
          is_recurring: true,
        }));
      }
    );

    updateAvailability.mutate(availabilitySlots);
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Availability"
          description="Manage your availability schedule"
        />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  return (
    <div className="space-y-6" onMouseUp={handleMouseUp}>
      <PageHeader
        title="Availability"
        description="Click and drag to set your available time slots"
        actions={
          <Button onClick={handleSave} disabled={updateAvailability.isPending}>
            <Save className="mr-2 h-4 w-4" />
            {updateAvailability.isPending ? "Saving..." : "Save Changes"}
          </Button>
        }
      />

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Weekly Schedule</CardTitle>
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <div className="h-3 w-3 rounded bg-primary" />
              <span>Available</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="h-3 w-3 rounded bg-muted" />
              <span>Unavailable</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <div className="min-w-[700px]">
              <div className="grid grid-cols-8 gap-px bg-border">
                <div className="bg-background p-2" />
                {DAYS.map((day) => (
                  <div
                    key={day}
                    className="bg-background p-2 text-center text-xs font-medium"
                  >
                    {day.substring(0, 3)}
                  </div>
                ))}

                {TIME_SLOTS.map((time) => (
                  <>
                    <div
                      key={`label-${time}`}
                      className="bg-background p-2 text-right text-xs text-muted-foreground"
                    >
                      {formatTimeLabel(time)}
                    </div>
                    {DAYS.map((_, dayIndex) => {
                      const key = getSlotKey(dayIndex, time);
                      const isAvailable = !!slots[key];
                      return (
                        <div
                          key={`${dayIndex}-${time}`}
                          className={cn(
                            "h-6 cursor-pointer select-none transition-colors",
                            isAvailable
                              ? "bg-primary/80 hover:bg-primary"
                              : "bg-background hover:bg-muted"
                          )}
                          onMouseDown={() => handleMouseDown(dayIndex, time)}
                          onMouseEnter={() => handleMouseEnter(dayIndex, time)}
                        />
                      );
                    })}
                  </>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function formatTimeLabel(time: string): string {
  const [hourStr, min] = time.split(":");
  const hour = parseInt(hourStr, 10);
  const ampm = hour >= 12 ? "PM" : "AM";
  const h = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
  return `${h}:${min} ${ampm}`;
}

function addThirtyMinutes(time: string): string {
  const [hourStr, minStr] = time.split(":");
  let hour = parseInt(hourStr, 10);
  let min = parseInt(minStr, 10) + 30;
  if (min >= 60) {
    min -= 60;
    hour += 1;
  }
  return `${hour.toString().padStart(2, "0")}:${min.toString().padStart(2, "0")}`;
}
