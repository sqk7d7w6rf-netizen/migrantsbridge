"""Scheduling and appointment API routes."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.pagination import PaginatedResponse, PaginationParams
from app.core.security import get_current_user
from app.schemas.common import SuccessResponse
from app.schemas.scheduling import (
    AppointmentCreate,
    AppointmentRead,
    AppointmentUpdate,
    AvailabilitySlotCreate,
    AvailabilitySlotRead,
    ReminderCreate,
)
from app.services import scheduling_service

router = APIRouter()


# --- Appointments ---

@router.post("/appointments", response_model=AppointmentRead, status_code=201)
async def create_appointment(
    payload: AppointmentCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Create a new appointment with conflict detection."""
    return await scheduling_service.create_appointment(session, payload)


@router.get("/appointments", response_model=PaginatedResponse[AppointmentRead])
async def list_appointments(
    pagination: PaginationParams = Depends(),
    staff_id: UUID | None = None,
    client_id: UUID | None = None,
    status: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List appointments with filters."""
    return await scheduling_service.list_appointments(
        session, pagination, staff_id, client_id, status, start_date, end_date
    )


@router.get("/appointments/{appointment_id}", response_model=AppointmentRead)
async def get_appointment(
    appointment_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get an appointment by ID."""
    return await scheduling_service.get_appointment(session, appointment_id)


@router.put("/appointments/{appointment_id}", response_model=AppointmentRead)
async def update_appointment(
    appointment_id: UUID,
    payload: AppointmentUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update an appointment."""
    return await scheduling_service.update_appointment(session, appointment_id, payload)


@router.post("/appointments/{appointment_id}/cancel", response_model=AppointmentRead)
async def cancel_appointment(
    appointment_id: UUID,
    reason: str | None = Query(default=None),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Cancel an appointment."""
    return await scheduling_service.cancel_appointment(session, appointment_id, reason)


# --- Availability ---

@router.post("/availability", response_model=AvailabilitySlotRead, status_code=201)
async def create_availability_slot(
    payload: AvailabilitySlotCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Create an availability slot for a staff member."""
    return await scheduling_service.create_availability_slot(session, payload)


@router.get("/availability/{staff_id}", response_model=list[AvailabilitySlotRead])
async def list_availability(
    staff_id: UUID,
    target_date: date | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get availability slots for a staff member."""
    return await scheduling_service.list_availability(session, staff_id, target_date)


@router.get("/availability/{staff_id}/slots")
async def get_available_slots(
    staff_id: UUID,
    target_date: date = Query(...),
    duration_minutes: int = Query(default=60, ge=15, le=480),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Compute available time slots for a staff member on a given date."""
    return await scheduling_service.compute_available_slots(
        session, staff_id, target_date, duration_minutes
    )


# --- Calendar ---

@router.get("/calendar", response_model=list[AppointmentRead])
async def get_calendar(
    start_date: date = Query(...),
    end_date: date = Query(...),
    staff_id: UUID | None = None,
    client_id: UUID | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get a calendar view of appointments for a date range."""
    return await scheduling_service.get_calendar_view(
        session, start_date, end_date, staff_id, client_id
    )


# --- Reminders ---

@router.post("/reminders", status_code=201)
async def create_reminder(
    payload: ReminderCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Create an appointment reminder."""
    return await scheduling_service.create_reminder(session, payload)
