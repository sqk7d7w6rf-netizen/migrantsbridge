"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import {
  workflowsService,
  WorkflowCreate,
  WorkflowUpdate,
  WorkflowGenerateRequest,
  WorkflowExecuteRequest,
} from "@/services/workflows.service";
import { PaginationParams } from "@/types/api";
import { toast } from "sonner";

export function useWorkflows(
  params?: PaginationParams & { is_template?: boolean }
) {
  return useQuery({
    queryKey: queryKeys.workflows.list((params || {}) as Record<string, unknown>),
    queryFn: () => workflowsService.getWorkflows(params),
  });
}

export function useWorkflow(id: string) {
  return useQuery({
    queryKey: queryKeys.workflows.detail(id),
    queryFn: () => workflowsService.getWorkflow(id),
    enabled: !!id,
  });
}

export function useCreateWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: WorkflowCreate) =>
      workflowsService.createWorkflow(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workflows.all });
      toast.success("Workflow created successfully");
    },
    onError: () => {
      toast.error("Failed to create workflow");
    },
  });
}

export function useUpdateWorkflow(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: WorkflowUpdate) =>
      workflowsService.updateWorkflow(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workflows.all });
      queryClient.invalidateQueries({
        queryKey: queryKeys.workflows.detail(id),
      });
      toast.success("Workflow updated successfully");
    },
    onError: () => {
      toast.error("Failed to update workflow");
    },
  });
}

export function useDeleteWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => workflowsService.deleteWorkflow(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workflows.all });
      toast.success("Workflow deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete workflow");
    },
  });
}

export function useGenerateWorkflow() {
  return useMutation({
    mutationFn: (payload: WorkflowGenerateRequest) =>
      workflowsService.generateWorkflow(payload),
    onSuccess: () => {
      toast.success("Workflow generated successfully");
    },
    onError: () => {
      toast.error("Failed to generate workflow");
    },
  });
}

export function useExecuteWorkflow(workflowId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload?: WorkflowExecuteRequest) =>
      workflowsService.executeWorkflow(workflowId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.workflows.detail(workflowId),
      });
      toast.success("Workflow execution started");
    },
    onError: () => {
      toast.error("Failed to execute workflow");
    },
  });
}

export function useWorkflowExecutions(
  workflowId: string,
  params?: PaginationParams
) {
  return useQuery({
    queryKey: [
      ...queryKeys.workflows.detail(workflowId),
      "executions",
      params ?? {},
    ],
    queryFn: () => workflowsService.getExecutions(workflowId, params),
    enabled: !!workflowId,
  });
}

export function useWorkflowTemplates() {
  return useQuery({
    queryKey: [...queryKeys.workflows.all, "templates"],
    queryFn: () => workflowsService.getTemplates(),
  });
}

export function useCloneTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (templateId: string) =>
      workflowsService.cloneTemplate(templateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workflows.all });
      toast.success("Workflow created from template");
    },
    onError: () => {
      toast.error("Failed to clone template");
    },
  });
}
