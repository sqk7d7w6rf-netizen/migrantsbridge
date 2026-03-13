import apiClient from "@/lib/api-client";
import { Invoice, Payment, ServiceFee } from "@/types/invoice";
import { PaginatedResponse, PaginationParams } from "@/types/api";

export interface InvoiceCreate {
  client_id: string;
  case_id?: string;
  due_date: string;
  line_items: {
    description: string;
    quantity: number;
    unit_price: number;
  }[];
  notes?: string;
  tax_rate?: number;
  is_pro_bono?: boolean;
}

export interface PaymentCreate {
  invoice_id: string;
  amount: number;
  payment_method: Payment["payment_method"];
  payment_date: string;
  reference_number?: string;
  notes?: string;
}

export interface FinancialSummary {
  total_revenue: number;
  total_outstanding: number;
  total_overdue: number;
  collected_this_month: number;
  invoice_count: number;
  paid_count: number;
  overdue_count: number;
}

export interface InvoiceFilters extends PaginationParams {
  status?: string;
  client_id?: string;
  date_from?: string;
  date_to?: string;
}

export interface PaymentFilters extends PaginationParams {
  payment_method?: string;
  date_from?: string;
  date_to?: string;
}

export const billingService = {
  async getInvoices(
    params?: InvoiceFilters
  ): Promise<PaginatedResponse<Invoice>> {
    const { data } = await apiClient.get("/invoices", { params });
    return data;
  },

  async getInvoice(id: string): Promise<Invoice> {
    const { data } = await apiClient.get(`/invoices/${id}`);
    return data;
  },

  async createInvoice(payload: InvoiceCreate): Promise<Invoice> {
    const { data } = await apiClient.post("/invoices", payload);
    return data;
  },

  async updateInvoice(
    id: string,
    payload: Partial<InvoiceCreate>
  ): Promise<Invoice> {
    const { data } = await apiClient.patch(`/invoices/${id}`, payload);
    return data;
  },

  async deleteInvoice(id: string): Promise<void> {
    await apiClient.delete(`/invoices/${id}`);
  },

  async sendInvoice(id: string): Promise<Invoice> {
    const { data } = await apiClient.post(`/invoices/${id}/send`);
    return data;
  },

  async cancelInvoice(id: string): Promise<Invoice> {
    const { data } = await apiClient.post(`/invoices/${id}/cancel`);
    return data;
  },

  async getPayments(
    params?: PaymentFilters
  ): Promise<PaginatedResponse<Payment>> {
    const { data } = await apiClient.get("/payments", { params });
    return data;
  },

  async getInvoicePayments(invoiceId: string): Promise<Payment[]> {
    const { data } = await apiClient.get(
      `/invoices/${invoiceId}/payments`
    );
    return data;
  },

  async recordPayment(payload: PaymentCreate): Promise<Payment> {
    const { data } = await apiClient.post("/payments", payload);
    return data;
  },

  async getServiceFees(): Promise<ServiceFee[]> {
    const { data } = await apiClient.get("/service-fees");
    return data;
  },

  async getFinancialSummary(): Promise<FinancialSummary> {
    const { data } = await apiClient.get("/billing/summary");
    return data;
  },
};
