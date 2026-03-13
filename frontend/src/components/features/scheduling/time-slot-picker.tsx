"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { format, parse } from "date-fns";

interface TimeSlot {
  start_time: string;
  end_time: string;
}

interface TimeSlotPickerProps {
  slots: TimeSlot[];
  selectedSlot: TimeSlot | null;
  onSelectSlot: (slot: TimeSlot) => void;
  loading?: boolean;
}

export function TimeSlotPicker({
  slots,
  selectedSlot,
  onSelectSlot,
  loading = false,
}: TimeSlotPickerProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-3 gap-2">
        {Array.from({ length: 9 }).map((_, i) => (
          <div
            key={i}
            className="h-10 animate-pulse rounded-md bg-muted"
          />
        ))}
      </div>
    );
  }

  if (slots.length === 0) {
    return (
      <div className="flex items-center justify-center rounded-md border border-dashed p-6">
        <p className="text-sm text-muted-foreground">
          No available time slots for this date
        </p>
      </div>
    );
  }

  const morningSlots = slots.filter((s) => {
    const hour = parseInt(s.start_time.split(":")[0], 10);
    return hour < 12;
  });
  const afternoonSlots = slots.filter((s) => {
    const hour = parseInt(s.start_time.split(":")[0], 10);
    return hour >= 12 && hour < 17;
  });
  const eveningSlots = slots.filter((s) => {
    const hour = parseInt(s.start_time.split(":")[0], 10);
    return hour >= 17;
  });

  const formatTime = (time: string) => {
    try {
      return format(parse(time, "HH:mm", new Date()), "h:mm a");
    } catch {
      return time;
    }
  };

  const renderSlotGroup = (label: string, groupSlots: TimeSlot[]) => {
    if (groupSlots.length === 0) return null;
    return (
      <div className="space-y-2">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          {label}
        </p>
        <div className="grid grid-cols-3 gap-2">
          {groupSlots.map((slot) => {
            const isSelected =
              selectedSlot?.start_time === slot.start_time &&
              selectedSlot?.end_time === slot.end_time;
            return (
              <Button
                key={`${slot.start_time}-${slot.end_time}`}
                variant={isSelected ? "default" : "outline"}
                size="sm"
                className={cn(
                  "text-xs",
                  isSelected && "ring-2 ring-primary ring-offset-2"
                )}
                onClick={() => onSelectSlot(slot)}
              >
                {formatTime(slot.start_time)}
              </Button>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {renderSlotGroup("Morning", morningSlots)}
      {renderSlotGroup("Afternoon", afternoonSlots)}
      {renderSlotGroup("Evening", eveningSlots)}
    </div>
  );
}
