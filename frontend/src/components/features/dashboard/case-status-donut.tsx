"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { ChartCard } from "@/components/features/reports/chart-card";
import { useCaseStatusDistribution } from "@/hooks/queries/use-reports";
import { Skeleton } from "@/components/ui/skeleton";

const STATUS_COLORS: Record<string, string> = {
  open: "hsl(221, 83%, 53%)",
  in_progress: "hsl(262, 83%, 58%)",
  pending_documents: "hsl(48, 96%, 53%)",
  under_review: "hsl(25, 95%, 53%)",
  approved: "hsl(142, 71%, 45%)",
  denied: "hsl(0, 84%, 60%)",
  closed: "hsl(215, 16%, 47%)",
};

function toTitleCase(str: string): string {
  return str
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function CaseStatusDonut() {
  const { data, isLoading } = useCaseStatusDistribution();

  const chartData = (data ?? []).map((item) => ({
    name: toTitleCase(item.status),
    value: item.count,
    status: item.status,
  }));

  return (
    <ChartCard
      title="Case Status Distribution"
      description="Active cases by current status"
    >
      {isLoading ? (
        <Skeleton className="h-[280px] w-full" />
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={chartData}
              innerRadius={65}
              outerRadius={105}
              paddingAngle={2}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={STATUS_COLORS[entry.status] ?? "hsl(215, 16%, 47%)"}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  );
}
