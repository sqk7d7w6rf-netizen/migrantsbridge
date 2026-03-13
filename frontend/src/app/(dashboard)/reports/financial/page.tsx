"use client";

import { useState } from "react";
import { useRevenueTrend, useBillingStatusBreakdown, useTopServices } from "@/hooks/queries/use-reports";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { RevenueChart } from "@/components/features/reports/revenue-chart";
import { ReportFilters } from "@/components/features/reports/report-filters";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { type DateRange } from "@/services/reports.service";
import {
  DollarSign,
  CreditCard,
  AlertCircle,
  Receipt,
  TrendingUp,
  Star,
} from "lucide-react";

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
  }).format(value);

const BILLING_STATUS_COLORS: Record<string, string> = {
  paid: "bg-green-500",
  sent: "bg-blue-500",
  overdue: "bg-red-500",
  draft: "bg-gray-400",
  cancelled: "bg-gray-300",
};

export default function FinancialReportsPage() {
  const [dateRange, setDateRange] = useState<DateRange>({});

  const { data: revenueData, isLoading: revenueLoading } = useRevenueTrend(dateRange);
  const { data: billingStatus, isLoading: billingLoading } = useBillingStatusBreakdown();
  const { data: topServices, isLoading: servicesLoading } = useTopServices();

  const isLoading = revenueLoading && billingLoading && servicesLoading;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Financial Reports"
          description="Revenue trends and billing analytics"
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

  const totalRevenue = revenueData?.reduce((sum, d) => sum + d.revenue, 0) ?? 0;
  const totalCollected = revenueData?.reduce((sum, d) => sum + d.collected, 0) ?? 0;
  const totalOutstanding = revenueData?.reduce((sum, d) => sum + d.outstanding, 0) ?? 0;

  const totalInvoices = billingStatus?.reduce((sum, b) => sum + b.count, 0) ?? 0;
  const avgInvoice = totalInvoices > 0
    ? (billingStatus?.reduce((sum, b) => sum + b.total_amount, 0) ?? 0) / totalInvoices
    : 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Financial Reports"
        description="Revenue trends and billing analytics"
      />

      <ReportFilters onDateRangeChange={handleDateRangeChange} />

      {/* Revenue Chart */}
      <RevenueChart dateRange={dateRange} />

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Revenue
            </CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(totalRevenue)}</div>
            <p className="text-xs text-muted-foreground mt-1">All invoiced revenue</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Collected
            </CardTitle>
            <CreditCard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(totalCollected)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Successfully collected</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Outstanding
            </CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {formatCurrency(totalOutstanding)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Pending collection</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Average Invoice
            </CardTitle>
            <Receipt className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(avgInvoice)}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Across {totalInvoices.toLocaleString()} invoices
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Billing Status & Top Services */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Billing Status Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <CreditCard className="h-4 w-4" />
              Billing Status Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            {billingStatus && billingStatus.length > 0 ? (
              <div className="space-y-4">
                {billingStatus.map((item) => {
                  const percentage = totalInvoices > 0
                    ? ((item.count / totalInvoices) * 100).toFixed(1)
                    : "0";
                  const colorClass = BILLING_STATUS_COLORS[item.status] ?? "bg-gray-400";
                  return (
                    <div key={item.status} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className={`h-3 w-3 rounded-full ${colorClass}`} />
                          <span className="text-sm font-medium capitalize">
                            {item.status}
                          </span>
                        </div>
                        <div className="text-right">
                          <span className="text-sm font-medium">
                            {item.count} invoices
                          </span>
                          <span className="text-xs text-muted-foreground ml-2">
                            ({percentage}%)
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>Total: {formatCurrency(item.total_amount)}</span>
                      </div>
                      <div className="h-2 rounded-full bg-muted overflow-hidden">
                        <div
                          className={`h-full rounded-full ${colorClass} transition-all`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No billing data available.</p>
            )}
          </CardContent>
        </Card>

        {/* Top Services */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Star className="h-4 w-4" />
              Top Services
            </CardTitle>
          </CardHeader>
          <CardContent>
            {topServices && topServices.length > 0 ? (
              <div className="space-y-4">
                {topServices.map((service, index) => (
                  <div
                    key={service.service_name}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <span className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                        {index + 1}
                      </span>
                      <div>
                        <p className="text-sm font-medium">{service.service_name}</p>
                        <p className="text-xs text-muted-foreground">
                          {service.count} engagements
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">
                        {formatCurrency(service.revenue)}
                      </p>
                      <p className="text-xs text-muted-foreground flex items-center justify-end gap-1">
                        <TrendingUp className="h-3 w-3" />
                        revenue
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No service data available.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
