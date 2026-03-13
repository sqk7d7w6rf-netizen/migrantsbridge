"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { casesService } from "@/services/cases.service";
import { Case } from "@/types/case";
import { PaginationParams } from "@/types/api";
import { toast } from "sonner";

export function useCases(params?: PaginationParams & { client_id?: string }) {
  return useQuery({
    queryKey: queryKeys.cases.list((params || {}) as Record<string, unknown>),
    queryFn: () => casesService.getCases(params),
  });
}

export function useCase(id: string) {
  return useQuery({
    queryKey: queryKeys.cases.detail(id),
    queryFn: () => casesService.getCase(id),
    enabled: !!id,
  });
}

export function useCreateCase() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (
      payload: Omit<Case, "id" | "created_at" | "updated_at" | "case_number">
    ) => casesService.createCase(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.cases.all });
      toast.success("Case created successfully");
    },
    onError: () => {
      toast.error("Failed to create case");
    },
  });
}

export function useUpdateCase(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: Partial<Case>) =>
      casesService.updateCase(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.cases.all });
      queryClient.invalidateQueries({
        queryKey: queryKeys.cases.detail(id),
      });
      toast.success("Case updated successfully");
    },
    onError: () => {
      toast.error("Failed to update case");
    },
  });
}

export function useCaseNotes(caseId: string) {
  return useQuery({
    queryKey: [...queryKeys.cases.detail(caseId), "notes"],
    queryFn: () => casesService.getCaseNotes(caseId),
    enabled: !!caseId,
  });
}

export function useAddCaseNote(caseId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: { content: string; is_internal: boolean }) =>
      casesService.addCaseNote(caseId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [...queryKeys.cases.detail(caseId), "notes"],
      });
      toast.success("Note added successfully");
    },
    onError: () => {
      toast.error("Failed to add note");
    },
  });
}

export function useCaseHistory(caseId: string) {
  return useQuery({
    queryKey: [...queryKeys.cases.detail(caseId), "history"],
    queryFn: () => casesService.getCaseHistory(caseId),
    enabled: !!caseId,
  });
}
