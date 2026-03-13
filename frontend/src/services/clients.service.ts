import apiClient from "@/lib/api-client";
import { Client, ClientCreate, ClientUpdate } from "@/types/client";
import { PaginatedResponse, PaginationParams } from "@/types/api";

export const clientsService = {
  async getClients(
    params?: PaginationParams
  ): Promise<PaginatedResponse<Client>> {
    const { data } = await apiClient.get("/clients", { params });
    return data;
  },

  async getClient(id: string): Promise<Client> {
    const { data } = await apiClient.get(`/clients/${id}`);
    return data;
  },

  async createClient(payload: ClientCreate): Promise<Client> {
    const { data } = await apiClient.post("/clients", payload);
    return data;
  },

  async updateClient(id: string, payload: ClientUpdate): Promise<Client> {
    const { data } = await apiClient.patch(`/clients/${id}`, payload);
    return data;
  },

  async deleteClient(id: string): Promise<void> {
    await apiClient.delete(`/clients/${id}`);
  },

  async searchClients(query: string): Promise<Client[]> {
    const { data } = await apiClient.get("/clients/search", {
      params: { q: query },
    });
    return data;
  },
};
