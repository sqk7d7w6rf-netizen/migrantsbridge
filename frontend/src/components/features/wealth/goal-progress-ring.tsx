"use client";

import { cn } from "@/lib/utils";

interface GoalProgressRingProps {
  percentage: number;
  size?: number;
  strokeWidth?: number;
  className?: string;
}

export function GoalProgressRing({
  percentage,
  size = 120,
  strokeWidth = 10,
  className,
}: GoalProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const clampedPercentage = Math.min(Math.max(percentage, 0), 100);
  const strokeDashoffset =
    circumference - (clampedPercentage / 100) * circumference;

  const getColor = () => {
    if (clampedPercentage >= 100) return "text-green-500";
    if (clampedPercentage >= 75) return "text-blue-500";
    if (clampedPercentage >= 50) return "text-yellow-500";
    return "text-orange-500";
  };

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-muted/30"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className={cn("transition-all duration-500", getColor())}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold">{Math.round(clampedPercentage)}%</span>
        <span className="text-xs text-muted-foreground">complete</span>
      </div>
    </div>
  );
}
