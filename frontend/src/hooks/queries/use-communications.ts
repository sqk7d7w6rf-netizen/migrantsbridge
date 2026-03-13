"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import {
  communicationsService,
  ThreadFilters,
} from "@/services/communications.service";
import {
  MessageTemplateCreate,
  MessageTemplateUpdate,
  SendNotificationPayload,
  NotificationPreference,
} from "@/types/communication";
import { PaginationParams } from "@/types/api";
import { toast } from "sonner";

export function useThreads(params?: ThreadFilters) {
  return useQuery({
    queryKey: queryKeys.communications.list(
      (params || {}) as Record<string, unknown>
    ),
    queryFn: () => communicationsService.getThreads(params),
  });
}

export function useThread(id: string) {
  return useQuery({
    queryKey: queryKeys.communications.detail(id),
    queryFn: () => communicationsService.getThread(id),
    enabled: !!id,
  });
}

export function useSendNotification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: SendNotificationPayload) =>
      communicationsService.sendNotification(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.communications.all,
      });
      toast.success("Message sent successfully");
    },
    onError: () => {
      toast.error("Failed to send message");
    },
  });
}

export function useMarkThreadRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (threadId: string) =>
      communicationsService.markThreadRead(threadId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.communications.all,
      });
    },
  });
}

export function useTemplates(params?: PaginationParams) {
  return useQuery({
    queryKey: [...queryKeys.communications.all, "templates", params],
    queryFn: () => communicationsService.getTemplates(params),
  });
}

export function useTemplate(id: string) {
  return useQuery({
    queryKey: [...queryKeys.communications.all, "templates", id],
    queryFn: () => communicationsService.getTemplate(id),
    enabled: !!id,
  });
}

export function useCreateTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: MessageTemplateCreate) =>
      communicationsService.createTemplate(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [...queryKeys.communications.all, "templates"],
      });
      toast.success("Template created successfully");
    },
    onError: () => {
      toast.error("Failed to create template");
    },
  });
}

export function useUpdateTemplate(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: MessageTemplateUpdate) =>
      communicationsService.updateTemplate(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [...queryKeys.communications.all, "templates"],
      });
      toast.success("Template updated successfully");
    },
    onError: () => {
      toast.error("Failed to update template");
    },
  });
}

export function useDeleteTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => communicationsService.deleteTemplate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [...queryKeys.communications.all, "templates"],
      });
      toast.success("Template deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete template");
    },
  });
}

export function useNotificationPreferences() {
  return useQuery({
    queryKey: [...queryKeys.communications.all, "preferences"],
    queryFn: () => communicationsService.getNotificationPreferences(),
  });
}

export function useUpdateNotificationPreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (preferences: NotificationPreference[]) =>
      communicationsService.updateNotificationPreferences(preferences),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [...queryKeys.communications.all, "preferences"],
      });
      toast.success("Preferences updated successfully");
    },
    onError: () => {
      toast.error("Failed to update preferences");
    },
  });
}
