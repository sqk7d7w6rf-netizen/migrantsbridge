"use client";

import { PageHeader } from "@/components/layout/page-header";
import { KpiGrid } from "@/components/features/dashboard/kpi-grid";
import { RecentActivityFeed } from "@/components/features/dashboard/recent-activity-feed";
import { QuickActions } from "@/components/features/dashboard/quick-actions";
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

      <div className="grid gap-6 md:grid-cols-2">
        <RecentActivityFeed data={activity} isLoading={activityLoading} />
        <QuickActions />
      </div>
    </div>
  );
}
