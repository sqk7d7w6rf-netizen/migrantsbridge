import { TimestampMixin } from "./common";

export interface FinancialGoal extends TimestampMixin {
  id: string;
  client_id: string;
  client_name?: string;
  name: string;
  description?: string;
  target_amount: number;
  current_amount: number;
  target_date: string;
  status: "active" | "completed" | "paused" | "cancelled";
  category: "emergency_fund" | "education" | "housing" | "business" | "retirement" | "other";
  progress_percentage: number;
}

export interface SavingsProgram extends TimestampMixin {
  id: string;
  client_id: string;
  goal_id?: string;
  name: string;
  contribution_amount: number;
  frequency: "weekly" | "biweekly" | "monthly";
  start_date: string;
  end_date?: string;
  is_active: boolean;
  total_saved: number;
}

export interface Investment extends TimestampMixin {
  id: string;
  client_id: string;
  name: string;
  type: "stocks" | "bonds" | "mutual_fund" | "savings_account" | "cd" | "other";
  amount_invested: number;
  current_value: number;
  return_rate: number;
  start_date: string;
  notes?: string;
}

export interface Asset extends TimestampMixin {
  id: string;
  client_id: string;
  name: string;
  type: "property" | "vehicle" | "business" | "other";
  estimated_value: number;
  purchase_date?: string;
  notes?: string;
}
