from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    MONEY_ORDER = "money_order"
    ONLINE = "online"
    OTHER = "other"


class ServiceFeeCreate(BaseModel):
    """Create a service fee definition."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    amount: Decimal = Field(ge=0, decimal_places=2)
    service_type: str = Field(max_length=100)
    is_active: bool = True


class ServiceFeeRead(BaseModel):
    """Service fee read response."""

    id: UUID
    name: str
    description: str | None = None
    amount: Decimal
    service_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LineItemCreate(BaseModel):
    """Create an invoice line item."""

    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(ge=0, decimal_places=2, default=Decimal("1.00"))
    unit_price: Decimal = Field(ge=0, decimal_places=2)
    service_fee_id: UUID | None = None


class LineItemRead(BaseModel):
    """Invoice line item read response."""

    id: UUID
    invoice_id: UUID
    description: str
    quantity: Decimal
    unit_price: Decimal
    total: Decimal
    service_fee_id: UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class InvoiceCreate(BaseModel):
    """Create a new invoice."""

    client_id: UUID
    case_id: UUID | None = None
    due_date: date
    notes: str | None = None
    line_items: list[LineItemCreate] = Field(min_length=1)


class InvoiceRead(BaseModel):
    """Invoice read response."""

    id: UUID
    invoice_number: str
    client_id: UUID
    client_name: str | None = None
    case_id: UUID | None = None
    status: InvoiceStatus
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    due_date: date
    paid_date: date | None = None
    notes: str | None = None
    line_items: list[LineItemRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InvoiceUpdate(BaseModel):
    """Update an invoice."""

    status: InvoiceStatus | None = None
    due_date: date | None = None
    notes: str | None = None
    tax_amount: Decimal | None = None


class PaymentCreate(BaseModel):
    """Record a payment."""

    invoice_id: UUID
    amount: Decimal = Field(gt=0, decimal_places=2)
    payment_method: PaymentMethod
    reference_number: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    payment_date: date | None = None


class PaymentRead(BaseModel):
    """Payment read response."""

    id: UUID
    invoice_id: UUID
    amount: Decimal
    payment_method: PaymentMethod
    reference_number: str | None = None
    notes: str | None = None
    payment_date: date
    recorded_by: UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BillingSummary(BaseModel):
    """Billing summary / dashboard data."""

    total_invoiced: Decimal
    total_collected: Decimal
    total_outstanding: Decimal
    overdue_amount: Decimal
    invoices_count: int
    paid_count: int
    overdue_count: int
    average_days_to_payment: float | None = None
    period_start: date | None = None
    period_end: date | None = None
