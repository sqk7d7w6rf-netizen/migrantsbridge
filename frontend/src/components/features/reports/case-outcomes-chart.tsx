"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { ChartCard } from "./chart-card";
import { useCaseOutcomes } from "@/hooks/queries/use-reports";
import { Skeleton } from "@/components/ui/skeleton";
import { type DateRange } from "@/services/reports.service";

interface CaseOutcomesChartProps {
  dateRange?: DateRange;
  onExport?: () => void;
}

export function CaseOutcomesChart({
  dateRange,
  onExport,
}: CaseOutcomesChartProps) {
  const { data, isLoading } = useCaseOutcomes(dateRange);

  return (
    <ChartCard
      title="Case Outcomes by Type"
      description="Breakdown of case resolutions across service types"
      onExport={onExport}
    >
      {isLoading ? (
        <Skeleton className="h-[300px] w-full" />
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data ?? []}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="case_type"
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
            <Bar
              dataKey="approved"
              fill="hsl(142, 71%, 45%)"
              name="Approved"
              radius={[4, 4, 0, 0]}
            />
            <Bar
              dataKey="denied"
              fill="hsl(0, 84%, 60%)"
              name="Denied"
              radius={[4, 4, 0, 0]}
            />
            <Bar
              dataKey="pending"
              fill="hsl(48, 96%, 53%)"
              name="Pending"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  );
}
