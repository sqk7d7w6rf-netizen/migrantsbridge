"use client";

import { useState } from "react";
import { useClientGrowth, useClientDemographics, useLanguageDistribution } from "@/hooks/queries/use-reports";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { ClientGrowthChart } from "@/components/features/reports/client-growth-chart";
import { ReportFilters } from "@/components/features/reports/report-filters";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { type DateRange } from "@/services/reports.service";
import {
  Users,
  UserPlus,
  Globe,
  Languages,
} from "lucide-react";

export default function ClientAnalyticsPage() {
  const [dateRange, setDateRange] = useState<DateRange>({});

  const { data: growthData, isLoading: growthLoading } = useClientGrowth(dateRange);
  const { data: demographics, isLoading: demoLoading } = useClientDemographics();
  const { data: languages, isLoading: langLoading } = useLanguageDistribution();

  const isLoading = growthLoading && demoLoading && langLoading;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Client Analytics"
          description="Client demographics and growth trends"
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

  const totalClients = growthData && growthData.length > 0
    ? growthData[growthData.length - 1].total_clients
    : 0;

  const newThisMonth = growthData && growthData.length > 0
    ? growthData[growthData.length - 1].new_clients
    : 0;

  const totalByNationality = demographics?.reduce((sum, d) => sum + d.count, 0) ?? 0;
  const totalByLanguage = languages?.reduce((sum, l) => sum + l.count, 0) ?? 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Client Analytics"
        description="Client demographics and growth trends"
      />

      <ReportFilters onDateRangeChange={handleDateRangeChange} />

      {/* Client Growth Chart */}
      <ClientGrowthChart dateRange={dateRange} />

      {/* Summary Stat Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Clients
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalClients.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground mt-1">All registered clients</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              New This Month
            </CardTitle>
            <UserPlus className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{newThisMonth.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground mt-1">Clients added this month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Nationalities
            </CardTitle>
            <Globe className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{demographics?.length ?? 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {totalByNationality.toLocaleString()} clients across nationalities
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Languages
            </CardTitle>
            <Languages className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{languages?.length ?? 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {totalByLanguage.toLocaleString()} clients across languages
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Breakdown Grids */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Nationality Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Globe className="h-4 w-4" />
              By Nationality
            </CardTitle>
          </CardHeader>
          <CardContent>
            {demographics && demographics.length > 0 ? (
              <div className="space-y-3">
                {demographics.map((item) => {
                  const percentage = totalByNationality > 0
                    ? ((item.count / totalByNationality) * 100).toFixed(1)
                    : "0";
                  return (
                    <div key={item.status} className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span className="capitalize">{item.status.replace(/_/g, " ")}</span>
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
              <p className="text-sm text-muted-foreground">No demographic data available.</p>
            )}
          </CardContent>
        </Card>

        {/* Language Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Languages className="h-4 w-4" />
              By Language
            </CardTitle>
          </CardHeader>
          <CardContent>
            {languages && languages.length > 0 ? (
              <div className="space-y-3">
                {languages.map((item) => {
                  const percentage = totalByLanguage > 0
                    ? ((item.count / totalByLanguage) * 100).toFixed(1)
                    : "0";
                  return (
                    <div key={item.language} className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span>{item.language}</span>
                        <span className="text-muted-foreground">
                          {item.count} ({percentage}%)
                        </span>
                      </div>
                      <div className="h-2 rounded-full bg-muted overflow-hidden">
                        <div
                          className="h-full rounded-full bg-blue-500 transition-all"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No language data available.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
