"use client";

import { Users, FolderOpen, CheckSquare, DollarSign } from "lucide-react";
import { KpiCard } from "./kpi-card";
import { type DashboardKPIs } from "@/services/dashboard.service";
import { Skeleton } from "@/components/ui/skeleton";

interface KpiGridProps {
  data?: DashboardKPIs;
  isLoading?: boolean;
}

export function KpiGrid({ data, isLoading }: KpiGridProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-lg border p-6 space-y-3">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-3 w-32" />
          </div>
        ))}
      </div>
    );
  }

  const kpis = [
    {
      title: "Active Clients",
      value: data?.active_clients ?? 0,
      change: data?.active_clients_change ?? 0,
      icon: Users,
    },
    {
      title: "Active Cases",
      value: data?.active_cases ?? 0,
      change: data?.active_cases_change ?? 0,
      icon: FolderOpen,
    },
    {
      title: "Pending Tasks",
      value: data?.pending_tasks ?? 0,
      change: data?.pending_tasks_change ?? 0,
      icon: CheckSquare,
    },
    {
      title: "Monthly Revenue",
      value: `$${(data?.monthly_revenue ?? 0).toLocaleString()}`,
      change: data?.monthly_revenue_change ?? 0,
      icon: DollarSign,
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {kpis.map((kpi) => (
        <KpiCard key={kpi.title} {...kpi} />
      ))}
    </div>
  );
}
