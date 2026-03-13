"use client";

import { useState } from "react";
import { useInvestments, useCreateInvestment } from "@/hooks/queries/use-wealth";
import { PageHeader } from "@/components/layout/page-header";
import { DataTable } from "@/components/shared/data-table/data-table";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { InvestmentAllocationChart } from "@/components/features/wealth/investment-allocation-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { type ColumnDef } from "@tanstack/react-table";
import { Investment } from "@/types/goal";
import { InvestmentCreate } from "@/services/wealth.service";
import { format } from "date-fns";
import { Plus, TrendingUp, Wallet } from "lucide-react";
import { cn } from "@/lib/utils";

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

const typeLabels: Record<Investment["type"], string> = {
  stocks: "Stocks",
  bonds: "Bonds",
  mutual_fund: "Mutual Fund",
  savings_account: "Savings Account",
  cd: "Certificate of Deposit",
  other: "Other",
};

const columns: ColumnDef<Investment>[] = [
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => (
      <span className="font-medium">{row.getValue("name")}</span>
    ),
  },
  {
    accessorKey: "type",
    header: "Type",
    cell: ({ row }) =>
      typeLabels[row.getValue("type") as Investment["type"]] ||
      row.getValue("type"),
  },
  {
    accessorKey: "amount_invested",
    header: "Invested",
    cell: ({ row }) => formatCurrency(row.getValue("amount_invested")),
  },
  {
    accessorKey: "current_value",
    header: "Current Value",
    cell: ({ row }) => (
      <span className="font-semibold">
        {formatCurrency(row.getValue("current_value"))}
      </span>
    ),
  },
  {
    accessorKey: "return_rate",
    header: "Return",
    cell: ({ row }) => {
      const rate = row.getValue("return_rate") as number;
      return (
        <span
          className={cn(
            "font-medium",
            rate >= 0 ? "text-green-600" : "text-red-600"
          )}
        >
          {rate >= 0 ? "+" : ""}
          {rate.toFixed(1)}%
        </span>
      );
    },
  },
  {
    accessorKey: "start_date",
    header: "Start Date",
    cell: ({ row }) =>
      format(new Date(row.getValue("start_date")), "MMM d, yyyy"),
  },
];

export default function InvestmentsPage() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState<Omit<InvestmentCreate, "client_id">>({
    name: "",
    type: "stocks",
    amount_invested: 0,
    start_date: "",
    notes: "",
  });

  const { data, isLoading } = useInvestments();
  const createInvestment = useCreateInvestment();

  const investments = data?.items ?? [];

  const totalPortfolioValue = investments.reduce(
    (sum, inv) => sum + inv.current_value,
    0
  );

  const allocationData = Object.entries(
    investments.reduce(
      (acc, inv) => {
        acc[inv.type] = (acc[inv.type] || 0) + inv.current_value;
        return acc;
      },
      {} as Record<string, number>
    )
  ).map(([type, value]) => ({
    type,
    value,
    percentage: totalPortfolioValue > 0 ? (value / totalPortfolioValue) * 100 : 0,
  }));

  const handleCreate = () => {
    if (!formData.name || !formData.amount_invested || !formData.start_date) return;
    createInvestment.mutate(
      { ...formData, client_id: "" } as InvestmentCreate,
      {
        onSuccess: () => {
          setDialogOpen(false);
          setFormData({
            name: "",
            type: "stocks",
            amount_invested: 0,
            start_date: "",
            notes: "",
          });
        },
      }
    );
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Investments" description="Manage investment records" />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Investments"
        description="Manage investment records and track portfolio performance"
        actions={
          <Button onClick={() => setDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Record Investment
          </Button>
        }
      />

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Portfolio Value
            </CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(totalPortfolioValue)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Across {investments.length} investment{investments.length !== 1 ? "s" : ""}
            </p>
          </CardContent>
        </Card>
        <InvestmentAllocationChart data={allocationData} />
      </div>

      {investments.length === 0 ? (
        <EmptyState
          icon={TrendingUp}
          title="No investments recorded"
          description="Start recording investments to track your portfolio performance."
          actionLabel="Record Investment"
          onAction={() => setDialogOpen(true)}
        />
      ) : (
        <DataTable columns={columns} data={investments} />
      )}

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-[450px]">
          <DialogHeader>
            <DialogTitle>Record Investment</DialogTitle>
            <DialogDescription>
              Add a new investment to the portfolio.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="inv-name">Investment Name</Label>
              <Input
                id="inv-name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                placeholder="e.g., S&P 500 Index Fund"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Type</Label>
                <Select
                  value={formData.type}
                  onValueChange={(value) =>
                    setFormData({
                      ...formData,
                      type: value as Investment["type"],
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="stocks">Stocks</SelectItem>
                    <SelectItem value="bonds">Bonds</SelectItem>
                    <SelectItem value="mutual_fund">Mutual Fund</SelectItem>
                    <SelectItem value="savings_account">
                      Savings Account
                    </SelectItem>
                    <SelectItem value="cd">Certificate of Deposit</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="inv-amount">Amount ($)</Label>
                <Input
                  id="inv-amount"
                  type="number"
                  min={0}
                  value={formData.amount_invested || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      amount_invested: parseFloat(e.target.value) || 0,
                    })
                  }
                  placeholder="5000"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="inv-date">Start Date</Label>
              <Input
                id="inv-date"
                type="date"
                value={formData.start_date}
                onChange={(e) =>
                  setFormData({ ...formData, start_date: e.target.value })
                }
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="inv-notes">Notes</Label>
              <Textarea
                id="inv-notes"
                value={formData.notes}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
                placeholder="Optional notes"
                rows={2}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleCreate}
              disabled={
                createInvestment.isPending ||
                !formData.name ||
                !formData.amount_invested ||
                !formData.start_date
              }
            >
              {createInvestment.isPending ? "Recording..." : "Record Investment"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
