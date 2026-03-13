"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { ChartCard } from "./chart-card";
import { useRevenueTrend } from "@/hooks/queries/use-reports";
import { Skeleton } from "@/components/ui/skeleton";
import { type DateRange } from "@/services/reports.service";

interface RevenueChartProps {
  dateRange?: DateRange;
  onExport?: () => void;
}

export function RevenueChart({ dateRange, onExport }: RevenueChartProps) {
  const { data, isLoading } = useRevenueTrend(dateRange);

  return (
    <ChartCard
      title="Monthly Revenue"
      description="Revenue trends over time"
      onExport={onExport}
    >
      {isLoading ? (
        <Skeleton className="h-[300px] w-full" />
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data ?? []}>
            <defs>
              <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="hsl(142, 71%, 45%)"
                  stopOpacity={0.3}
                />
                <stop
                  offset="95%"
                  stopColor="hsl(142, 71%, 45%)"
                  stopOpacity={0}
                />
              </linearGradient>
              <linearGradient
                id="collectedGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop
                  offset="5%"
                  stopColor="hsl(221, 83%, 53%)"
                  stopOpacity={0.3}
                />
                <stop
                  offset="95%"
                  stopColor="hsl(221, 83%, 53%)"
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="month"
              className="text-xs"
              tick={{ fontSize: 12 }}
            />
            <YAxis
              className="text-xs"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              formatter={(value) =>
                new Intl.NumberFormat("en-US", {
                  style: "currency",
                  currency: "USD",
                }).format(Number(value))
              }
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="revenue"
              stroke="hsl(142, 71%, 45%)"
              fill="url(#revenueGradient)"
              name="Revenue"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="collected"
              stroke="hsl(221, 83%, 53%)"
              fill="url(#collectedGradient)"
              name="Collected"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  );
}
