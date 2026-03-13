"use client";

import { cn } from "@/lib/utils";
import { Zap, Clock, MousePointerClick } from "lucide-react";

interface TriggerNodeProps {
  triggerType: "manual" | "event" | "schedule";
  config?: Record<string, unknown>;
  isSelected?: boolean;
  onClick?: () => void;
}

const triggerIcons = {
  manual: MousePointerClick,
  event: Zap,
  schedule: Clock,
};

const triggerLabels = {
  manual: "Manual Trigger",
  event: "Event Trigger",
  schedule: "Scheduled Trigger",
};

function getConfigSummary(
  triggerType: string,
  config?: Record<string, unknown>
): string {
  if (!config || Object.keys(config).length === 0) return "Not configured";
  if (triggerType === "schedule" && config.cron) return `Cron: ${config.cron}`;
  if (triggerType === "event" && config.event_name)
    return `Event: ${config.event_name}`;
  return "Configured";
}

export function TriggerNode({
  triggerType,
  config,
  isSelected,
  onClick,
}: TriggerNodeProps) {
  const Icon = triggerIcons[triggerType];

  return (
    <div
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 rounded-lg border-2 bg-card p-4 shadow-sm transition-all cursor-pointer hover:shadow-md min-w-[220px]",
        isSelected
          ? "border-primary ring-2 ring-primary/20"
          : "border-green-300 bg-green-50"
      )}
    >
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-100">
        <Icon className="h-5 w-5 text-green-700" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold">{triggerLabels[triggerType]}</p>
        <p className="text-xs text-muted-foreground truncate">
          {getConfigSummary(triggerType, config)}
        </p>
      </div>
    </div>
  );
}
