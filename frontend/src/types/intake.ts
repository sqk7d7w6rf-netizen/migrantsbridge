export interface IntakePersonalInfo {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  email: string;
  phone: string;
  preferred_language: string;
  nationality: string;
}

export interface IntakeCaseDetails {
  service_type: string;
  immigration_status: string;
  description: string;
  urgency: "low" | "medium" | "high" | "urgent";
}

export interface IntakeDocument {
  id: string;
  name: string;
  type: string;
  file?: File;
  uploaded: boolean;
  required: boolean;
}

export interface IntakeFormData {
  personal_info: IntakePersonalInfo;
  case_details: IntakeCaseDetails;
  documents: IntakeDocument[];
  preferred_language: string;
}

export interface IntakeSubmission {
  id: string;
  reference_number: string;
  status: "submitted" | "under_review" | "accepted" | "rejected";
  submitted_at: string;
  form_data: IntakeFormData;
}

export const INTAKE_STEPS = [
  { id: "personal-info", label: "Personal Information", path: "personal-info" },
  { id: "case-details", label: "Case Details", path: "case-details" },
  { id: "documents", label: "Documents", path: "documents" },
  { id: "review", label: "Review & Submit", path: "review" },
] as const;

export type IntakeStepId = (typeof INTAKE_STEPS)[number]["id"];
