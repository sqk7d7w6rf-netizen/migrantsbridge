"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { wealthService, GoalCreate, GoalUpdate } from "@/services/wealth.service";
import { PaginationParams } from "@/types/api";
import { toast } from "sonner";

export function useWealthDashboard() {
  return useQuery({
    queryKey: [...queryKeys.wealth.all, "dashboard"],
    queryFn: () => wealthService.getDashboard(),
  });
}

export function useGoals(params?: PaginationParams & { status?: string }) {
  return useQuery({
    queryKey: [...queryKeys.wealth.goals(), params ?? {}],
    queryFn: () => wealthService.getGoals(params),
  });
}

export function useGoal(id: string) {
  return useQuery({
    queryKey: queryKeys.wealth.goal(id),
    queryFn: () => wealthService.getGoal(id),
    enabled: !!id,
  });
}

export function useGoalMilestones(goalId: string) {
  return useQuery({
    queryKey: [...queryKeys.wealth.goal(goalId), "milestones"],
    queryFn: () => wealthService.getGoalMilestones(goalId),
    enabled: !!goalId,
  });
}

export function useGoalTransactions(goalId: string) {
  return useQuery({
    queryKey: [...queryKeys.wealth.goal(goalId), "transactions"],
    queryFn: () => wealthService.getGoalTransactions(goalId),
    enabled: !!goalId,
  });
}

export function useCreateGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: GoalCreate) => wealthService.createGoal(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.wealth.goals() });
      queryClient.invalidateQueries({ queryKey: queryKeys.wealth.all });
      toast.success("Goal created successfully");
    },
    onError: () => {
      toast.error("Failed to create goal");
    },
  });
}

export function useUpdateGoal(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: GoalUpdate) =>
      wealthService.updateGoal(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.wealth.goals() });
      queryClient.invalidateQueries({ queryKey: queryKeys.wealth.goal(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.wealth.all });
      toast.success("Goal updated successfully");
    },
    onError: () => {
      toast.error("Failed to update goal");
    },
  });
}

export function useDeleteGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => wealthService.deleteGoal(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.wealth.goals() });
      queryClient.invalidateQueries({ queryKey: queryKeys.wealth.all });
      toast.success("Goal deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete goal");
    },
  });
}

export function useSavingsPrograms(params?: PaginationParams) {
  return useQuery({
    queryKey: [...queryKeys.wealth.savings(), params ?? {}],
    queryFn: () => wealthService.getSavingsPrograms(params),
  });
}

export function useCreateSavingsProgram() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: wealthService.createSavingsProgram,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.wealth.savings() });
      toast.success("Savings program created successfully");
    },
    onError: () => {
      toast.error("Failed to create savings program");
    },
  });
}

export function useInvestments(params?: PaginationParams) {
  return useQuery({
    queryKey: [...queryKeys.wealth.investments(), params ?? {}],
    queryFn: () => wealthService.getInvestments(params),
  });
}

export function useCreateInvestment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: wealthService.createInvestment,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.wealth.investments(),
      });
      toast.success("Investment recorded successfully");
    },
    onError: () => {
      toast.error("Failed to record investment");
    },
  });
}

export function useAssets(params?: PaginationParams) {
  return useQuery({
    queryKey: [...queryKeys.wealth.all, "assets", params ?? {}],
    queryFn: () => wealthService.getAssets(params),
  });
}

export function useCreateAsset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: wealthService.createAsset,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.wealth.all });
      toast.success("Asset recorded successfully");
    },
    onError: () => {
      toast.error("Failed to record asset");
    },
  });
}
