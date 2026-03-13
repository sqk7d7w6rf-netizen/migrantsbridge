"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { ChartCard } from "./chart-card";
import { useClientGrowth } from "@/hooks/queries/use-reports";
import { Skeleton } from "@/components/ui/skeleton";
import { type DateRange } from "@/services/reports.service";

interface ClientGrowthChartProps {
  dateRange?: DateRange;
  onExport?: () => void;
}

export function ClientGrowthChart({
  dateRange,
  onExport,
}: ClientGrowthChartProps) {
  const { data, isLoading } = useClientGrowth(dateRange);

  return (
    <ChartCard
      title="Client Growth"
      description="New and total clients over time"
      onExport={onExport}
    >
      {isLoading ? (
        <Skeleton className="h-[300px] w-full" />
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data ?? []}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="month"
              className="text-xs"
              tick={{ fontSize: 12 }}
            />
            <YAxis className="text-xs" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="new_clients"
              stroke="hsl(221, 83%, 53%)"
              name="New Clients"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="total_clients"
              stroke="hsl(262, 83%, 58%)"
              name="Total Clients"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  );
}
