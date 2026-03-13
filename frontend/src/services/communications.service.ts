import apiClient from "@/lib/api-client";
import {
  Thread,
  Message,
  MessageTemplate,
  MessageTemplateCreate,
  MessageTemplateUpdate,
  SendNotificationPayload,
  NotificationPreference,
} from "@/types/communication";
import { PaginatedResponse, PaginationParams } from "@/types/api";

export interface ThreadFilters extends PaginationParams {
  status?: string;
  channel?: string;
  client_id?: string;
}

export const communicationsService = {
  async getThreads(
    params?: ThreadFilters
  ): Promise<PaginatedResponse<Thread>> {
    const { data } = await apiClient.get("/communications/threads", { params });
    return data;
  },

  async getThread(id: string): Promise<Thread & { messages: Message[] }> {
    const { data } = await apiClient.get(`/communications/threads/${id}`);
    return data;
  },

  async getThreadMessages(threadId: string): Promise<Message[]> {
    const { data } = await apiClient.get(
      `/communications/threads/${threadId}/messages`
    );
    return data;
  },

  async sendNotification(
    payload: SendNotificationPayload
  ): Promise<Message> {
    const { data } = await apiClient.post(
      "/communications/send",
      payload
    );
    return data;
  },

  async markThreadRead(threadId: string): Promise<void> {
    await apiClient.post(`/communications/threads/${threadId}/read`);
  },

  async getTemplates(
    params?: PaginationParams
  ): Promise<PaginatedResponse<MessageTemplate>> {
    const { data } = await apiClient.get("/communications/templates", {
      params,
    });
    return data;
  },

  async getTemplate(id: string): Promise<MessageTemplate> {
    const { data } = await apiClient.get(`/communications/templates/${id}`);
    return data;
  },

  async createTemplate(
    payload: MessageTemplateCreate
  ): Promise<MessageTemplate> {
    const { data } = await apiClient.post(
      "/communications/templates",
      payload
    );
    return data;
  },

  async updateTemplate(
    id: string,
    payload: MessageTemplateUpdate
  ): Promise<MessageTemplate> {
    const { data } = await apiClient.patch(
      `/communications/templates/${id}`,
      payload
    );
    return data;
  },

  async deleteTemplate(id: string): Promise<void> {
    await apiClient.delete(`/communications/templates/${id}`);
  },

  async getNotificationPreferences(): Promise<NotificationPreference[]> {
    const { data } = await apiClient.get(
      "/communications/notification-preferences"
    );
    return data;
  },

  async updateNotificationPreferences(
    preferences: NotificationPreference[]
  ): Promise<NotificationPreference[]> {
    const { data } = await apiClient.put(
      "/communications/notification-preferences",
      { preferences }
    );
    return data;
  },
};
