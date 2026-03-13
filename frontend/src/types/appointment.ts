import { TimestampMixin } from "./common";

export interface Appointment extends TimestampMixin {
  id: string;
  client_id: string;
  client_name?: string;
  case_id?: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  meeting_url?: string;
  type: "in_person" | "video" | "phone";
  status: "scheduled" | "confirmed" | "completed" | "cancelled" | "no_show";
  assigned_to: string;
  assigned_to_name?: string;
  notes?: string;
  reminder_sent: boolean;
}

export interface Availability extends TimestampMixin {
  id: string;
  user_id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  is_recurring: boolean;
  specific_date?: string;
}
