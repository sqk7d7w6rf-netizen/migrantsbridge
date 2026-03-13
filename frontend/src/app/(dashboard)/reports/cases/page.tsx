"use client";

import { useState } from "react";
import {
  useCaseOutcomes,
  useCaseResolutionTimes,
  useCaseStatusDistribution,
} from "@/hooks/queries/use-reports";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { CaseOutcomesChart } from "@/components/features/reports/case-outcomes-chart";
import { ReportFilters } from "@/components/features/reports/report-filters";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { type DateRange } from "@/services/reports.service";
import { CASE_STATUSES } from "@/lib/constants";
import {
  Briefcase,
  CheckCircle2,
  Clock,
  Scale,
  FolderOpen,
  Timer,
} from "lucide-react";

export default function CaseAnalyticsPage() {
  const [dateRange, setDateRange] = useState<DateRange>({});

  const { data: outcomes, isLoading: outcomesLoading } = useCaseOutcomes(dateRange);
  const { data: resolutionTimes, isLoading: resolutionLoading } = useCaseResolutionTimes();
  const { data: statusDist, isLoading: statusLoading } = useCaseStatusDistribution();

  const isLoading = outcomesLoading && resolutionLoading && statusLoading;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Case Analytics"
          description="Case outcomes, resolution times, and status distribution"
        />
        <LoadingSkeleton variant="card" count={4} />
      </div>
    );
  }

  const handleDateRangeChange = (dateFrom: string, dateTo: string) => {
    setDateRange({
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
    });
  };

  const totalCases = statusDist?.reduce((sum, s) => sum + s.count, 0) ?? 0;
  const openCases = statusDist
    ?.filter((s) => !["closed", "approved", "denied"].includes(s.status))
    .reduce((sum, s) => sum + s.count, 0) ?? 0;
  const closedCases = statusDist
    ?.filter((s) => ["closed", "approved", "denied"].includes(s.status))
    .reduce((sum, s) => sum + s.count, 0) ?? 0;

  const avgResolution = resolutionTimes && resolutionTimes.length > 0
    ? resolutionTimes.reduce((sum, r) => sum + r.avg_days, 0) / resolutionTimes.length
    : 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Case Analytics"
        description="Case outcomes, resolution times, and status distribution"
      />

      <ReportFilters onDateRangeChange={handleDateRangeChange} />

      {/* Case Outcomes Chart */}
      <CaseOutcomesChart dateRange={dateRange} />

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Cases
            </CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalCases.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground mt-1">All cases in the system</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Open / Closed Ratio
            </CardTitle>
            <Scale className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {openCases} / {closedCases}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {totalCases > 0
                ? `${((openCases / totalCases) * 100).toFixed(0)}% open`
                : "No cases"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Avg Resolution Time
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgResolution.toFixed(1)} days</div>
            <p className="text-xs text-muted-foreground mt-1">
              Across all case types
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Case Types
            </CardTitle>
            <FolderOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{outcomes?.length ?? 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Distinct service categories
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Breakdowns */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Cases by Status */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" />
              Cases by Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            {statusDist && statusDist.length > 0 ? (
              <div className="space-y-3">
                {statusDist.map((item) => {
                  const percentage = totalCases > 0
                    ? ((item.count / totalCases) * 100).toFixed(1)
                    : "0";
                  const statusConfig = CASE_STATUSES[item.status as keyof typeof CASE_STATUSES];
                  const statusLabel = statusConfig?.label ?? item.status.replace(/_/g, " ");
                  const statusColor = statusConfig?.color ?? "bg-gray-100 text-gray-800";
                  return (
                    <div key={item.status} className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColor}`}
                        >
                          {statusLabel}
                        </span>
                        <span className="text-muted-foreground">
                          {item.count} ({percentage}%)
                        </span>
                      </div>
                      <div className="h-2 rounded-full bg-muted overflow-hidden">
                        <div
                          className="h-full rounded-full bg-primary transition-all"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No status data available.</p>
            )}
          </CardContent>
        </Card>

        {/* Cases by Type (Resolution Times) */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Timer className="h-4 w-4" />
              Resolution Times by Type
            </CardTitle>
          </CardHeader>
          <CardContent>
            {resolutionTimes && resolutionTimes.length > 0 ? (
              <div className="space-y-4">
                {resolutionTimes.map((item) => (
                  <div
                    key={item.case_type}
                    className="flex items-center justify-between"
                  >
                    <div>
                      <p className="text-sm font-medium">{item.case_type}</p>
                      <p className="text-xs text-muted-foreground">
                        Median: {item.median_days.toFixed(1)} days
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold">{item.avg_days.toFixed(1)}</p>
                      <p className="text-xs text-muted-foreground">avg days</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No resolution time data available.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
