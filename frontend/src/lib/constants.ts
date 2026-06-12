export interface StatusConfig {
  label: string;
  color: string;
}

export const CASE_STATUSES: Record<string, StatusConfig> = {
  intake: { label: "Intake", color: "bg-blue-100 text-blue-800" },
  open: { label: "Open", color: "bg-green-100 text-green-800" },
  in_progress: { label: "In Progress", color: "bg-yellow-100 text-yellow-800" },
  pending_client: { label: "Pending Client", color: "bg-orange-100 text-orange-800" },
  pending_external: { label: "Pending External", color: "bg-orange-100 text-orange-800" },
  under_review: { label: "Under Review", color: "bg-purple-100 text-purple-800" },
  on_hold: { label: "On Hold", color: "bg-gray-100 text-gray-800" },
  closed_successful: { label: "Closed (Successful)", color: "bg-emerald-100 text-emerald-800" },
  closed_unsuccessful: { label: "Closed (Unsuccessful)", color: "bg-red-100 text-red-800" },
  closed_withdrawn: { label: "Closed (Withdrawn)", color: "bg-gray-100 text-gray-600" },
};

export const PRIORITIES: Record<string, StatusConfig> = {
  low: { label: "Low", color: "bg-gray-100 text-gray-800" },
  medium: { label: "Medium", color: "bg-blue-100 text-blue-800" },
  high: { label: "High", color: "bg-orange-100 text-orange-800" },
  urgent: { label: "Urgent", color: "bg-red-100 text-red-800" },
};

export const TASK_STATUSES: Record<string, StatusConfig> = {
  pending: { label: "Pending", color: "bg-gray-100 text-gray-800" },
  in_progress: { label: "In Progress", color: "bg-blue-100 text-blue-800" },
  blocked: { label: "Blocked", color: "bg-red-100 text-red-800" },
  completed: { label: "Completed", color: "bg-green-100 text-green-800" },
  cancelled: { label: "Cancelled", color: "bg-gray-100 text-gray-600" },
};

export const APPOINTMENT_STATUSES: Record<string, StatusConfig> = {
  scheduled: { label: "Scheduled", color: "bg-blue-100 text-blue-800" },
  confirmed: { label: "Confirmed", color: "bg-green-100 text-green-800" },
  in_progress: { label: "In Progress", color: "bg-yellow-100 text-yellow-800" },
  completed: { label: "Completed", color: "bg-emerald-100 text-emerald-800" },
  cancelled: { label: "Cancelled", color: "bg-gray-100 text-gray-600" },
  no_show: { label: "No Show", color: "bg-red-100 text-red-800" },
  rescheduled: { label: "Rescheduled", color: "bg-purple-100 text-purple-800" },
};

export const APPOINTMENT_TYPES: Record<string, StatusConfig> = {
  in_person: { label: "In Person", color: "bg-blue-100 text-blue-800" },
  video: { label: "Video Call", color: "bg-purple-100 text-purple-800" },
  phone: { label: "Phone Call", color: "bg-green-100 text-green-800" },
  initial_consultation: { label: "Initial Consultation", color: "bg-blue-100 text-blue-800" },
  follow_up: { label: "Follow Up", color: "bg-teal-100 text-teal-800" },
  document_review: { label: "Document Review", color: "bg-amber-100 text-amber-800" },
  court_preparation: { label: "Court Preparation", color: "bg-red-100 text-red-800" },
  home_visit: { label: "Home Visit", color: "bg-orange-100 text-orange-800" },
  group_session: { label: "Group Session", color: "bg-indigo-100 text-indigo-800" },
  other: { label: "Other", color: "bg-gray-100 text-gray-800" },
};

export const INVOICE_STATUSES: Record<string, StatusConfig> = {
  draft: { label: "Draft", color: "bg-gray-100 text-gray-800" },
  sent: { label: "Sent", color: "bg-blue-100 text-blue-800" },
  paid: { label: "Paid", color: "bg-green-100 text-green-800" },
  partially_paid: { label: "Partially Paid", color: "bg-yellow-100 text-yellow-800" },
  overdue: { label: "Overdue", color: "bg-red-100 text-red-800" },
  cancelled: { label: "Cancelled", color: "bg-gray-100 text-gray-600" },
  refunded: { label: "Refunded", color: "bg-purple-100 text-purple-800" },
  waived: { label: "Waived", color: "bg-teal-100 text-teal-800" },
};

export const IMMIGRATION_STATUSES: Record<string, StatusConfig> = {
  citizen: { label: "Citizen", color: "bg-green-100 text-green-800" },
  permanent_resident: { label: "Permanent Resident", color: "bg-emerald-100 text-emerald-800" },
  visa_holder: { label: "Visa Holder", color: "bg-blue-100 text-blue-800" },
  work_visa: { label: "Work Visa", color: "bg-blue-100 text-blue-800" },
  student_visa: { label: "Student Visa", color: "bg-indigo-100 text-indigo-800" },
  refugee: { label: "Refugee", color: "bg-orange-100 text-orange-800" },
  asylee: { label: "Asylee", color: "bg-amber-100 text-amber-800" },
  asylum_seeker: { label: "Asylum Seeker", color: "bg-amber-100 text-amber-800" },
  undocumented: { label: "Undocumented", color: "bg-gray-100 text-gray-800" },
  temporary_protected_status: { label: "TPS", color: "bg-purple-100 text-purple-800" },
  daca: { label: "DACA", color: "bg-teal-100 text-teal-800" },
  other: { label: "Other", color: "bg-gray-100 text-gray-800" },
};

export const DOCUMENT_TYPES: Record<string, StatusConfig> = {
  passport: { label: "Passport", color: "bg-blue-100 text-blue-800" },
  visa: { label: "Visa", color: "bg-indigo-100 text-indigo-800" },
  birth_certificate: { label: "Birth Certificate", color: "bg-green-100 text-green-800" },
  marriage_certificate: { label: "Marriage Certificate", color: "bg-pink-100 text-pink-800" },
  court_order: { label: "Court Order", color: "bg-red-100 text-red-800" },
  immigration_form: { label: "Immigration Form", color: "bg-purple-100 text-purple-800" },
  medical_record: { label: "Medical Record", color: "bg-teal-100 text-teal-800" },
  financial_document: { label: "Financial Document", color: "bg-amber-100 text-amber-800" },
  employment_record: { label: "Employment Record", color: "bg-orange-100 text-orange-800" },
  identity_card: { label: "Identity Card", color: "bg-cyan-100 text-cyan-800" },
  education_record: { label: "Education Record", color: "bg-lime-100 text-lime-800" },
  correspondence: { label: "Correspondence", color: "bg-gray-100 text-gray-800" },
  legal_brief: { label: "Legal Brief", color: "bg-slate-100 text-slate-800" },
  photo: { label: "Photo", color: "bg-rose-100 text-rose-800" },
  other: { label: "Other", color: "bg-gray-100 text-gray-800" },
};

export const SERVICE_TYPES: { value: string; label: string }[] = [
  { value: "immigration", label: "Immigration Services" },
  { value: "legal", label: "Legal Assistance" },
  { value: "housing", label: "Housing Support" },
  { value: "employment", label: "Job Placement" },
  { value: "education", label: "Education Services" },
  { value: "healthcare", label: "Healthcare Navigation" },
  { value: "social_services", label: "Social Services" },
  { value: "financial", label: "Financial / Wealth Building" },
  { value: "translation", label: "Translation Services" },
  { value: "other", label: "Other" },
];
