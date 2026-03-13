"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { clientsService } from "@/services/clients.service";
import { ClientCreate, ClientUpdate } from "@/types/client";
import { PaginationParams } from "@/types/api";
import { toast } from "sonner";

export function useClients(params?: PaginationParams) {
  return useQuery({
    queryKey: queryKeys.clients.list((params || {}) as Record<string, unknown>),
    queryFn: () => clientsService.getClients(params),
  });
}

export function useClient(id: string) {
  return useQuery({
    queryKey: queryKeys.clients.detail(id),
    queryFn: () => clientsService.getClient(id),
    enabled: !!id,
  });
}

export function useCreateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ClientCreate) =>
      clientsService.createClient(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.clients.all });
      toast.success("Client created successfully");
    },
    onError: () => {
      toast.error("Failed to create client");
    },
  });
}

export function useUpdateClient(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ClientUpdate) =>
      clientsService.updateClient(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.clients.all });
      queryClient.invalidateQueries({
        queryKey: queryKeys.clients.detail(id),
      });
      toast.success("Client updated successfully");
    },
    onError: () => {
      toast.error("Failed to update client");
    },
  });
}

export function useDeleteClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => clientsService.deleteClient(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.clients.all });
      toast.success("Client deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete client");
    },
  });
}
