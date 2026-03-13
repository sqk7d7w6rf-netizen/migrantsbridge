import { InvoiceStatus, TimestampMixin } from "./common";

export interface LineItem {
  id: string;
  description: string;
  quantity: number;
  unit_price: number;
  total: number;
}

export interface Invoice extends TimestampMixin {
  id: string;
  invoice_number: string;
  client_id: string;
  client_name?: string;
  case_id?: string;
  status: InvoiceStatus;
  issue_date: string;
  due_date: string;
  paid_date?: string;
  subtotal: number;
  tax_rate: number;
  tax_amount: number;
  total: number;
  amount_paid: number;
  balance_due: number;
  line_items: LineItem[];
  notes?: string;
}

export interface Payment extends TimestampMixin {
  id: string;
  invoice_id: string;
  amount: number;
  payment_method: "cash" | "check" | "credit_card" | "bank_transfer" | "other";
  payment_date: string;
  reference_number?: string;
  notes?: string;
}

export interface ServiceFee {
  id: string;
  name: string;
  description?: string;
  amount: number;
  is_active: boolean;
}
