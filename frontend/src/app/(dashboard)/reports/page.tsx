"use client";

import { useKPIs } from "@/hooks/queries/use-reports";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { CaseOutcomesChart } from "@/components/features/reports/case-outcomes-chart";
import { ClientGrowthChart } from "@/components/features/reports/client-growth-chart";
import { RevenueChart } from "@/components/features/reports/revenue-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import {
  Users,
  Briefcase,
  DollarSign,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  TrendingUp,
  BarChart3,
  PieChart,
} from "lucide-react";

export default function ReportsPage() {
  const { data: kpis, isLoading } = useKPIs();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Reports & Analytics"
          description="Overview of key metrics and trends"
        />
        <LoadingSkeleton variant="card" count={4} />
      </div>
    );
  }

  const kpiCards = [
    {
      title: "Total Clients",
      value: kpis?.total_clients ?? 0,
      change: kpis?.client_growth_pct ?? 0,
      icon: Users,
      href: "/reports/clients",
      format: (v: number) => v.toLocaleString(),
    },
    {
      title: "Active Cases",
      value: kpis?.active_cases ?? 0,
      change: null,
      icon: Briefcase,
      href: "/reports/cases",
      format: (v: number) => v.toLocaleString(),
    },
    {
      title: "Revenue MTD",
      value: kpis?.total_revenue ?? 0,
      change: kpis?.revenue_growth_pct ?? 0,
      icon: DollarSign,
      href: "/reports/financial",
      format: (v: number) =>
        new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: "USD",
          minimumFractionDigits: 0,
        }).format(v),
    },
    {
      title: "Avg Resolution Days",
      value: kpis?.avg_resolution_days ?? 0,
      change: null,
      icon: Clock,
      href: "/reports/cases",
      format: (v: number) => `${v.toFixed(1)} days`,
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Reports & Analytics"
        description="Overview of key metrics and trends"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" asChild>
              <Link href="/reports/clients">
                <PieChart className="mr-2 h-4 w-4" />
                Client Analytics
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/reports/cases">
                <BarChart3 className="mr-2 h-4 w-4" />
                Case Analytics
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/reports/financial">
                <TrendingUp className="mr-2 h-4 w-4" />
                Financial
              </Link>
            </Button>
          </div>
        }
      />

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {kpiCards.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <Link key={kpi.title} href={kpi.href}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {kpi.title}
                  </CardTitle>
                  <Icon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{kpi.format(kpi.value)}</div>
                  {kpi.change !== null && (
                    <p className="flex items-center text-xs text-muted-foreground mt-1">
                      {kpi.change >= 0 ? (
                        <ArrowUpRight className="mr-1 h-3 w-3 text-green-600" />
                      ) : (
                        <ArrowDownRight className="mr-1 h-3 w-3 text-red-600" />
                      )}
                      <span
                        className={
                          kpi.change >= 0 ? "text-green-600" : "text-red-600"
                        }
                      >
                        {Math.abs(kpi.change).toFixed(1)}%
                      </span>
                      <span className="ml-1">from last month</span>
                    </p>
                  )}
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        <CaseOutcomesChart />
        <ClientGrowthChart />
      </div>

      {/* Revenue Chart Full Width */}
      <RevenueChart />
    </div>
  );
}
