"""Billing service: invoices, payments, service fees, and summaries."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.constants import InvoiceStatus as ModelInvoiceStatus
from app.constants import PaymentMethod as ModelPaymentMethod
from app.core.pagination import PaginatedResponse, PaginationParams, paginate
from app.models.billing import Invoice, InvoiceLineItem, Payment, ServiceFee
from app.models.client import Client
from app.schemas.billing import (
    BillingSummary,
    InvoiceCreate,
    InvoiceRead,
    InvoiceStatus,
    InvoiceUpdate,
    LineItemRead,
    PaymentCreate,
    PaymentMethod,
    PaymentRead,
    ServiceFeeCreate,
    ServiceFeeRead,
)


async def _get_invoice_or_404(session: AsyncSession, invoice_id: UUID) -> Invoice:
    result = await session.execute(
        select(Invoice)
        .options(selectinload(Invoice.line_items))
        .where(Invoice.id == invoice_id, Invoice.is_deleted == False)
    )
    invoice = result.scalar_one_or_none()
    if invoice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice


def _to_line_item_read(li: InvoiceLineItem) -> LineItemRead:
    """Map InvoiceLineItem model to LineItemRead schema."""
    return LineItemRead(
        id=li.id,
        invoice_id=li.invoice_id,
        description=li.description,
        quantity=Decimal(li.quantity),
        unit_price=li.unit_price,
        total=li.total_price,
        service_fee_id=li.service_fee_id,
        created_at=li.created_at,
    )


async def _build_invoice_read(session: AsyncSession, invoice: Invoice) -> InvoiceRead:
    client_name = None
    if invoice.client:
        client_name = f"{invoice.client.first_name} {invoice.client.last_name}"
    elif invoice.client_id:
        cr = await session.execute(select(Client).where(Client.id == invoice.client_id))
        client = cr.scalar_one_or_none()
        if client:
            client_name = f"{client.first_name} {client.last_name}"

    line_items = [_to_line_item_read(li) for li in (invoice.line_items or [])]

    # Compute balance_due from model fields
    balance_due = invoice.total_amount - invoice.amount_paid

    return InvoiceRead(
        id=invoice.id,
        invoice_number=f"INV-{invoice.invoice_number:06d}",
        client_id=invoice.client_id,
        client_name=client_name,
        case_id=invoice.case_id,
        status=invoice.status.value,
        subtotal=invoice.subtotal,
        tax_amount=invoice.tax_amount,
        total_amount=invoice.total_amount,
        amount_paid=invoice.amount_paid,
        balance_due=balance_due,
        due_date=invoice.due_date,
        paid_date=invoice.paid_date,
        notes=invoice.notes,
        line_items=line_items,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at,
    )


def _to_service_fee_read(fee: ServiceFee) -> ServiceFeeRead:
    """Map ServiceFee model to ServiceFeeRead schema."""
    return ServiceFeeRead(
        id=fee.id,
        name=fee.name,
        description=fee.description,
        amount=fee.amount,
        service_type=fee.category or "",
        is_active=fee.is_active,
        created_at=fee.created_at,
        updated_at=fee.updated_at,
    )


# --- Service Fees ---

async def create_service_fee(session: AsyncSession, payload: ServiceFeeCreate) -> ServiceFeeRead:
    """Create a service fee definition."""
    fee = ServiceFee(
        name=payload.name,
        description=payload.description,
        amount=payload.amount,
        category=payload.service_type,
        is_active=payload.is_active,
    )
    session.add(fee)
    await session.flush()
    await session.refresh(fee)
    return _to_service_fee_read(fee)


async def list_service_fees(
    session: AsyncSession, pagination: PaginationParams, active_only: bool = True
) -> PaginatedResponse[ServiceFeeRead]:
    """List service fee definitions."""
    query = select(ServiceFee)
    if active_only:
        query = query.where(ServiceFee.is_active == True)
    query = query.order_by(ServiceFee.name.asc())
    result = await paginate(session, query, pagination)
    result.items = [_to_service_fee_read(f) for f in result.items]
    return result


# --- Invoices ---

async def create_invoice(
    session: AsyncSession, payload: InvoiceCreate, created_by: UUID
) -> InvoiceRead:
    """Create an invoice with line items and auto-computed totals."""
    # Verify client
    client_result = await session.execute(
        select(Client).where(Client.id == payload.client_id, Client.is_deleted == False)
    )
    if client_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    # Compute subtotal from line items
    subtotal = Decimal("0.00")
    for item in payload.line_items:
        subtotal += item.quantity * item.unit_price

    invoice = Invoice(
        client_id=payload.client_id,
        case_id=payload.case_id,
        status=ModelInvoiceStatus.DRAFT,
        subtotal=subtotal,
        tax_amount=Decimal("0.00"),
        discount_amount=Decimal("0.00"),
        total_amount=subtotal,
        amount_paid=Decimal("0.00"),
        issue_date=date.today(),
        due_date=payload.due_date,
        notes=payload.notes,
        created_by_id=created_by,
    )
    session.add(invoice)
    await session.flush()

    # Create line items
    for item in payload.line_items:
        line_total = item.quantity * item.unit_price
        li = InvoiceLineItem(
            invoice_id=invoice.id,
            description=item.description,
            quantity=int(item.quantity),
            unit_price=item.unit_price,
            total_price=line_total,
            service_fee_id=item.service_fee_id,
        )
        session.add(li)

    await session.flush()
    await session.refresh(invoice, attribute_names=["line_items"])

    return await _build_invoice_read(session, invoice)


async def get_invoice(session: AsyncSession, invoice_id: UUID) -> InvoiceRead:
    """Get an invoice by ID."""
    invoice = await _get_invoice_or_404(session, invoice_id)
    return await _build_invoice_read(session, invoice)


async def list_invoices(
    session: AsyncSession,
    pagination: PaginationParams,
    client_id: UUID | None = None,
    status_filter: str | None = None,
) -> PaginatedResponse[InvoiceRead]:
    """List invoices with optional filters."""
    query = select(Invoice).where(Invoice.is_deleted == False)
    if client_id:
        query = query.where(Invoice.client_id == client_id)
    if status_filter:
        try:
            query = query.where(Invoice.status == ModelInvoiceStatus(status_filter))
        except ValueError:
            pass
    query = query.order_by(Invoice.created_at.desc())
    result = await paginate(session, query, pagination)
    items = []
    for inv in result.items:
        items.append(await _build_invoice_read(session, inv))
    result.items = items
    return result


async def update_invoice(
    session: AsyncSession, invoice_id: UUID, payload: InvoiceUpdate
) -> InvoiceRead:
    """Update an invoice."""
    invoice = await _get_invoice_or_404(session, invoice_id)

    update_data = payload.model_dump(exclude_unset=True)

    if "status" in update_data and update_data["status"] is not None:
        try:
            invoice.status = ModelInvoiceStatus(update_data.pop("status").value)
        except (ValueError, AttributeError):
            update_data.pop("status", None)

    # Recompute total if tax changes
    if "tax_amount" in update_data and update_data["tax_amount"] is not None:
        tax = update_data.pop("tax_amount")
        invoice.tax_amount = tax
        invoice.total_amount = invoice.subtotal + tax - invoice.discount_amount

    for field, value in update_data.items():
        setattr(invoice, field, value)

    session.add(invoice)
    await session.flush()
    await session.refresh(invoice, attribute_names=["line_items"])
    return await _build_invoice_read(session, invoice)


async def delete_invoice(session: AsyncSession, invoice_id: UUID) -> None:
    """Soft-delete an invoice."""
    invoice = await _get_invoice_or_404(session, invoice_id)
    if invoice.status not in (ModelInvoiceStatus.DRAFT, ModelInvoiceStatus.CANCELLED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft or cancelled invoices can be deleted",
        )
    invoice.is_deleted = True
    invoice.deleted_at = datetime.now(timezone.utc)
    session.add(invoice)


# --- Payments ---

async def record_payment(
    session: AsyncSession, payload: PaymentCreate, recorded_by: UUID
) -> PaymentRead:
    """Record a payment against an invoice."""
    invoice = await _get_invoice_or_404(session, payload.invoice_id)

    if invoice.status in (ModelInvoiceStatus.CANCELLED, ModelInvoiceStatus.REFUNDED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot record payment on a {invoice.status.value} invoice",
        )

    balance_due = invoice.total_amount - invoice.amount_paid
    if payload.amount > balance_due:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount ({payload.amount}) exceeds balance due ({balance_due})",
        )

    # Map schema PaymentMethod to model PaymentMethod
    try:
        model_method = ModelPaymentMethod(payload.payment_method.value)
    except ValueError:
        model_method = ModelPaymentMethod.OTHER

    payment = Payment(
        invoice_id=invoice.id,
        amount=payload.amount,
        payment_method=model_method,
        external_transaction_id=payload.reference_number,
        notes=payload.notes,
        payment_date=datetime.combine(payload.payment_date, datetime.min.time()).replace(tzinfo=timezone.utc) if payload.payment_date else datetime.now(timezone.utc),
        processed_by_id=recorded_by,
    )
    session.add(payment)

    # Update invoice totals
    invoice.amount_paid += payload.amount

    if invoice.total_amount - invoice.amount_paid <= Decimal("0.00"):
        invoice.status = ModelInvoiceStatus.PAID
        invoice.paid_date = date.today()
    elif invoice.amount_paid > Decimal("0.00"):
        invoice.status = ModelInvoiceStatus.PARTIALLY_PAID

    session.add(invoice)
    await session.flush()
    await session.refresh(payment)

    return PaymentRead(
        id=payment.id,
        invoice_id=payment.invoice_id,
        amount=payment.amount,
        payment_method=payment.payment_method.value,
        reference_number=payment.external_transaction_id,
        notes=payment.notes,
        payment_date=payment.payment_date.date() if payment.payment_date else date.today(),
        recorded_by=payment.processed_by_id,
        created_at=payment.created_at,
    )


async def list_payments(
    session: AsyncSession,
    pagination: PaginationParams,
    invoice_id: UUID | None = None,
) -> PaginatedResponse[PaymentRead]:
    """List payments with optional invoice filter."""
    query = select(Payment)
    if invoice_id:
        query = query.where(Payment.invoice_id == invoice_id)
    query = query.order_by(Payment.payment_date.desc())
    result = await paginate(session, query, pagination)
    result.items = [
        PaymentRead(
            id=p.id,
            invoice_id=p.invoice_id,
            amount=p.amount,
            payment_method=p.payment_method.value,
            reference_number=p.external_transaction_id,
            notes=p.notes,
            payment_date=p.payment_date.date() if p.payment_date else date.today(),
            recorded_by=p.processed_by_id,
            created_at=p.created_at,
        )
        for p in result.items
    ]
    return result


# --- Summary ---

async def compute_billing_summary(
    session: AsyncSession,
    period_start: date | None = None,
    period_end: date | None = None,
    client_id: UUID | None = None,
) -> BillingSummary:
    """Compute billing summary with aggregate financials."""
    base_query = select(Invoice).where(Invoice.is_deleted == False)

    if client_id:
        base_query = base_query.where(Invoice.client_id == client_id)
    if period_start:
        base_query = base_query.where(Invoice.created_at >= datetime.combine(period_start, datetime.min.time()))
    if period_end:
        base_query = base_query.where(Invoice.created_at <= datetime.combine(period_end, datetime.max.time()))

    result = await session.execute(base_query)
    invoices = result.scalars().all()

    total_invoiced = Decimal("0.00")
    total_collected = Decimal("0.00")
    total_outstanding = Decimal("0.00")
    overdue_amount = Decimal("0.00")
    paid_count = 0
    overdue_count = 0
    payment_days: list[int] = []

    today = date.today()

    for inv in invoices:
        total_invoiced += inv.total_amount
        total_collected += inv.amount_paid
        balance_due = inv.total_amount - inv.amount_paid
        total_outstanding += balance_due

        if inv.status == ModelInvoiceStatus.PAID:
            paid_count += 1
            if inv.paid_date and inv.created_at:
                delta = (inv.paid_date - inv.created_at.date()).days
                payment_days.append(delta)

        if balance_due > 0 and inv.due_date < today and inv.status not in (
            ModelInvoiceStatus.PAID,
            ModelInvoiceStatus.CANCELLED,
            ModelInvoiceStatus.REFUNDED,
        ):
            overdue_count += 1
            overdue_amount += balance_due

    avg_days = sum(payment_days) / len(payment_days) if payment_days else None

    return BillingSummary(
        total_invoiced=total_invoiced,
        total_collected=total_collected,
        total_outstanding=total_outstanding,
        overdue_amount=overdue_amount,
        invoices_count=len(invoices),
        paid_count=paid_count,
        overdue_count=overdue_count,
        average_days_to_payment=avg_days,
        period_start=period_start,
        period_end=period_end,
    )
