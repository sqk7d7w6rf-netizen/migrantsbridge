import enum


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    OTHER = "other"


class ImmigrationStatus(str, enum.Enum):
    REFUGEE = "refugee"
    ASYLEE = "asylee"
    VISA_HOLDER = "visa_holder"
    UNDOCUMENTED = "undocumented"
    PERMANENT_RESIDENT = "permanent_resident"
    CITIZEN = "citizen"
    OTHER = "other"


class CaseType(str, enum.Enum):
    IMMIGRATION = "immigration"
    LEGAL = "legal"
    HOUSING = "housing"
    EMPLOYMENT = "employment"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    SOCIAL_SERVICES = "social_services"
    FINANCIAL = "financial"
    TRANSLATION = "translation"
    OTHER = "other"


class CaseStatus(str, enum.Enum):
    INTAKE = "intake"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_CLIENT = "pending_client"
    PENDING_EXTERNAL = "pending_external"
    UNDER_REVIEW = "under_review"
    ON_HOLD = "on_hold"
    CLOSED_SUCCESSFUL = "closed_successful"
    CLOSED_UNSUCCESSFUL = "closed_unsuccessful"
    CLOSED_WITHDRAWN = "closed_withdrawn"


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class DocumentType(str, enum.Enum):
    PASSPORT = "passport"
    VISA = "visa"
    BIRTH_CERTIFICATE = "birth_certificate"
    MARRIAGE_CERTIFICATE = "marriage_certificate"
    COURT_ORDER = "court_order"
    IMMIGRATION_FORM = "immigration_form"
    MEDICAL_RECORD = "medical_record"
    FINANCIAL_DOCUMENT = "financial_document"
    EMPLOYMENT_RECORD = "employment_record"
    IDENTITY_CARD = "identity_card"
    EDUCATION_RECORD = "education_record"
    CORRESPONDENCE = "correspondence"
    LEGAL_BRIEF = "legal_brief"
    PHOTO = "photo"
    OTHER = "other"


class OcrStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"


class AppointmentType(str, enum.Enum):
    INITIAL_CONSULTATION = "initial_consultation"
    FOLLOW_UP = "follow_up"
    DOCUMENT_REVIEW = "document_review"
    COURT_PREPARATION = "court_preparation"
    PHONE_CALL = "phone_call"
    VIDEO_CALL = "video_call"
    HOME_VISIT = "home_visit"
    GROUP_SESSION = "group_session"
    OTHER = "other"


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class DayOfWeek(str, enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class ChannelType(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    PUSH = "push"
    WHATSAPP = "whatsapp"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    WAIVED = "waived"


class PaymentMethod(str, enum.Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CHECK = "check"
    STRIPE = "stripe"
    OTHER = "other"


class TaskType(str, enum.Enum):
    FOLLOW_UP = "follow_up"
    DOCUMENT_REQUEST = "document_request"
    REVIEW = "review"
    RESEARCH = "research"
    OUTREACH = "outreach"
    DATA_ENTRY = "data_entry"
    TRANSLATION = "translation"
    COURT_PREP = "court_prep"
    ADMINISTRATIVE = "administrative"
    OTHER = "other"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EmploymentStatus(str, enum.Enum):
    EMPLOYED_FULL_TIME = "employed_full_time"
    EMPLOYED_PART_TIME = "employed_part_time"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    STUDENT = "student"
    RETIRED = "retired"
    UNABLE_TO_WORK = "unable_to_work"
    OTHER = "other"


class WorkflowTriggerType(str, enum.Enum):
    CASE_CREATED = "case_created"
    CASE_STATUS_CHANGED = "case_status_changed"
    DOCUMENT_UPLOADED = "document_uploaded"
    APPOINTMENT_SCHEDULED = "appointment_scheduled"
    INTAKE_COMPLETED = "intake_completed"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    AI_TRIGGERED = "ai_triggered"


class WorkflowStepType(str, enum.Enum):
    SEND_NOTIFICATION = "send_notification"
    CREATE_TASK = "create_task"
    ASSIGN_CASE = "assign_case"
    UPDATE_STATUS = "update_status"
    AI_CLASSIFICATION = "ai_classification"
    WAIT = "wait"
    CONDITION = "condition"
    WEBHOOK = "webhook"
    APPROVAL = "approval"


class WorkflowExecutionStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class IntakeSubmissionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReminderType(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class SavingsTransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    INTEREST = "interest"
    MATCH = "match"
    FEE = "fee"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
