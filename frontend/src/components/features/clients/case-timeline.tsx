"use client";

import { CaseHistory } from "@/types/case";
import { format } from "date-fns";
import {
  ArrowRightLeft,
  MessageSquare,
  UserPlus,
  FileText,
  Clock,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface CaseTimelineProps {
  events: CaseHistory[];
  className?: string;
}

const actionIcons: Record<string, typeof Clock> = {
  status_change: ArrowRightLeft,
  note_added: MessageSquare,
  assigned: UserPlus,
  document_added: FileText,
};

const actionColors: Record<string, string> = {
  status_change: "bg-blue-100 text-blue-600",
  note_added: "bg-green-100 text-green-600",
  assigned: "bg-purple-100 text-purple-600",
  document_added: "bg-orange-100 text-orange-600",
};

function getEventDescription(event: CaseHistory): string {
  if (event.field_changed === "status") {
    return `Status changed from "${event.old_value}" to "${event.new_value}"`;
  }
  if (event.field_changed === "assigned_to") {
    return `Case reassigned to ${event.new_value || "unassigned"}`;
  }
  if (event.action === "note_added") {
    return "Added a note";
  }
  if (event.action === "document_added") {
    return "Attached a document";
  }
  return event.action.replace(/_/g, " ");
}

export function CaseTimeline({ events, className }: CaseTimelineProps) {
  if (events.length === 0) {
    return (
      <p className="text-sm text-muted-foreground py-4">
        No history events yet.
      </p>
    );
  }

  return (
    <div className={cn("relative", className)}>
      <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />
      <div className="space-y-6">
        {events.map((event) => {
          const Icon = actionIcons[event.action] ?? Clock;
          const colorClass = actionColors[event.action] ?? "bg-gray-100 text-gray-600";

          return (
            <div key={event.id} className="relative flex gap-4 pl-0">
              <div
                className={cn(
                  "relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                  colorClass
                )}
              >
                <Icon className="h-4 w-4" />
              </div>
              <div className="flex-1 pt-0.5">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">
                    {event.user_name}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {format(new Date(event.created_at), "MMM d, yyyy h:mm a")}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mt-0.5">
                  {getEventDescription(event)}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
