/** UI display maps for backend enum values. Each entry: { label, color } for StatusBadge. */

export const CASE_STATUSES: Record<string, { label: string; color: string }> = {
  intake:              { label: "Intake",            color: "bg-blue-100 text-blue-800" },
  open:                { label: "Open",              color: "bg-green-100 text-green-800" },
  in_progress:         { label: "In Progress",       color: "bg-yellow-100 text-yellow-800" },
  pending_client:      { label: "Pending Client",    color: "bg-orange-100 text-orange-800" },
  pending_external:    { label: "Pending External",  color: "bg-purple-100 text-purple-800" },
  under_review:        { label: "Under Review",      color: "bg-indigo-100 text-indigo-800" },
  on_hold:             { label: "On Hold",           color: "bg-gray-100 text-gray-800" },
  closed_successful:   { label: "Closed ✓",          color: "bg-green-200 text-green-900" },
  closed_unsuccessful: { label: "Closed ✗",          color: "bg-red-100 text-red-800" },
  closed_withdrawn:    { label: "Withdrawn",         color: "bg-gray-200 text-gray-700" },
};

export const PRIORITIES: Record<string, { label: string; color: string }> = {
  low:    { label: "Low",    color: "bg-gray-100 text-gray-600" },
  medium: { label: "Medium", color: "bg-blue-100 text-blue-700" },
  high:   { label: "High",   color: "bg-orange-100 text-orange-700" },
  urgent: { label: "Urgent", color: "bg-red-100 text-red-700" },
};

export const TASK_STATUSES: Record<string, { label: string; color: string }> = {
  pending:     { label: "Pending",     color: "bg-gray-100 text-gray-600" },
  in_progress: { label: "In Progress", color: "bg-blue-100 text-blue-700" },
  blocked:     { label: "Blocked",     color: "bg-red-100 text-red-700" },
  completed:   { label: "Completed",   color: "bg-green-100 text-green-700" },
  cancelled:   { label: "Cancelled",   color: "bg-gray-200 text-gray-500" },
};

export const APPOINTMENT_STATUSES: Record<string, { label: string; color: string }> = {
  scheduled:   { label: "Scheduled",   color: "bg-blue-100 text-blue-700" },
  confirmed:   { label: "Confirmed",   color: "bg-green-100 text-green-700" },
  in_progress: { label: "In Progress", color: "bg-yellow-100 text-yellow-700" },
  completed:   { label: "Completed",   color: "bg-green-200 text-green-800" },
  cancelled:   { label: "Cancelled",   color: "bg-red-100 text-red-700" },
  no_show:     { label: "No Show",     color: "bg-orange-100 text-orange-700" },
  rescheduled: { label: "Rescheduled", color: "bg-purple-100 text-purple-700" },
};

export const APPOINTMENT_TYPES: Record<string, { label: string }> = {
  initial_consultation: { label: "Initial Consultation" },
  follow_up:            { label: "Follow-up" },
  document_review:      { label: "Document Review" },
  court_preparation:    { label: "Court Preparation" },
  phone_call:           { label: "Phone Call" },
  video_call:           { label: "Video Call" },
  home_visit:           { label: "Home Visit" },
  group_session:        { label: "Group Session" },
  other:                { label: "Other" },
};

export const INVOICE_STATUSES: Record<string, { label: string; color: string }> = {
  draft:           { label: "Draft",          color: "bg-gray-100 text-gray-600" },
  sent:            { label: "Sent",           color: "bg-blue-100 text-blue-700" },
  paid:            { label: "Paid",           color: "bg-green-100 text-green-700" },
  partially_paid:  { label: "Partial",        color: "bg-yellow-100 text-yellow-700" },
  overdue:         { label: "Overdue",        color: "bg-red-100 text-red-700" },
  cancelled:       { label: "Cancelled",      color: "bg-gray-200 text-gray-500" },
  refunded:        { label: "Refunded",       color: "bg-purple-100 text-purple-700" },
  waived:          { label: "Waived",         color: "bg-teal-100 text-teal-700" },
};

export const IMMIGRATION_STATUSES: Record<string, { label: string; color: string }> = {
  refugee:            { label: "Refugee",            color: "bg-orange-100 text-orange-700" },
  asylee:             { label: "Asylee",             color: "bg-yellow-100 text-yellow-700" },
  visa_holder:        { label: "Visa Holder",        color: "bg-blue-100 text-blue-700" },
  undocumented:       { label: "Undocumented",       color: "bg-red-100 text-red-700" },
  permanent_resident: { label: "Permanent Resident", color: "bg-green-100 text-green-700" },
  citizen:            { label: "Citizen",            color: "bg-green-200 text-green-800" },
  other:              { label: "Other",              color: "bg-gray-100 text-gray-600" },
};

export const DOCUMENT_TYPES: Record<string, { label: string }> = {
  passport:             { label: "Passport" },
  visa:                 { label: "Visa" },
  birth_certificate:    { label: "Birth Certificate" },
  marriage_certificate: { label: "Marriage Certificate" },
  court_order:          { label: "Court Order" },
  immigration_form:     { label: "Immigration Form" },
  medical_record:       { label: "Medical Record" },
  financial_document:   { label: "Financial Document" },
  employment_record:    { label: "Employment Record" },
  identity_card:        { label: "Identity Card" },
  education_record:     { label: "Education Record" },
  correspondence:       { label: "Correspondence" },
  legal_brief:          { label: "Legal Brief" },
  photo:                { label: "Photo" },
  other:                { label: "Other" },
};

export const SERVICE_TYPES: { value: string; label: string }[] = [
  { value: "immigration",      label: "Immigration" },
  { value: "legal",            label: "Legal" },
  { value: "housing",          label: "Housing" },
  { value: "employment",       label: "Employment" },
  { value: "education",        label: "Education" },
  { value: "healthcare",       label: "Healthcare" },
  { value: "social_services",  label: "Social Services" },
  { value: "financial",        label: "Financial" },
  { value: "translation",      label: "Translation" },
  { value: "other",            label: "Other" },
];
