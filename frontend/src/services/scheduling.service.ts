import apiClient from "@/lib/api-client";
import { Appointment, Availability } from "@/types/appointment";
import { PaginatedResponse, PaginationParams } from "@/types/api";

export interface AppointmentFilters extends PaginationParams {
  status?: string;
  type?: string;
  assigned_to?: string;
  start_date?: string;
  end_date?: string;
  client_id?: string;
}

export interface CalendarData {
  appointments: Appointment[];
  month: number;
  year: number;
}

export interface AppointmentCreate {
  client_id: string;
  case_id?: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  meeting_url?: string;
  type: "in_person" | "video" | "phone";
  assigned_to: string;
  notes?: string;
}

export type AppointmentUpdate = Partial<AppointmentCreate> & {
  status?: Appointment["status"];
};

export interface AvailabilitySlot {
  user_id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  is_recurring: boolean;
  specific_date?: string;
}

export const schedulingService = {
  async getAppointments(
    params?: AppointmentFilters
  ): Promise<PaginatedResponse<Appointment>> {
    const { data } = await apiClient.get("/appointments", { params });
    return data;
  },

  async getAppointment(id: string): Promise<Appointment> {
    const { data } = await apiClient.get(`/appointments/${id}`);
    return data;
  },

  async createAppointment(payload: AppointmentCreate): Promise<Appointment> {
    const { data } = await apiClient.post("/appointments", payload);
    return data;
  },

  async updateAppointment(
    id: string,
    payload: AppointmentUpdate
  ): Promise<Appointment> {
    const { data } = await apiClient.patch(`/appointments/${id}`, payload);
    return data;
  },

  async deleteAppointment(id: string): Promise<void> {
    await apiClient.delete(`/appointments/${id}`);
  },

  async getCalendarData(month: number, year: number): Promise<CalendarData> {
    const { data } = await apiClient.get("/appointments/calendar", {
      params: { month, year },
    });
    return data;
  },

  async getAvailability(userId?: string): Promise<Availability[]> {
    const { data } = await apiClient.get("/appointments/availability", {
      params: userId ? { user_id: userId } : {},
    });
    return data;
  },

  async updateAvailability(slots: AvailabilitySlot[]): Promise<Availability[]> {
    const { data } = await apiClient.put("/appointments/availability", {
      slots,
    });
    return data;
  },

  async getAvailableSlots(
    date: string,
    staffId?: string
  ): Promise<{ start_time: string; end_time: string }[]> {
    const { data } = await apiClient.get("/appointments/available-slots", {
      params: { date, staff_id: staffId },
    });
    return data;
  },
};
