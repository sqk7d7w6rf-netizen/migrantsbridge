"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import {
  schedulingService,
  AppointmentCreate,
  AppointmentUpdate,
  AppointmentFilters,
} from "@/services/scheduling.service";
import { toast } from "sonner";

export function useAppointments(params?: AppointmentFilters) {
  return useQuery({
    queryKey: queryKeys.appointments.list(
      (params || {}) as Record<string, unknown>
    ),
    queryFn: () => schedulingService.getAppointments(params),
  });
}

export function useAppointment(id: string) {
  return useQuery({
    queryKey: queryKeys.appointments.detail(id),
    queryFn: () => schedulingService.getAppointment(id),
    enabled: !!id,
  });
}

export function useCalendarData(month: number, year: number) {
  return useQuery({
    queryKey: [...queryKeys.appointments.all, "calendar", month, year],
    queryFn: () => schedulingService.getCalendarData(month, year),
  });
}

export function useCreateAppointment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: AppointmentCreate) =>
      schedulingService.createAppointment(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.appointments.all });
      toast.success("Appointment created successfully");
    },
    onError: () => {
      toast.error("Failed to create appointment");
    },
  });
}

export function useUpdateAppointment(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: AppointmentUpdate) =>
      schedulingService.updateAppointment(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.appointments.all });
      queryClient.invalidateQueries({
        queryKey: queryKeys.appointments.detail(id),
      });
      toast.success("Appointment updated successfully");
    },
    onError: () => {
      toast.error("Failed to update appointment");
    },
  });
}

export function useDeleteAppointment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => schedulingService.deleteAppointment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.appointments.all });
      toast.success("Appointment deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete appointment");
    },
  });
}

export function useAvailability(userId?: string) {
  return useQuery({
    queryKey: [...queryKeys.appointments.all, "availability", userId],
    queryFn: () => schedulingService.getAvailability(userId),
  });
}

export function useUpdateAvailability() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: schedulingService.updateAvailability,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [...queryKeys.appointments.all, "availability"],
      });
      toast.success("Availability updated successfully");
    },
    onError: () => {
      toast.error("Failed to update availability");
    },
  });
}

export function useAvailableSlots(date: string, staffId?: string) {
  return useQuery({
    queryKey: [...queryKeys.appointments.all, "slots", date, staffId],
    queryFn: () => schedulingService.getAvailableSlots(date, staffId),
    enabled: !!date,
  });
}
