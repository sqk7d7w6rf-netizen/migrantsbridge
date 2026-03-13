from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    PASSPORT = "passport"
    VISA = "visa"
    BIRTH_CERTIFICATE = "birth_certificate"
    MARRIAGE_CERTIFICATE = "marriage_certificate"
    WORK_PERMIT = "work_permit"
    ID_CARD = "id_card"
    DRIVERS_LICENSE = "drivers_license"
    TAX_RETURN = "tax_return"
    PAY_STUB = "pay_stub"
    BANK_STATEMENT = "bank_statement"
    LEASE_AGREEMENT = "lease_agreement"
    COURT_ORDER = "court_order"
    MEDICAL_RECORD = "medical_record"
    SCHOOL_RECORD = "school_record"
    REFERENCE_LETTER = "reference_letter"
    APPLICATION_FORM = "application_form"
    OTHER = "other"


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class DocumentRead(BaseModel):
    """Document read response."""

    id: UUID
    client_id: UUID
    case_id: UUID | None = None
    file_name: str
    original_file_name: str
    content_type: str
    file_size: int
    document_type: DocumentType | None = None
    storage_path: str
    verification_status: VerificationStatus
    verified_by: UUID | None = None
    verified_at: datetime | None = None
    expiry_date: datetime | None = None
    notes: str | None = None
    uploaded_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentUpdate(BaseModel):
    """Document update payload."""

    document_type: DocumentType | None = None
    expiry_date: datetime | None = None
    notes: str | None = None


class OCRResultRead(BaseModel):
    """OCR result read response."""

    id: UUID
    document_id: UUID
    raw_text: str
    extracted_data: dict | None = None
    confidence_score: float | None = None
    language_detected: str | None = None
    processed_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentVerifyRequest(BaseModel):
    """Document verification request."""

    status: VerificationStatus
    notes: str | None = None


class DocumentClassifyRequest(BaseModel):
    """Request AI document classification."""

    force_reclassify: bool = Field(default=False, description="Re-classify even if already classified")
