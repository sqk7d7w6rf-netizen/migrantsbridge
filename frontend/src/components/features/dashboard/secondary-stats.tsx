"use client";

import { format } from "date-fns";
import { Calendar, AlertCircle, CheckCircle2, Star } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAppointments } from "@/hooks/queries/use-appointments";
import { useTasks } from "@/hooks/queries/use-tasks";
import { useKPIs } from "@/hooks/queries/use-reports";

const today = format(new Date(), "yyyy-MM-dd");

export function SecondaryStats() {
  const { data: appointmentsData, isLoading: appointmentsLoading } =
    useAppointments({ start_date: today, end_date: today });

  const { data: overdueData, isLoading: overdueLoading } = useTasks({
    due_before: today,
    status: "todo",
    page_size: 1,
  });

  const { data: kpis, isLoading: kpisLoading } = useKPIs();

  const stats = [
    {
      label: "Today's Appointments",
      value: appointmentsLoading
        ? null
        : (appointmentsData?.total ?? 0).toString(),
      icon: Calendar,
      iconColor: "text-blue-600",
      iconBg: "bg-blue-50",
      isLoading: appointmentsLoading,
    },
    {
      label: "Overdue Tasks",
      value: overdueLoading ? null : (overdueData?.total ?? 0).toString(),
      icon: AlertCircle,
      iconColor: "text-red-600",
      iconBg: "bg-red-50",
      isLoading: overdueLoading,
    },
    {
      label: "Cases Resolved (This Month)",
      value: kpisLoading
        ? null
        : (kpis?.cases_resolved ?? 0).toString(),
      icon: CheckCircle2,
      iconColor: "text-green-600",
      iconBg: "bg-green-50",
      isLoading: kpisLoading,
    },
    {
      label: "Satisfaction Rate",
      value: kpisLoading
        ? null
        : kpis?.satisfaction_rate
        ? `${kpis.satisfaction_rate}%`
        : "—",
      icon: Star,
      iconColor: "text-yellow-500",
      iconBg: "bg-yellow-50",
      isLoading: kpisLoading,
    },
  ];

  return (
    <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.label}>
          <CardContent className="pt-4 pb-4">
            <div className="flex items-center gap-4">
              <div
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${stat.iconBg}`}
              >
                <stat.icon className={`h-5 w-5 ${stat.iconColor}`} />
              </div>
              <div className="min-w-0">
                {stat.isLoading ? (
                  <>
                    <Skeleton className="h-6 w-12 mb-1" />
                    <Skeleton className="h-3 w-24" />
                  </>
                ) : (
                  <>
                    <p className="text-2xl font-bold leading-none">
                      {stat.value}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1 leading-tight">
                      {stat.label}
                    </p>
                  </>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
