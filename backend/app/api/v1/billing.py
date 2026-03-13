"""Billing API routes: invoices, payments, service fees, summary."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.pagination import PaginatedResponse, PaginationParams
from app.core.security import get_current_user
from app.schemas.billing import (
    BillingSummary,
    InvoiceCreate,
    InvoiceRead,
    InvoiceUpdate,
    PaymentCreate,
    PaymentRead,
    ServiceFeeCreate,
    ServiceFeeRead,
)
from app.schemas.common import SuccessResponse
from app.services import billing_service

router = APIRouter()


# --- Service Fees ---

@router.post("/service-fees", response_model=ServiceFeeRead, status_code=201)
async def create_service_fee(
    payload: ServiceFeeCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Create a service fee definition."""
    return await billing_service.create_service_fee(session, payload)


@router.get("/service-fees", response_model=PaginatedResponse[ServiceFeeRead])
async def list_service_fees(
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List service fee definitions."""
    return await billing_service.list_service_fees(session, pagination)


# --- Invoices ---

@router.post("/invoices", response_model=InvoiceRead, status_code=201)
async def create_invoice(
    payload: InvoiceCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Create a new invoice with line items."""
    return await billing_service.create_invoice(session, payload, current_user.id)


@router.get("/invoices", response_model=PaginatedResponse[InvoiceRead])
async def list_invoices(
    pagination: PaginationParams = Depends(),
    client_id: UUID | None = None,
    status: str | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List invoices with filters."""
    return await billing_service.list_invoices(session, pagination, client_id, status)


@router.get("/invoices/{invoice_id}", response_model=InvoiceRead)
async def get_invoice(
    invoice_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get an invoice by ID."""
    return await billing_service.get_invoice(session, invoice_id)


@router.put("/invoices/{invoice_id}", response_model=InvoiceRead)
async def update_invoice(
    invoice_id: UUID,
    payload: InvoiceUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update an invoice."""
    return await billing_service.update_invoice(session, invoice_id, payload)


@router.delete("/invoices/{invoice_id}", response_model=SuccessResponse)
async def delete_invoice(
    invoice_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Delete a draft or cancelled invoice."""
    await billing_service.delete_invoice(session, invoice_id)
    return SuccessResponse(message="Invoice deleted successfully")


# --- Payments ---

@router.post("/payments", response_model=PaymentRead, status_code=201)
async def record_payment(
    payload: PaymentCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Record a payment against an invoice."""
    return await billing_service.record_payment(session, payload, current_user.id)


@router.get("/payments", response_model=PaginatedResponse[PaymentRead])
async def list_payments(
    pagination: PaginationParams = Depends(),
    invoice_id: UUID | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List payments."""
    return await billing_service.list_payments(session, pagination, invoice_id)


# --- Summary ---

@router.get("/summary", response_model=BillingSummary)
async def get_billing_summary(
    period_start: date | None = None,
    period_end: date | None = None,
    client_id: UUID | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get billing summary with aggregate financials."""
    return await billing_service.compute_billing_summary(
        session, period_start, period_end, client_id
    )
