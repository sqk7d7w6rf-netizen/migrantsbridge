import { TimestampMixin } from "./common";

export type MessageChannel = "email" | "sms" | "in_app";

export type ThreadStatus = "open" | "closed" | "archived";

export interface Message extends TimestampMixin {
  id: string;
  thread_id: string;
  sender_id: string;
  sender_name: string;
  sender_type: "staff" | "client" | "system";
  content: string;
  channel: MessageChannel;
  is_read: boolean;
  metadata?: Record<string, unknown>;
}

export interface Thread extends TimestampMixin {
  id: string;
  subject: string;
  client_id: string;
  client_name: string;
  participants: string[];
  status: ThreadStatus;
  last_message?: Message;
  unread_count: number;
  channel: MessageChannel;
}

export interface MessageTemplate extends TimestampMixin {
  id: string;
  name: string;
  subject: string;
  body: string;
  channel: MessageChannel;
  category: string;
  variables: string[];
  is_active: boolean;
}

export interface MessageTemplateCreate {
  name: string;
  subject: string;
  body: string;
  channel: MessageChannel;
  category: string;
  variables?: string[];
}

export type MessageTemplateUpdate = Partial<MessageTemplateCreate>;

export interface SendNotificationPayload {
  thread_id?: string;
  client_id: string;
  channel: MessageChannel;
  subject?: string;
  content: string;
  template_id?: string;
  template_variables?: Record<string, string>;
}

export interface NotificationPreference {
  event_type: string;
  event_label: string;
  email_enabled: boolean;
  sms_enabled: boolean;
  in_app_enabled: boolean;
}
