import { CaseStatus, Priority, TimestampMixin } from "./common";

export interface Case extends TimestampMixin {
  id: string;
  client_id: string;
  client_name?: string;
  case_number: string;
  title: string;
  description?: string;
  case_type: string;
  status: CaseStatus;
  priority: Priority;
  assigned_to?: string;
  assigned_to_name?: string;
  opened_date: string;
  closed_date?: string;
  due_date?: string;
  notes?: string;
  tags?: string[];
}

export interface CaseNote extends TimestampMixin {
  id: string;
  case_id: string;
  author_id: string;
  author_name: string;
  content: string;
  is_internal: boolean;
}

export interface CaseHistory extends TimestampMixin {
  id: string;
  case_id: string;
  user_id: string;
  user_name: string;
  action: string;
  field_changed?: string;
  old_value?: string;
  new_value?: string;
}
