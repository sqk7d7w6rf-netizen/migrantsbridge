"use client";

import { cn } from "@/lib/utils";
import {
  Mail,
  Bell,
  FileText,
  CheckSquare,
  Clock,
  Cog,
} from "lucide-react";
import { WorkflowStep } from "@/types/workflow";

interface ActionNodeProps {
  step: WorkflowStep;
  isSelected?: boolean;
  onClick?: () => void;
}

const stepTypeIcons: Record<string, typeof Cog> = {
  action: CheckSquare,
  notification: Bell,
  delay: Clock,
  approval: FileText,
};

const stepTypeColors: Record<string, { bg: string; icon: string; border: string }> = {
  action: {
    bg: "bg-blue-50",
    icon: "text-blue-700 bg-blue-100",
    border: "border-blue-300",
  },
  notification: {
    bg: "bg-purple-50",
    icon: "text-purple-700 bg-purple-100",
    border: "border-purple-300",
  },
  delay: {
    bg: "bg-yellow-50",
    icon: "text-yellow-700 bg-yellow-100",
    border: "border-yellow-300",
  },
  approval: {
    bg: "bg-orange-50",
    icon: "text-orange-700 bg-orange-100",
    border: "border-orange-300",
  },
};

export function ActionNode({ step, isSelected, onClick }: ActionNodeProps) {
  const colors = stepTypeColors[step.step_type] || stepTypeColors.action;
  const Icon = stepTypeIcons[step.step_type] || Cog;

  return (
    <div
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 rounded-lg border-2 p-4 shadow-sm transition-all cursor-pointer hover:shadow-md min-w-[220px]",
        colors.bg,
        isSelected
          ? "border-primary ring-2 ring-primary/20"
          : colors.border
      )}
    >
      <div
        className={cn(
          "flex h-10 w-10 items-center justify-center rounded-full shrink-0",
          colors.icon
        )}
      >
        <Icon className="h-5 w-5" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold truncate">{step.name}</p>
        <p className="text-xs text-muted-foreground capitalize">
          {step.step_type}
        </p>
        {step.description && (
          <p className="text-xs text-muted-foreground truncate mt-0.5">
            {step.description}
          </p>
        )}
      </div>
    </div>
  );
}
