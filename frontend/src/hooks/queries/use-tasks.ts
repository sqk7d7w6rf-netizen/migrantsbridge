"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import {
  tasksService,
  TaskCreate,
  TaskUpdate,
  TaskFilters,
} from "@/services/tasks.service";
import { toast } from "sonner";

export function useTasks(params?: TaskFilters) {
  return useQuery({
    queryKey: queryKeys.tasks.list(
      (params || {}) as Record<string, unknown>
    ),
    queryFn: () => tasksService.getTasks(params),
  });
}

export function useTask(id: string) {
  return useQuery({
    queryKey: queryKeys.tasks.detail(id),
    queryFn: () => tasksService.getTask(id),
    enabled: !!id,
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: TaskCreate) => tasksService.createTask(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all });
      toast.success("Task created successfully");
    },
    onError: () => {
      toast.error("Failed to create task");
    },
  });
}

export function useUpdateTask(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: TaskUpdate) =>
      tasksService.updateTask(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all });
      queryClient.invalidateQueries({
        queryKey: queryKeys.tasks.detail(id),
      });
      toast.success("Task updated successfully");
    },
    onError: () => {
      toast.error("Failed to update task");
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => tasksService.deleteTask(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all });
      toast.success("Task deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete task");
    },
  });
}

export function useAssignTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, userId }: { id: string; userId: string }) =>
      tasksService.assignTask(id, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all });
      toast.success("Task assigned successfully");
    },
    onError: () => {
      toast.error("Failed to assign task");
    },
  });
}

export function useMyTasks(params?: TaskFilters) {
  return useQuery({
    queryKey: [...queryKeys.tasks.all, "my-tasks", params],
    queryFn: () => tasksService.getMyTasks(params),
  });
}

export function useAddTaskComment(taskId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (content: string) =>
      tasksService.addComment(taskId, content),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.tasks.detail(taskId),
      });
      toast.success("Comment added");
    },
    onError: () => {
      toast.error("Failed to add comment");
    },
  });
}

export function useTeamWorkload() {
  return useQuery({
    queryKey: [...queryKeys.tasks.all, "workload"],
    queryFn: () => tasksService.getWorkload(),
  });
}
