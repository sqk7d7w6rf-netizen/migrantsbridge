"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  useGoal,
  useUpdateGoal,
  useDeleteGoal,
  useGoalMilestones,
  useGoalTransactions,
} from "@/hooks/queries/use-wealth";
import { PageHeader } from "@/components/layout/page-header";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { GoalProgressRing } from "@/components/features/wealth/goal-progress-ring";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  CalendarDays,
  Pencil,
  Trash2,
  CheckCircle2,
  Circle,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { FinancialGoal } from "@/types/goal";
import { GoalUpdate } from "@/services/wealth.service";

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

const categoryLabels: Record<FinancialGoal["category"], string> = {
  emergency_fund: "Emergency Fund",
  education: "Education",
  housing: "Housing",
  business: "Business",
  retirement: "Retirement",
  other: "Other",
};

const statusOptions: { value: FinancialGoal["status"]; label: string }[] = [
  { value: "active", label: "Active" },
  { value: "completed", label: "Completed" },
  { value: "paused", label: "Paused" },
  { value: "cancelled", label: "Cancelled" },
];

export default function GoalDetailPage() {
  const params = useParams();
  const router = useRouter();
  const goalId = params.goalId as string;

  const { data: goal, isLoading } = useGoal(goalId);
  const { data: milestones } = useGoalMilestones(goalId);
  const { data: transactions } = useGoalTransactions(goalId);
  const updateGoal = useUpdateGoal(goalId);
  const deleteGoal = useDeleteGoal();

  const [isEditing, setIsEditing] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [editForm, setEditForm] = useState<GoalUpdate>({});

  const startEditing = () => {
    if (!goal) return;
    setEditForm({
      name: goal.name,
      description: goal.description,
      target_amount: goal.target_amount,
      target_date: goal.target_date,
      status: goal.status,
    });
    setIsEditing(true);
  };

  const handleSave = () => {
    updateGoal.mutate(editForm, {
      onSuccess: () => setIsEditing(false),
    });
  };

  const handleDelete = () => {
    deleteGoal.mutate(goalId, {
      onSuccess: () => router.push("/wealth/goals"),
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Goal Details" />
        <LoadingSkeleton variant="detail" />
      </div>
    );
  }

  if (!goal) {
    return (
      <div className="space-y-6">
        <PageHeader title="Goal Not Found" />
        <p className="text-sm text-muted-foreground">
          The requested goal could not be found.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={goal.name}
        description={goal.description}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={startEditing}>
              <Pencil className="mr-2 h-4 w-4" />
              Edit
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={() => setDeleteOpen(true)}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </Button>
          </div>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardContent className="flex flex-col items-center pt-6">
            <GoalProgressRing
              percentage={goal.progress_percentage}
              size={140}
            />
            <div className="mt-4 text-center space-y-1">
              <p className="text-lg font-bold">
                {formatCurrency(goal.current_amount)}
              </p>
              <p className="text-sm text-muted-foreground">
                of {formatCurrency(goal.target_amount)}
              </p>
            </div>
            <div className="mt-4 flex items-center gap-2">
              <Badge variant="outline">
                {categoryLabels[goal.category]}
              </Badge>
              <Badge
                className={cn(
                  goal.status === "active" && "bg-green-100 text-green-800",
                  goal.status === "completed" && "bg-blue-100 text-blue-800",
                  goal.status === "paused" && "bg-yellow-100 text-yellow-800",
                  goal.status === "cancelled" && "bg-red-100 text-red-800"
                )}
              >
                {goal.status}
              </Badge>
            </div>
            <div className="mt-3 flex items-center gap-1 text-xs text-muted-foreground">
              <CalendarDays className="h-3 w-3" />
              Target: {format(new Date(goal.target_date), "MMM d, yyyy")}
            </div>
          </CardContent>
        </Card>

        <div className="lg:col-span-2">
          {isEditing ? (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Edit Goal</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Name</Label>
                  <Input
                    value={editForm.name || ""}
                    onChange={(e) =>
                      setEditForm({ ...editForm, name: e.target.value })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label>Description</Label>
                  <Textarea
                    value={editForm.description || ""}
                    onChange={(e) =>
                      setEditForm({
                        ...editForm,
                        description: e.target.value,
                      })
                    }
                    rows={2}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Target Amount ($)</Label>
                    <Input
                      type="number"
                      value={editForm.target_amount || ""}
                      onChange={(e) =>
                        setEditForm({
                          ...editForm,
                          target_amount: parseFloat(e.target.value) || 0,
                        })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Target Date</Label>
                    <Input
                      type="date"
                      value={editForm.target_date || ""}
                      onChange={(e) =>
                        setEditForm({
                          ...editForm,
                          target_date: e.target.value,
                        })
                      }
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Status</Label>
                  <Select
                    value={editForm.status}
                    onValueChange={(value) =>
                      setEditForm({
                        ...editForm,
                        status: value as FinancialGoal["status"],
                      })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {statusOptions.map((opt) => (
                        <SelectItem key={opt.value} value={opt.value}>
                          {opt.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex gap-2">
                  <Button onClick={handleSave} disabled={updateGoal.isPending}>
                    {updateGoal.isPending ? "Saving..." : "Save Changes"}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setIsEditing(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Tabs defaultValue="transactions">
              <TabsList>
                <TabsTrigger value="transactions">Transactions</TabsTrigger>
                <TabsTrigger value="milestones">Milestones</TabsTrigger>
              </TabsList>

              <TabsContent value="transactions">
                <Card>
                  <CardContent className="pt-6">
                    {!transactions || transactions.length === 0 ? (
                      <p className="text-sm text-muted-foreground text-center py-8">
                        No transactions recorded for this goal.
                      </p>
                    ) : (
                      <div className="space-y-2">
                        {transactions.map((tx) => (
                          <div
                            key={tx.id}
                            className="flex items-center justify-between rounded-md border px-4 py-3"
                          >
                            <div className="flex items-center gap-3">
                              {tx.type === "deposit" ? (
                                <ArrowUpRight className="h-4 w-4 text-green-600" />
                              ) : (
                                <ArrowDownRight className="h-4 w-4 text-red-600" />
                              )}
                              <div>
                                <p className="text-sm font-medium capitalize">
                                  {tx.type}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                  {format(new Date(tx.date), "MMM d, yyyy")}
                                </p>
                              </div>
                            </div>
                            <span
                              className={cn(
                                "text-sm font-semibold",
                                tx.type === "deposit"
                                  ? "text-green-600"
                                  : "text-red-600"
                              )}
                            >
                              {tx.type === "deposit" ? "+" : "-"}
                              {formatCurrency(tx.amount)}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="milestones">
                <Card>
                  <CardContent className="pt-6">
                    {!milestones || milestones.length === 0 ? (
                      <p className="text-sm text-muted-foreground text-center py-8">
                        No milestones set for this goal.
                      </p>
                    ) : (
                      <div className="space-y-3">
                        {milestones.map((milestone) => (
                          <div
                            key={milestone.id}
                            className="flex items-center gap-3 rounded-md border px-4 py-3"
                          >
                            {milestone.is_reached ? (
                              <CheckCircle2 className="h-5 w-5 text-green-600 shrink-0" />
                            ) : (
                              <Circle className="h-5 w-5 text-muted-foreground shrink-0" />
                            )}
                            <div className="flex-1 min-w-0">
                              <p
                                className={cn(
                                  "text-sm font-medium",
                                  milestone.is_reached &&
                                    "line-through text-muted-foreground"
                                )}
                              >
                                {milestone.title}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                Target: {formatCurrency(milestone.target_amount)}
                                {milestone.reached_at &&
                                  ` - Reached ${format(new Date(milestone.reached_at), "MMM d, yyyy")}`}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          )}
        </div>
      </div>

      <ConfirmDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        title="Delete Goal"
        description="Are you sure you want to delete this goal? This action cannot be undone."
        confirmLabel="Delete"
        variant="destructive"
        onConfirm={handleDelete}
        loading={deleteGoal.isPending}
      />
    </div>
  );
}
