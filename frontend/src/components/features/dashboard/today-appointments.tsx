"use client";

import { format, parseISO } from "date-fns";
import { MapPin, Video, Phone, Calendar } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAppointments } from "@/hooks/queries/use-appointments";
import { type Appointment } from "@/types/appointment";

const today = format(new Date(), "yyyy-MM-dd");

const typeIconMap: Record<Appointment["type"], typeof MapPin> = {
  in_person: MapPin,
  video: Video,
  phone: Phone,
};

const statusConfig: Record<
  Appointment["status"],
  { label: string; className: string }
> = {
  scheduled: {
    label: "Scheduled",
    className: "bg-blue-100 text-blue-700 border-blue-200",
  },
  confirmed: {
    label: "Confirmed",
    className: "bg-green-100 text-green-700 border-green-200",
  },
  completed: {
    label: "Completed",
    className: "bg-gray-100 text-gray-600 border-gray-200",
  },
  cancelled: {
    label: "Cancelled",
    className: "bg-red-100 text-red-700 border-red-200",
  },
  no_show: {
    label: "No Show",
    className: "bg-orange-100 text-orange-700 border-orange-200",
  },
};

export function TodayAppointments() {
  const { data, isLoading } = useAppointments({
    start_date: today,
    end_date: today,
    page_size: 5,
  });

  const appointments = data?.items ?? [];
  const total = data?.total ?? 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle className="text-base">Today&apos;s Appointments</CardTitle>
        {!isLoading && (
          <Badge variant="outline" className="text-xs">
            {total}
          </Badge>
        )}
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3">
                <Skeleton className="h-9 w-9 rounded-lg shrink-0" />
                <div className="flex-1 space-y-1.5">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              </div>
            ))}
          </div>
        ) : appointments.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-6">
            No appointments today
          </p>
        ) : (
          <div className="space-y-3">
            {appointments.map((appointment) => {
              const TypeIcon = typeIconMap[appointment.type] ?? Calendar;
              const status =
                statusConfig[appointment.status] ?? statusConfig.scheduled;

              return (
                <div key={appointment.id} className="flex items-center gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-muted">
                    <TypeIcon className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {appointment.title}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {appointment.client_name} &middot;{" "}
                      {format(parseISO(appointment.start_time), "h:mm a")}
                    </p>
                  </div>
                  <span
                    className={`shrink-0 inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${status.className}`}
                  >
                    {status.label}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
