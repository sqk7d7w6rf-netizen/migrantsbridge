"use client";

import { PageHeader } from "@/components/layout/page-header";
import { KpiGrid } from "@/components/features/dashboard/kpi-grid";
import { SecondaryStats } from "@/components/features/dashboard/secondary-stats";
import { RecentActivityFeed } from "@/components/features/dashboard/recent-activity-feed";
import { QuickActions } from "@/components/features/dashboard/quick-actions";
import { TodayAppointments } from "@/components/features/dashboard/today-appointments";
import { UrgentTasks } from "@/components/features/dashboard/urgent-tasks";
import { CaseStatusDonut } from "@/components/features/dashboard/case-status-donut";
import { RevenueChart } from "@/components/features/reports/revenue-chart";
import { ClientGrowthChart } from "@/components/features/reports/client-growth-chart";
import { CaseOutcomesChart } from "@/components/features/reports/case-outcomes-chart";
import { useDashboardKPIs, useRecentActivity } from "@/hooks/queries/use-dashboard";

export default function DashboardPage() {
  const { data: kpis, isLoading: kpisLoading } = useDashboardKPIs();
  const { data: activity, isLoading: activityLoading } = useRecentActivity();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="Overview of your organization's operations"
        showBreadcrumbs={false}
      />

      <KpiGrid data={kpis} isLoading={kpisLoading} />

      <SecondaryStats />

      <div className="grid gap-6 lg:grid-cols-2">
        <RevenueChart />
        <ClientGrowthChart />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <CaseStatusDonut />
        <CaseOutcomesChart />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <TodayAppointments />
        <UrgentTasks />
        <RecentActivityFeed data={activity} isLoading={activityLoading} />
      </div>

      <QuickActions />
    </div>
  );
}
