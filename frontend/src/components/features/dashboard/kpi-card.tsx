"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { type LucideIcon, TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon: LucideIcon;
}

export function KpiCard({
  title,
  value,
  change,
  changeLabel = "from last month",
  icon: Icon,
}: KpiCardProps) {
  const isPositive = change !== undefined && change >= 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {change !== undefined && (
          <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
            {isPositive ? (
              <TrendingUp className="h-3 w-3 text-green-600" />
            ) : (
              <TrendingDown className="h-3 w-3 text-red-600" />
            )}
            <span
              className={cn(
                "font-medium",
                isPositive ? "text-green-600" : "text-red-600"
              )}
            >
              {isPositive ? "+" : ""}
              {change}%
            </span>{" "}
            {changeLabel}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
