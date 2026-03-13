"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAppointment, useUpdateAppointment, useDeleteAppointment } from "@/hooks/queries/use-appointments";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { StatusBadge } from "@/components/shared/status-badge";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { APPOINTMENT_STATUSES, APPOINTMENT_TYPES } from "@/lib/constants";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import {
  Clock,
  MapPin,
  User,
  Video,
  Phone,
  Calendar,
  FileText,
  ExternalLink,
  XCircle,
  RefreshCw,
} from "lucide-react";
import { format } from "date-fns";
import Link from "next/link";

export default function AppointmentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const appointmentId = params.appointmentId as string;

  const { data: appointment, isLoading } = useAppointment(appointmentId);
  const updateAppointment = useUpdateAppointment(appointmentId);
  const deleteAppointment = useDeleteAppointment();

  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [notes, setNotes] = useState("");
  const [editingNotes, setEditingNotes] = useState(false);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Appointment Details" />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  if (!appointment) {
    return (
      <div className="space-y-6">
        <PageHeader title="Appointment Not Found" />
        <p className="text-muted-foreground">
          The requested appointment could not be found.
        </p>
      </div>
    );
  }

  const typeIcons = {
    in_person: MapPin,
    video: Video,
    phone: Phone,
  };
  const TypeIcon = typeIcons[appointment.type] || MapPin;

  const handleCancel = () => {
    updateAppointment.mutate(
      { status: "cancelled" },
      {
        onSuccess: () => setCancelDialogOpen(false),
      }
    );
  };

  const handleComplete = () => {
    updateAppointment.mutate({ status: "completed" });
  };

  const handleConfirm = () => {
    updateAppointment.mutate({ status: "confirmed" });
  };

  const handleSaveNotes = () => {
    updateAppointment.mutate(
      { notes },
      {
        onSuccess: () => setEditingNotes(false),
      }
    );
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title={appointment.title}
        description={`Appointment with ${appointment.client_name || "Client"}`}
        actions={
          <div className="flex items-center gap-2">
            {appointment.status === "scheduled" && (
              <Button variant="outline" onClick={handleConfirm}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Confirm
              </Button>
            )}
            {(appointment.status === "scheduled" ||
              appointment.status === "confirmed") && (
              <>
                <Button variant="outline" onClick={handleComplete}>
                  Mark Complete
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => setCancelDialogOpen(true)}
                >
                  <XCircle className="mr-2 h-4 w-4" />
                  Cancel
                </Button>
              </>
            )}
          </div>
        }
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Appointment Details</span>
                <StatusBadge
                  status={appointment.status}
                  statusMap={APPOINTMENT_STATUSES}
                />
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-xs text-muted-foreground">Date</p>
                    <p className="text-sm font-medium">
                      {format(
                        new Date(appointment.start_time),
                        "EEEE, MMMM d, yyyy"
                      )}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-xs text-muted-foreground">Time</p>
                    <p className="text-sm font-medium">
                      {format(new Date(appointment.start_time), "h:mm a")} -{" "}
                      {format(new Date(appointment.end_time), "h:mm a")}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <TypeIcon className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-xs text-muted-foreground">Type</p>
                    <p className="text-sm font-medium">
                      {APPOINTMENT_TYPES[appointment.type]?.label ||
                        appointment.type}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-xs text-muted-foreground">Staff</p>
                    <p className="text-sm font-medium">
                      {appointment.assigned_to_name || appointment.assigned_to}
                    </p>
                  </div>
                </div>
              </div>

              {appointment.location && (
                <>
                  <Separator />
                  <div className="flex items-center gap-3">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">Location</p>
                      <p className="text-sm font-medium">
                        {appointment.location}
                      </p>
                    </div>
                  </div>
                </>
              )}

              {appointment.meeting_url && (
                <>
                  <Separator />
                  <div className="flex items-center gap-3">
                    <Video className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">
                        Meeting Link
                      </p>
                      <a
                        href={appointment.meeting_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm font-medium text-primary hover:underline inline-flex items-center gap-1"
                      >
                        Join Meeting
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </div>
                  </div>
                </>
              )}

              {appointment.description && (
                <>
                  <Separator />
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">
                      Description
                    </p>
                    <p className="text-sm">{appointment.description}</p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base">Notes</CardTitle>
              {!editingNotes && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setNotes(appointment.notes || "");
                    setEditingNotes(true);
                  }}
                >
                  Edit
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {editingNotes ? (
                <div className="space-y-3">
                  <Textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={4}
                    placeholder="Add notes about this appointment..."
                  />
                  <div className="flex gap-2 justify-end">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setEditingNotes(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      size="sm"
                      onClick={handleSaveNotes}
                      disabled={updateAppointment.isPending}
                    >
                      Save Notes
                    </Button>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  {appointment.notes || "No notes added yet."}
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Client Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                  <User className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="font-medium">
                    {appointment.client_name || "Unknown Client"}
                  </p>
                  <Link
                    href={`/clients/${appointment.client_id}`}
                    className="text-xs text-primary hover:underline"
                  >
                    View Profile
                  </Link>
                </div>
              </div>

              {appointment.case_id && (
                <>
                  <Separator />
                  <div className="flex items-center gap-3">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-xs text-muted-foreground">
                        Linked Case
                      </p>
                      <Link
                        href={`/cases/${appointment.case_id}`}
                        className="text-sm text-primary hover:underline"
                      >
                        View Case
                      </Link>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  Reminder Sent
                </span>
                <Badge variant={appointment.reminder_sent ? "default" : "secondary"}>
                  {appointment.reminder_sent ? "Yes" : "No"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Created</span>
                <span className="text-sm">
                  {format(new Date(appointment.created_at), "MMM d, yyyy")}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Updated</span>
                <span className="text-sm">
                  {format(new Date(appointment.updated_at), "MMM d, yyyy")}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <ConfirmDialog
        open={cancelDialogOpen}
        onOpenChange={setCancelDialogOpen}
        title="Cancel Appointment"
        description="Are you sure you want to cancel this appointment? The client will be notified."
        confirmLabel="Cancel Appointment"
        variant="destructive"
        onConfirm={handleCancel}
        loading={updateAppointment.isPending}
      />
    </div>
  );
}
