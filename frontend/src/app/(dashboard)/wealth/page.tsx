"use client";

import { useWealthDashboard } from "@/hooks/queries/use-wealth";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { WealthSummaryCards } from "@/components/features/wealth/wealth-summary-cards";
import { SavingsChart } from "@/components/features/wealth/savings-chart";
import { InvestmentAllocationChart } from "@/components/features/wealth/investment-allocation-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

export default function WealthDashboardPage() {
  const { data, isLoading } = useWealthDashboard();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Wealth Creation"
          description="Track savings, investments, and financial goals"
        />
        <LoadingSkeleton variant="card" count={4} />
      </div>
    );
  }

  const dashboard = data;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Wealth Creation"
        description="Track savings, investments, and financial goals"
      />

      <WealthSummaryCards
        totalSavings={dashboard?.total_savings ?? 0}
        totalInvestments={dashboard?.total_investments ?? 0}
        netWorth={dashboard?.net_worth ?? 0}
        activeGoalsCount={dashboard?.active_goals_count ?? 0}
        savingsChange={dashboard?.savings_change}
        investmentsChange={dashboard?.investments_change}
        netWorthChange={dashboard?.net_worth_change}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <SavingsChart data={dashboard?.savings_history ?? []} />
        <InvestmentAllocationChart
          data={dashboard?.investment_allocation ?? []}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Recent Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          {!dashboard?.recent_transactions ||
          dashboard.recent_transactions.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No recent transactions
            </p>
          ) : (
            <div className="space-y-3">
              {dashboard.recent_transactions.map((tx) => (
                <div
                  key={tx.id}
                  className="flex items-center justify-between rounded-md border px-4 py-3"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={cn(
                        "h-2 w-2 rounded-full",
                        tx.type === "credit" ? "bg-green-500" : "bg-red-500"
                      )}
                    />
                    <div>
                      <p className="text-sm font-medium">{tx.description}</p>
                      <p className="text-xs text-muted-foreground">
                        {format(new Date(tx.date), "MMM d, yyyy")}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      {tx.category}
                    </Badge>
                    <span
                      className={cn(
                        "text-sm font-semibold",
                        tx.type === "credit"
                          ? "text-green-600"
                          : "text-red-600"
                      )}
                    >
                      {tx.type === "credit" ? "+" : "-"}
                      {formatCurrency(Math.abs(tx.amount))}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
