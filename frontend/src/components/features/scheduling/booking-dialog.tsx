"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TimeSlotPicker } from "./time-slot-picker";
import { useCreateAppointment, useAvailableSlots } from "@/hooks/queries/use-appointments";
import { format } from "date-fns";

interface BookingDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  selectedDate?: Date;
}

export function BookingDialog({
  open,
  onOpenChange,
  selectedDate,
}: BookingDialogProps) {
  const [title, setTitle] = useState("");
  const [clientId, setClientId] = useState("");
  const [clientName, setClientName] = useState("");
  const [staffId, setStaffId] = useState("");
  const [type, setType] = useState<"in_person" | "video" | "phone">("video");
  const [date, setDate] = useState(
    selectedDate ? format(selectedDate, "yyyy-MM-dd") : ""
  );
  const [selectedSlot, setSelectedSlot] = useState<{
    start_time: string;
    end_time: string;
  } | null>(null);
  const [location, setLocation] = useState("");
  const [meetingUrl, setMeetingUrl] = useState("");
  const [notes, setNotes] = useState("");

  const { data: availableSlots, isLoading: slotsLoading } = useAvailableSlots(
    date,
    staffId || undefined
  );

  const createAppointment = useCreateAppointment();

  const handleSubmit = () => {
    if (!title || !clientId || !staffId || !date || !selectedSlot) return;

    const startDateTime = `${date}T${selectedSlot.start_time}:00`;
    const endDateTime = `${date}T${selectedSlot.end_time}:00`;

    createAppointment.mutate(
      {
        title,
        client_id: clientId,
        assigned_to: staffId,
        type,
        start_time: startDateTime,
        end_time: endDateTime,
        location: type === "in_person" ? location : undefined,
        meeting_url: type === "video" ? meetingUrl : undefined,
        notes: notes || undefined,
      },
      {
        onSuccess: () => {
          onOpenChange(false);
          resetForm();
        },
      }
    );
  };

  const resetForm = () => {
    setTitle("");
    setClientId("");
    setClientName("");
    setStaffId("");
    setType("video");
    setDate(selectedDate ? format(selectedDate, "yyyy-MM-dd") : "");
    setSelectedSlot(null);
    setLocation("");
    setMeetingUrl("");
    setNotes("");
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>New Appointment</DialogTitle>
          <DialogDescription>
            Schedule a new appointment with a client.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              placeholder="Appointment title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="client">Client</Label>
              <Input
                id="client"
                placeholder="Search client..."
                value={clientName}
                onChange={(e) => {
                  setClientName(e.target.value);
                  setClientId(e.target.value);
                }}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="staff">Staff Member</Label>
              <Input
                id="staff"
                placeholder="Assign staff..."
                value={staffId}
                onChange={(e) => setStaffId(e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="type">Type</Label>
              <Select
                value={type}
                onValueChange={(v) =>
                  setType(v as "in_person" | "video" | "phone")
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="in_person">In Person</SelectItem>
                  <SelectItem value="video">Video Call</SelectItem>
                  <SelectItem value="phone">Phone Call</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="date">Date</Label>
              <Input
                id="date"
                type="date"
                value={date}
                onChange={(e) => {
                  setDate(e.target.value);
                  setSelectedSlot(null);
                }}
              />
            </div>
          </div>

          {type === "in_person" && (
            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                placeholder="Office address or room"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>
          )}

          {type === "video" && (
            <div className="space-y-2">
              <Label htmlFor="meeting-url">Meeting Link</Label>
              <Input
                id="meeting-url"
                placeholder="https://meet.google.com/..."
                value={meetingUrl}
                onChange={(e) => setMeetingUrl(e.target.value)}
              />
            </div>
          )}

          {date && (
            <div className="space-y-2">
              <Label>Available Time Slots</Label>
              <TimeSlotPicker
                slots={availableSlots || []}
                selectedSlot={selectedSlot}
                onSelectSlot={setSelectedSlot}
                loading={slotsLoading}
              />
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              placeholder="Additional notes..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={createAppointment.isPending}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={
              !title ||
              !clientId ||
              !staffId ||
              !date ||
              !selectedSlot ||
              createAppointment.isPending
            }
          >
            {createAppointment.isPending ? "Creating..." : "Create Appointment"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
