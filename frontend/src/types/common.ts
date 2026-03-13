export type CaseStatus =
  | "open"
  | "in_progress"
  | "pending_documents"
  | "under_review"
  | "approved"
  | "denied"
  | "closed";

export type Priority = "low" | "medium" | "high" | "urgent";

export type TaskStatus = "todo" | "in_progress" | "completed" | "cancelled";

export type InvoiceStatus = "draft" | "sent" | "paid" | "overdue" | "cancelled";

export type ImmigrationStatus =
  | "citizen"
  | "permanent_resident"
  | "work_visa"
  | "student_visa"
  | "refugee"
  | "asylum_seeker"
  | "undocumented"
  | "temporary_protected_status"
  | "daca"
  | "other";

export interface Address {
  street: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
}

export interface PhoneNumber {
  number: string;
  type: "mobile" | "home" | "work";
  is_primary: boolean;
}

export interface TimestampMixin {
  created_at: string;
  updated_at: string;
}
