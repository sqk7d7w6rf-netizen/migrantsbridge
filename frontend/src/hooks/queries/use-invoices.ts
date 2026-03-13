"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import {
  billingService,
  InvoiceCreate,
  InvoiceFilters,
  PaymentCreate,
  PaymentFilters,
} from "@/services/billing.service";
import { toast } from "sonner";

export function useInvoices(params?: InvoiceFilters) {
  return useQuery({
    queryKey: queryKeys.invoices.list(
      (params || {}) as Record<string, unknown>
    ),
    queryFn: () => billingService.getInvoices(params),
  });
}

export function useInvoice(id: string) {
  return useQuery({
    queryKey: queryKeys.invoices.detail(id),
    queryFn: () => billingService.getInvoice(id),
    enabled: !!id,
  });
}

export function useCreateInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: InvoiceCreate) =>
      billingService.createInvoice(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.invoices.all });
      toast.success("Invoice created successfully");
    },
    onError: () => {
      toast.error("Failed to create invoice");
    },
  });
}

export function useUpdateInvoice(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: Partial<InvoiceCreate>) =>
      billingService.updateInvoice(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.invoices.all });
      queryClient.invalidateQueries({
        queryKey: queryKeys.invoices.detail(id),
      });
      toast.success("Invoice updated successfully");
    },
    onError: () => {
      toast.error("Failed to update invoice");
    },
  });
}

export function useDeleteInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => billingService.deleteInvoice(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.invoices.all });
      toast.success("Invoice deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete invoice");
    },
  });
}

export function useSendInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => billingService.sendInvoice(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.invoices.all });
      toast.success("Invoice sent successfully");
    },
    onError: () => {
      toast.error("Failed to send invoice");
    },
  });
}

export function useCancelInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => billingService.cancelInvoice(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.invoices.all });
      toast.success("Invoice cancelled");
    },
    onError: () => {
      toast.error("Failed to cancel invoice");
    },
  });
}

export function useRecordPayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: PaymentCreate) =>
      billingService.recordPayment(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.invoices.all });
      toast.success("Payment recorded successfully");
    },
    onError: () => {
      toast.error("Failed to record payment");
    },
  });
}

export function usePayments(params?: PaymentFilters) {
  return useQuery({
    queryKey: ["payments", params],
    queryFn: () => billingService.getPayments(params),
  });
}

export function useInvoicePayments(invoiceId: string) {
  return useQuery({
    queryKey: ["payments", "invoice", invoiceId],
    queryFn: () => billingService.getInvoicePayments(invoiceId),
    enabled: !!invoiceId,
  });
}

export function useServiceFees() {
  return useQuery({
    queryKey: ["service-fees"],
    queryFn: () => billingService.getServiceFees(),
  });
}

export function useFinancialSummary() {
  return useQuery({
    queryKey: ["billing", "summary"],
    queryFn: () => billingService.getFinancialSummary(),
  });
}
