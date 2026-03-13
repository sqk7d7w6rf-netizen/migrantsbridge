"use client";

import { cn } from "@/lib/utils";
import { GitBranch } from "lucide-react";
import { WorkflowStep } from "@/types/workflow";

interface ConditionNodeProps {
  step: WorkflowStep;
  isSelected?: boolean;
  onClick?: () => void;
}

export function ConditionNode({ step, isSelected, onClick }: ConditionNodeProps) {
  return (
    <div className="flex flex-col items-center">
      <div
        onClick={onClick}
        className={cn(
          "relative flex items-center justify-center w-[160px] h-[100px] cursor-pointer transition-all hover:scale-105",
          isSelected && "scale-105"
        )}
      >
        <svg
          viewBox="0 0 160 100"
          className="absolute inset-0 w-full h-full"
        >
          <polygon
            points="80,4 156,50 80,96 4,50"
            fill="hsl(var(--background))"
            stroke={isSelected ? "hsl(var(--primary))" : "#f59e0b"}
            strokeWidth="2"
          />
        </svg>
        <div className="relative flex flex-col items-center gap-1 z-10">
          <GitBranch className="h-4 w-4 text-amber-700" />
          <span className="text-xs font-semibold text-center max-w-[100px] truncate">
            {step.name}
          </span>
        </div>
      </div>
      <div className="flex items-center gap-16 mt-1">
        <span className="text-xs font-medium text-green-600">Yes</span>
        <span className="text-xs font-medium text-red-600">No</span>
      </div>
    </div>
  );
}
