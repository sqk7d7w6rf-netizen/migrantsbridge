import { Address, ImmigrationStatus, PhoneNumber, TimestampMixin } from "./common";

export interface ClientLanguage {
  language: string;
  proficiency: "basic" | "intermediate" | "fluent" | "native";
  is_primary: boolean;
}

export interface Client extends TimestampMixin {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone_numbers: PhoneNumber[];
  date_of_birth?: string;
  nationality?: string;
  immigration_status?: ImmigrationStatus;
  address?: Address;
  languages: ClientLanguage[];
  notes?: string;
  assigned_to?: string;
  assigned_to_name?: string;
  is_active: boolean;
  case_count?: number;
  tags?: string[];
}

export interface ClientCreate {
  first_name: string;
  last_name: string;
  email: string;
  phone_numbers?: PhoneNumber[];
  date_of_birth?: string;
  nationality?: string;
  immigration_status?: ImmigrationStatus;
  address?: Address;
  languages?: ClientLanguage[];
  notes?: string;
  assigned_to?: string;
  tags?: string[];
}

export type ClientUpdate = Partial<ClientCreate>;
