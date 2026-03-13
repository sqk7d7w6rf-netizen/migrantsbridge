"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FinancialGoal } from "@/types/goal";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { CalendarDays } from "lucide-react";

const categoryLabels: Record<FinancialGoal["category"], string> = {
  emergency_fund: "Emergency Fund",
  education: "Education",
  housing: "Housing",
  business: "Business",
  retirement: "Retirement",
  other: "Other",
};

const categoryColors: Record<FinancialGoal["category"], string> = {
  emergency_fund: "bg-orange-100 text-orange-800",
  education: "bg-blue-100 text-blue-800",
  housing: "bg-green-100 text-green-800",
  business: "bg-purple-100 text-purple-800",
  retirement: "bg-indigo-100 text-indigo-800",
  other: "bg-gray-100 text-gray-800",
};

const statusColors: Record<FinancialGoal["status"], string> = {
  active: "bg-green-100 text-green-800",
  completed: "bg-blue-100 text-blue-800",
  paused: "bg-yellow-100 text-yellow-800",
  cancelled: "bg-red-100 text-red-800",
};

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

interface GoalCardProps {
  goal: FinancialGoal;
}

export function GoalCard({ goal }: GoalCardProps) {
  return (
    <Link href={`/wealth/goals/${goal.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-base font-semibold line-clamp-1">
              {goal.name}
            </CardTitle>
            <span
              className={cn(
                "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium shrink-0",
                statusColors[goal.status]
              )}
            >
              {goal.status}
            </span>
          </div>
          <Badge
            variant="outline"
            className={cn("w-fit text-xs", categoryColors[goal.category])}
          >
            {categoryLabels[goal.category]}
          </Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium">
                {Math.round(goal.progress_percentage)}%
              </span>
            </div>
            <div className="h-2 w-full rounded-full bg-secondary">
              <div
                className={cn(
                  "h-2 rounded-full transition-all",
                  goal.progress_percentage >= 100
                    ? "bg-green-500"
                    : goal.progress_percentage >= 50
                      ? "bg-blue-500"
                      : "bg-orange-500"
                )}
                style={{
                  width: `${Math.min(goal.progress_percentage, 100)}%`,
                }}
              />
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">
                {formatCurrency(goal.current_amount)}
              </span>
              <span className="font-medium">
                {formatCurrency(goal.target_amount)}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <CalendarDays className="h-3 w-3" />
            <span>Target: {format(new Date(goal.target_date), "MMM d, yyyy")}</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
