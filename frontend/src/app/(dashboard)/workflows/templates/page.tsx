"use client";

import Link from "next/link";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  UserPlus,
  Bell,
  FileWarning,
  CalendarClock,
  Route,
  FileBarChart,
  Zap,
  Clock,
  MousePointerClick,
  ArrowRight,
} from "lucide-react";

const triggerBadgeMap: Record<string, { label: string; icon: typeof Zap }> = {
  event: { label: "Event", icon: Zap },
  schedule: { label: "Scheduled", icon: Clock },
  manual: { label: "Manual", icon: MousePointerClick },
};

const templates = [
  {
    id: "tpl-onboarding",
    name: "New Client Onboarding",
    description:
      "Automatically set up a new client record, send a welcome email, assign a case worker, and schedule an initial consultation when a client is registered.",
    triggerType: "event" as const,
    stepCount: 5,
    icon: UserPlus,
  },
  {
    id: "tpl-case-status",
    name: "Case Status Update Notification",
    description:
      "Send real-time notifications to clients and team members when a case status changes, including email and in-app alerts with next steps.",
    triggerType: "event" as const,
    stepCount: 4,
    icon: Bell,
  },
  {
    id: "tpl-doc-expiration",
    name: "Document Expiration Alert",
    description:
      "Monitor document expiry dates and send automated reminders at 90, 60, and 30 days before expiration. Escalate to the case worker if no action is taken.",
    triggerType: "schedule" as const,
    stepCount: 6,
    icon: FileWarning,
  },
  {
    id: "tpl-appointment",
    name: "Appointment Reminder Flow",
    description:
      "Send appointment reminders via email and SMS at 48 hours and 2 hours before a scheduled appointment, with rescheduling options included.",
    triggerType: "schedule" as const,
    stepCount: 4,
    icon: CalendarClock,
  },
  {
    id: "tpl-intake-routing",
    name: "Intake Auto-Routing",
    description:
      "Automatically route new intake submissions to the appropriate department based on case type, language preference, and urgency level.",
    triggerType: "event" as const,
    stepCount: 5,
    icon: Route,
  },
  {
    id: "tpl-monthly-report",
    name: "Monthly Report Generation",
    description:
      "Generate comprehensive monthly reports on case activity, team performance, billing summaries, and client engagement metrics on the first of every month.",
    triggerType: "schedule" as const,
    stepCount: 7,
    icon: FileBarChart,
  },
];

export default function WorkflowTemplatesPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Workflow Templates"
        description="Get started quickly with pre-built workflow templates tailored for immigration services"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {templates.map((template) => {
          const Icon = template.icon;
          const trigger = triggerBadgeMap[template.triggerType];
          const TriggerIcon = trigger.icon;

          return (
            <Card key={template.id} className="flex flex-col h-full">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Icon className="h-5 w-5 text-primary" />
                    </div>
                    <CardTitle className="text-base font-semibold line-clamp-1">
                      {template.name}
                    </CardTitle>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="flex flex-col flex-1 space-y-4">
                <p className="text-sm text-muted-foreground line-clamp-3 flex-1">
                  {template.description}
                </p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="flex items-center gap-1">
                      <TriggerIcon className="h-3 w-3" />
                      {trigger.label}
                    </Badge>
                    <Badge variant="secondary">
                      {template.stepCount} steps
                    </Badge>
                  </div>
                </div>
                <Button asChild className="w-full">
                  <Link href={`/workflows/builder?template=${template.id}`}>
                    Use Template
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
