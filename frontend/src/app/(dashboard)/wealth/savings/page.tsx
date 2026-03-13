"use client";

import { useState } from "react";
import {
  useSavingsPrograms,
  useCreateSavingsProgram,
} from "@/hooks/queries/use-wealth";
import { PageHeader } from "@/components/layout/page-header";
import { DataTable } from "@/components/shared/data-table/data-table";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import { SavingsProgram } from "@/types/goal";
import { SavingsProgramCreate } from "@/services/wealth.service";
import { format } from "date-fns";
import { Plus, PiggyBank } from "lucide-react";

const savingsStatusMap: Record<string, { label: string; color: string }> = {
  true: { label: "Active", color: "bg-green-100 text-green-800" },
  false: { label: "Inactive", color: "bg-gray-100 text-gray-800" },
};

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

const columns: ColumnDef<SavingsProgram>[] = [
  {
    accessorKey: "name",
    header: "Program Name",
    cell: ({ row }) => (
      <span className="font-medium">{row.getValue("name")}</span>
    ),
  },
  {
    accessorKey: "contribution_amount",
    header: "Contribution",
    cell: ({ row }) =>
      formatCurrency(row.getValue("contribution_amount")),
  },
  {
    accessorKey: "frequency",
    header: "Frequency",
    cell: ({ row }) => (
      <span className="capitalize">{row.getValue("frequency")}</span>
    ),
  },
  {
    accessorKey: "total_saved",
    header: "Total Saved",
    cell: ({ row }) => (
      <span className="font-semibold text-green-600">
        {formatCurrency(row.getValue("total_saved"))}
      </span>
    ),
  },
  {
    accessorKey: "start_date",
    header: "Start Date",
    cell: ({ row }) =>
      format(new Date(row.getValue("start_date")), "MMM d, yyyy"),
  },
  {
    accessorKey: "is_active",
    header: "Status",
    cell: ({ row }) => (
      <StatusBadge
        status={String(row.getValue("is_active"))}
        statusMap={savingsStatusMap}
      />
    ),
  },
];

export default function SavingsPage() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState<Omit<SavingsProgramCreate, "client_id">>({
    name: "",
    contribution_amount: 0,
    frequency: "monthly",
    start_date: "",
  });

  const { data, isLoading } = useSavingsPrograms();
  const createProgram = useCreateSavingsProgram();

  const handleCreate = () => {
    if (!formData.name || !formData.contribution_amount || !formData.start_date)
      return;
    createProgram.mutate(
      { ...formData, client_id: "" } as SavingsProgramCreate,
      {
        onSuccess: () => {
          setDialogOpen(false);
          setFormData({
            name: "",
            contribution_amount: 0,
            frequency: "monthly",
            start_date: "",
          });
        },
      }
    );
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Savings Programs"
          description="Manage savings programs and contributions"
        />
        <LoadingSkeleton variant="table" />
      </div>
    );
  }

  const programs = data?.items ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Savings Programs"
        description="Manage savings programs and contributions"
        actions={
          <Button onClick={() => setDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Program
          </Button>
        }
      />

      {programs.length === 0 ? (
        <EmptyState
          icon={PiggyBank}
          title="No savings programs"
          description="Create a savings program to start building wealth systematically."
          actionLabel="Create Program"
          onAction={() => setDialogOpen(true)}
        />
      ) : (
        <DataTable columns={columns} data={programs} />
      )}

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-[450px]">
          <DialogHeader>
            <DialogTitle>Create Savings Program</DialogTitle>
            <DialogDescription>
              Set up a new recurring savings program.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="prog-name">Program Name</Label>
              <Input
                id="prog-name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                placeholder="e.g., Weekly Emergency Fund"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="prog-amount">Contribution ($)</Label>
                <Input
                  id="prog-amount"
                  type="number"
                  min={0}
                  value={formData.contribution_amount || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      contribution_amount: parseFloat(e.target.value) || 0,
                    })
                  }
                  placeholder="100"
                />
              </div>
              <div className="space-y-2">
                <Label>Frequency</Label>
                <Select
                  value={formData.frequency}
                  onValueChange={(value) =>
                    setFormData({
                      ...formData,
                      frequency: value as SavingsProgramCreate["frequency"],
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="biweekly">Biweekly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="prog-start">Start Date</Label>
              <Input
                id="prog-start"
                type="date"
                value={formData.start_date}
                onChange={(e) =>
                  setFormData({ ...formData, start_date: e.target.value })
                }
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
                createProgram.isPending ||
                !formData.name ||
                !formData.contribution_amount ||
                !formData.start_date
              }
            >
              {createProgram.isPending ? "Creating..." : "Create Program"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
