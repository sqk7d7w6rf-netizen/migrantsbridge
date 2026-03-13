"use client";

import { useState } from "react";
import { useGoals, useCreateGoal } from "@/hooks/queries/use-wealth";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { GoalCard } from "@/components/features/wealth/goal-card";
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
import { Plus, Target } from "lucide-react";
import { FinancialGoal } from "@/types/goal";
import { GoalCreate } from "@/services/wealth.service";

const statusFilters = [
  { value: "all", label: "All Goals" },
  { value: "active", label: "Active" },
  { value: "completed", label: "Completed" },
  { value: "paused", label: "Paused" },
  { value: "cancelled", label: "Cancelled" },
];

const categoryOptions: { value: FinancialGoal["category"]; label: string }[] = [
  { value: "emergency_fund", label: "Emergency Fund" },
  { value: "education", label: "Education" },
  { value: "housing", label: "Housing" },
  { value: "business", label: "Business" },
  { value: "retirement", label: "Retirement" },
  { value: "other", label: "Other" },
];

export default function GoalsPage() {
  const [statusFilter, setStatusFilter] = useState("all");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState<GoalCreate>({
    name: "",
    description: "",
    target_amount: 0,
    target_date: "",
    category: "other",
  });

  const { data, isLoading } = useGoals(
    statusFilter === "all" ? undefined : { status: statusFilter }
  );
  const createGoal = useCreateGoal();

  const handleCreate = () => {
    if (!formData.name || !formData.target_amount || !formData.target_date) return;
    createGoal.mutate(formData, {
      onSuccess: () => {
        setDialogOpen(false);
        setFormData({
          name: "",
          description: "",
          target_amount: 0,
          target_date: "",
          category: "other",
        });
      },
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Financial Goals" description="Track your financial goals" />
        <LoadingSkeleton variant="card" count={4} />
      </div>
    );
  }

  const goals = data?.items ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Financial Goals"
        description="Track and manage financial goals"
        actions={
          <Button onClick={() => setDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Goal
          </Button>
        }
      />

      <div className="flex items-center gap-2">
        {statusFilters.map((filter) => (
          <Button
            key={filter.value}
            variant={statusFilter === filter.value ? "default" : "outline"}
            size="sm"
            onClick={() => setStatusFilter(filter.value)}
          >
            {filter.label}
          </Button>
        ))}
      </div>

      {goals.length === 0 ? (
        <EmptyState
          icon={Target}
          title="No goals found"
          description={
            statusFilter === "all"
              ? "Create your first financial goal to start tracking progress."
              : `No ${statusFilter} goals found.`
          }
          actionLabel="Create Goal"
          onAction={() => setDialogOpen(true)}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {goals.map((goal) => (
            <GoalCard key={goal.id} goal={goal} />
          ))}
        </div>
      )}

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create Financial Goal</DialogTitle>
            <DialogDescription>
              Set a new financial goal to track your progress.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="goal-name">Goal Name</Label>
              <Input
                id="goal-name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                placeholder="e.g., Emergency Fund"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="goal-desc">Description</Label>
              <Textarea
                id="goal-desc"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Describe your goal"
                rows={2}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="goal-amount">Target Amount ($)</Label>
                <Input
                  id="goal-amount"
                  type="number"
                  min={0}
                  value={formData.target_amount || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      target_amount: parseFloat(e.target.value) || 0,
                    })
                  }
                  placeholder="10000"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="goal-date">Target Date</Label>
                <Input
                  id="goal-date"
                  type="date"
                  value={formData.target_date}
                  onChange={(e) =>
                    setFormData({ ...formData, target_date: e.target.value })
                  }
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Category</Label>
              <Select
                value={formData.category}
                onValueChange={(value) =>
                  setFormData({
                    ...formData,
                    category: value as FinancialGoal["category"],
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categoryOptions.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleCreate}
              disabled={
                createGoal.isPending ||
                !formData.name ||
                !formData.target_amount ||
                !formData.target_date
              }
            >
              {createGoal.isPending ? "Creating..." : "Create Goal"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
