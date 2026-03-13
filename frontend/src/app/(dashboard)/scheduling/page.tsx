"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useAppointments } from "@/hooks/queries/use-appointments";
import { PageHeader } from "@/components/layout/page-header";
import { CalendarView } from "@/components/features/scheduling/calendar-view";
import { AppointmentCard } from "@/components/features/scheduling/appointment-card";
import { BookingDialog } from "@/components/features/scheduling/booking-dialog";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Calendar } from "lucide-react";
import { format, isToday, startOfMonth, endOfMonth } from "date-fns";

export default function SchedulingPage() {
  const [bookingOpen, setBookingOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined);
  const router = useRouter();

  const now = new Date();
  const { data, isLoading } = useAppointments({
    start_date: format(startOfMonth(now), "yyyy-MM-dd"),
    end_date: format(endOfMonth(now), "yyyy-MM-dd"),
  });

  const appointments = useMemo(() => data?.items ?? [], [data]);

  const todaysAppointments = useMemo(
    () =>
      appointments
        .filter((apt) => isToday(new Date(apt.start_time)))
        .sort(
          (a, b) =>
            new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
        ),
    [appointments]
  );

  const handleDateClick = (date: Date) => {
    setSelectedDate(date);
    setBookingOpen(true);
  };

  const handleAppointmentClick = (appointment: { id: string }) => {
    router.push(`/scheduling/${appointment.id}`);
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Scheduling"
          description="Manage appointments and calendar"
        />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Scheduling"
        description="Manage appointments and calendar"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" asChild>
              <a href="/scheduling/availability">Manage Availability</a>
            </Button>
            <Button onClick={() => setBookingOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              New Appointment
            </Button>
          </div>
        }
      />

      {appointments.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title="No appointments yet"
          description="Get started by scheduling your first appointment."
          actionLabel="New Appointment"
          onAction={() => setBookingOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-4">
          <div className="xl:col-span-3">
            <CalendarView
              appointments={appointments}
              onDateClick={handleDateClick}
              onAppointmentClick={handleAppointmentClick}
            />
          </div>

          <div className="xl:col-span-1">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">
                  Today&apos;s Appointments
                </CardTitle>
                <p className="text-xs text-muted-foreground">
                  {format(new Date(), "EEEE, MMMM d")}
                </p>
              </CardHeader>
              <CardContent className="space-y-2">
                {todaysAppointments.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-4 text-center">
                    No appointments today
                  </p>
                ) : (
                  todaysAppointments.map((apt) => (
                    <AppointmentCard
                      key={apt.id}
                      appointment={apt}
                      compact
                    />
                  ))
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      <BookingDialog
        open={bookingOpen}
        onOpenChange={setBookingOpen}
        selectedDate={selectedDate}
      />
    </div>
  );
}
