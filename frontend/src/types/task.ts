import { Priority, TaskStatus, TimestampMixin } from "./common";

export interface Task extends TimestampMixin {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: Priority;
  assigned_to?: string;
  assigned_to_name?: string;
  client_id?: string;
  client_name?: string;
  case_id?: string;
  due_date?: string;
  completed_at?: string;
  tags?: string[];
  comments?: TaskComment[];
}

export interface TaskComment extends TimestampMixin {
  id: string;
  task_id: string;
  author_id: string;
  author_name: string;
  content: string;
}
