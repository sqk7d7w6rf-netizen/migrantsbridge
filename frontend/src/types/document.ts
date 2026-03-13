import { TimestampMixin } from "./common";

export interface Document extends TimestampMixin {
  id: string;
  client_id: string;
  case_id?: string;
  name: string;
  file_name: string;
  file_type: string;
  file_size: number;
  document_type: string;
  status: "pending" | "approved" | "rejected" | "expired";
  uploaded_by: string;
  uploaded_by_name?: string;
  expiry_date?: string;
  notes?: string;
  url?: string;
  versions?: DocumentVersion[];
}

export interface DocumentVersion extends TimestampMixin {
  id: string;
  document_id: string;
  version_number: number;
  file_name: string;
  file_size: number;
  uploaded_by: string;
  uploaded_by_name?: string;
  url?: string;
}
