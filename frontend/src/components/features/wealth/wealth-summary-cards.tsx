"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  PiggyBank,
  TrendingUp,
  TrendingDown,
  Wallet,
  Target,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface WealthSummaryCardsProps {
  totalSavings: number;
  totalInvestments: number;
  netWorth: number;
  activeGoalsCount: number;
  savingsChange?: number;
  investmentsChange?: number;
  netWorthChange?: number;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

function ChangeIndicator({
  change,
  label,
}: {
  change?: number;
  label: string;
}) {
  if (change === undefined) return null;
  const isPositive = change >= 0;

  return (
    <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
      {isPositive ? (
        <TrendingUp className="h-3 w-3 text-green-600" />
      ) : (
        <TrendingDown className="h-3 w-3 text-red-600" />
      )}
      <span
        className={cn(
          "font-medium",
          isPositive ? "text-green-600" : "text-red-600"
        )}
      >
        {isPositive ? "+" : ""}
        {change}%
      </span>{" "}
      {label}
    </p>
  );
}

export function WealthSummaryCards({
  totalSavings,
  totalInvestments,
  netWorth,
  activeGoalsCount,
  savingsChange,
  investmentsChange,
  netWorthChange,
}: WealthSummaryCardsProps) {
  const cards = [
    {
      title: "Total Savings",
      value: formatCurrency(totalSavings),
      change: savingsChange,
      icon: PiggyBank,
    },
    {
      title: "Total Investments",
      value: formatCurrency(totalInvestments),
      change: investmentsChange,
      icon: TrendingUp,
    },
    {
      title: "Net Worth",
      value: formatCurrency(netWorth),
      change: netWorthChange,
      icon: Wallet,
    },
    {
      title: "Active Goals",
      value: activeGoalsCount,
      icon: Target,
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {card.title}
              </CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{card.value}</div>
              <ChangeIndicator
                change={card.change}
                label="from last month"
              />
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
