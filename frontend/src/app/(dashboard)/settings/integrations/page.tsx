"use client";

import { PageHeader } from "@/components/layout/page-header";
import { StatusBadge } from "@/components/shared/status-badge";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Mail,
  MessageSquare,
  HardDrive,
  CreditCard,
  Sparkles,
  Settings,
} from "lucide-react";

const connectionStatusMap: Record<string, { label: string; color: string }> = {
  connected: { label: "Connected", color: "bg-green-100 text-green-800" },
  disconnected: { label: "Disconnected", color: "bg-gray-100 text-gray-800" },
};

const integrations = [
  {
    id: "email",
    name: "Email (SMTP)",
    description:
      "Send transactional and notification emails through your SMTP server. Used for client communications, reminders, and team alerts.",
    icon: Mail,
    status: "connected" as const,
  },
  {
    id: "sms",
    name: "SMS (Twilio)",
    description:
      "Send SMS notifications to clients for appointment reminders, case updates, and urgent communications via Twilio.",
    icon: MessageSquare,
    status: "disconnected" as const,
  },
  {
    id: "storage",
    name: "Storage (S3 / Local)",
    description:
      "Store uploaded documents and generated reports. Supports Amazon S3 for cloud storage or local filesystem for on-premise deployments.",
    icon: HardDrive,
    status: "connected" as const,
  },
  {
    id: "payments",
    name: "Payments (Stripe)",
    description:
      "Process client payments and manage billing through Stripe. Supports one-time payments and recurring subscriptions.",
    icon: CreditCard,
    status: "disconnected" as const,
  },
  {
    id: "ai",
    name: "AI (Claude API)",
    description:
      "Power intelligent features like workflow generation, document classification, eligibility assessment, and automated summaries using Claude.",
    icon: Sparkles,
    status: "connected" as const,
  },
];

export default function IntegrationsSettingsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Integrations"
        description="Manage connections to external services and APIs"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {integrations.map((integration) => {
          const Icon = integration.icon;
          return (
            <Card key={integration.id} className="flex flex-col h-full">
              <CardContent className="flex flex-col flex-1 p-6 space-y-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                      <Icon className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold">{integration.name}</h3>
                      <StatusBadge
                        status={integration.status}
                        statusMap={connectionStatusMap}
                        className="mt-1"
                      />
                    </div>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground flex-1">
                  {integration.description}
                </p>
                <Button variant="outline" className="w-full">
                  <Settings className="mr-2 h-4 w-4" />
                  Configure
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
