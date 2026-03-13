"use client";

import { useState, useEffect } from "react";
import {
  useNotificationPreferences,
  useUpdateNotificationPreferences,
} from "@/hooks/queries/use-communications";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { NotificationPreference } from "@/types/communication";
import { Save, Bell } from "lucide-react";
import { cn } from "@/lib/utils";

const DEFAULT_PREFERENCES: NotificationPreference[] = [
  {
    event_type: "appointment_reminder",
    event_label: "Appointment Reminders",
    email_enabled: true,
    sms_enabled: true,
    in_app_enabled: true,
  },
  {
    event_type: "appointment_confirmed",
    event_label: "Appointment Confirmed",
    email_enabled: true,
    sms_enabled: false,
    in_app_enabled: true,
  },
  {
    event_type: "appointment_cancelled",
    event_label: "Appointment Cancelled",
    email_enabled: true,
    sms_enabled: true,
    in_app_enabled: true,
  },
  {
    event_type: "case_status_update",
    event_label: "Case Status Updates",
    email_enabled: true,
    sms_enabled: false,
    in_app_enabled: true,
  },
  {
    event_type: "document_request",
    event_label: "Document Requests",
    email_enabled: true,
    sms_enabled: false,
    in_app_enabled: true,
  },
  {
    event_type: "new_message",
    event_label: "New Messages",
    email_enabled: false,
    sms_enabled: false,
    in_app_enabled: true,
  },
  {
    event_type: "intake_submitted",
    event_label: "New Intake Submissions",
    email_enabled: true,
    sms_enabled: false,
    in_app_enabled: true,
  },
  {
    event_type: "task_assigned",
    event_label: "Task Assignments",
    email_enabled: true,
    sms_enabled: false,
    in_app_enabled: true,
  },
];

export default function CommunicationSettingsPage() {
  const { data: serverPrefs, isLoading } = useNotificationPreferences();
  const updatePrefs = useUpdateNotificationPreferences();
  const [preferences, setPreferences] = useState<NotificationPreference[]>([]);

  useEffect(() => {
    if (serverPrefs && serverPrefs.length > 0) {
      setPreferences(serverPrefs);
    } else if (!isLoading) {
      setPreferences(DEFAULT_PREFERENCES);
    }
  }, [serverPrefs, isLoading]);

  const toggleChannel = (
    eventType: string,
    channel: "email_enabled" | "sms_enabled" | "in_app_enabled"
  ) => {
    setPreferences((prev) =>
      prev.map((p) =>
        p.event_type === eventType ? { ...p, [channel]: !p[channel] } : p
      )
    );
  };

  const handleSave = () => {
    updatePrefs.mutate(preferences);
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Notification Settings"
          description="Configure how notifications are sent for each event type"
        />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Notification Settings"
        description="Configure how notifications are sent for each event type"
        actions={
          <Button onClick={handleSave} disabled={updatePrefs.isPending}>
            <Save className="mr-2 h-4 w-4" />
            {updatePrefs.isPending ? "Saving..." : "Save Settings"}
          </Button>
        }
      />

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notification Channels
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="pb-3 pr-4 text-left text-sm font-medium">
                    Event Type
                  </th>
                  <th className="pb-3 px-4 text-center text-sm font-medium">
                    Email
                  </th>
                  <th className="pb-3 px-4 text-center text-sm font-medium">
                    SMS
                  </th>
                  <th className="pb-3 pl-4 text-center text-sm font-medium">
                    In-App
                  </th>
                </tr>
              </thead>
              <tbody>
                {preferences.map((pref) => (
                  <tr key={pref.event_type} className="border-b last:border-0">
                    <td className="py-4 pr-4 text-sm">{pref.event_label}</td>
                    <td className="py-4 px-4 text-center">
                      <ToggleButton
                        enabled={pref.email_enabled}
                        onClick={() =>
                          toggleChannel(pref.event_type, "email_enabled")
                        }
                      />
                    </td>
                    <td className="py-4 px-4 text-center">
                      <ToggleButton
                        enabled={pref.sms_enabled}
                        onClick={() =>
                          toggleChannel(pref.event_type, "sms_enabled")
                        }
                      />
                    </td>
                    <td className="py-4 pl-4 text-center">
                      <ToggleButton
                        enabled={pref.in_app_enabled}
                        onClick={() =>
                          toggleChannel(pref.event_type, "in_app_enabled")
                        }
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function ToggleButton({
  enabled,
  onClick,
}: {
  enabled: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
        enabled ? "bg-primary" : "bg-muted"
      )}
    >
      <span
        className={cn(
          "inline-block h-4 w-4 rounded-full bg-white transition-transform",
          enabled ? "translate-x-6" : "translate-x-1"
        )}
      />
    </button>
  );
}
