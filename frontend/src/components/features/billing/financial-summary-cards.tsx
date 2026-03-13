"use client";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { DollarSign, Clock, AlertTriangle, TrendingUp } from "lucide-react";
import { useFinancialSummary } from "@/hooks/queries/use-invoices";
import { Skeleton } from "@/components/ui/skeleton";

const formatCurrency = (amount: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);

export function FinancialSummaryCards() {
  const { data: summary, isLoading } = useFinancialSummary();

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-4" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const cards = [
    {
      title: "Total Revenue",
      value: formatCurrency(summary?.total_revenue ?? 0),
      description: `${summary?.paid_count ?? 0} invoices paid`,
      icon: DollarSign,
      iconColor: "text-green-600",
    },
    {
      title: "Outstanding",
      value: formatCurrency(summary?.total_outstanding ?? 0),
      description: `${summary?.invoice_count ?? 0} total invoices`,
      icon: Clock,
      iconColor: "text-blue-600",
    },
    {
      title: "Overdue",
      value: formatCurrency(summary?.total_overdue ?? 0),
      description: `${summary?.overdue_count ?? 0} invoices overdue`,
      icon: AlertTriangle,
      iconColor: "text-red-600",
    },
    {
      title: "Collected This Month",
      value: formatCurrency(summary?.collected_this_month ?? 0),
      description: "Current billing period",
      icon: TrendingUp,
      iconColor: "text-purple-600",
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {card.title}
            </CardTitle>
            <card.icon className={`h-4 w-4 ${card.iconColor}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {card.description}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
