"use client";

import { Appointment } from "@/types/appointment";
import { StatusBadge } from "@/components/shared/status-badge";
import { APPOINTMENT_STATUSES, APPOINTMENT_TYPES } from "@/lib/constants";
import { Card, CardContent } from "@/components/ui/card";
import { Clock, MapPin, User, Video, Phone } from "lucide-react";
import { format } from "date-fns";
import Link from "next/link";

interface AppointmentCardProps {
  appointment: Appointment;
  compact?: boolean;
}

const typeIcons = {
  in_person: MapPin,
  video: Video,
  phone: Phone,
};

export function AppointmentCard({
  appointment,
  compact = false,
}: AppointmentCardProps) {
  const TypeIcon = typeIcons[appointment.type] || MapPin;

  if (compact) {
    return (
      <Link href={`/scheduling/${appointment.id}`}>
        <div className="flex items-center gap-3 rounded-md border p-3 hover:bg-accent transition-colors">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
            <TypeIcon className="h-4 w-4 text-primary" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{appointment.title}</p>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>
                {format(new Date(appointment.start_time), "h:mm a")} -{" "}
                {format(new Date(appointment.end_time), "h:mm a")}
              </span>
            </div>
          </div>
          <StatusBadge
            status={appointment.status}
            statusMap={APPOINTMENT_STATUSES}
          />
        </div>
      </Link>
    );
  }

  return (
    <Link href={`/scheduling/${appointment.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer">
        <CardContent className="p-4">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <h4 className="font-medium">{appointment.title}</h4>
              {appointment.client_name && (
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <User className="h-3.5 w-3.5" />
                  <span>{appointment.client_name}</span>
                </div>
              )}
            </div>
            <StatusBadge
              status={appointment.status}
              statusMap={APPOINTMENT_STATUSES}
            />
          </div>

          <div className="mt-3 space-y-1.5">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-3.5 w-3.5" />
              <span>
                {format(new Date(appointment.start_time), "MMM d, yyyy")} at{" "}
                {format(new Date(appointment.start_time), "h:mm a")} -{" "}
                {format(new Date(appointment.end_time), "h:mm a")}
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <TypeIcon className="h-3.5 w-3.5" />
              <span>
                {APPOINTMENT_TYPES[appointment.type]?.label || appointment.type}
              </span>
              {appointment.location && <span>- {appointment.location}</span>}
            </div>
            {appointment.assigned_to_name && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <User className="h-3.5 w-3.5" />
                <span>Staff: {appointment.assigned_to_name}</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
