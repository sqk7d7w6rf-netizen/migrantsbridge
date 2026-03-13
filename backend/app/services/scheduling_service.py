"""Scheduling service with appointment management and conflict detection."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import AppointmentStatus as ModelAppointmentStatus
from app.constants import AppointmentType as ModelAppointmentType
from app.constants import DayOfWeek, ReminderType
from app.core.pagination import PaginatedResponse, PaginationParams, paginate
from app.models.scheduling import Appointment, Reminder, StaffAvailability
from app.models.client import Client
from app.models.user import User
from app.schemas.scheduling import (
    AppointmentCreate,
    AppointmentRead,
    AppointmentStatus,
    AppointmentUpdate,
    AvailabilitySlotCreate,
    AvailabilitySlotRead,
    ReminderCreate,
)


async def _get_appointment_or_404(session: AsyncSession, appt_id: UUID) -> Appointment:
    result = await session.execute(
        select(Appointment).where(Appointment.id == appt_id, Appointment.is_deleted == False)
    )
    appt = result.scalar_one_or_none()
    if appt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appt


def _build_appointment_read(appt: Appointment) -> AppointmentRead:
    """Map Appointment model to schema using selectin-loaded relationships."""
    client_name = None
    if appt.client:
        client_name = f"{appt.client.first_name} {appt.client.last_name}"

    staff_name = None
    if appt.staff:
        staff_name = f"{appt.staff.first_name} {appt.staff.last_name}"

    return AppointmentRead(
        id=appt.id,
        client_id=appt.client_id,
        client_name=client_name,
        case_id=appt.case_id,
        staff_id=appt.staff_id,
        staff_name=staff_name,
        appointment_type=appt.appointment_type.value,
        title=appt.title,
        description=appt.description,
        start_time=appt.start_time,
        end_time=appt.end_time,
        status=appt.status.value,
        location=appt.location,
        is_virtual=bool(appt.meeting_link),
        meeting_link=appt.meeting_link,
        cancellation_reason=appt.cancellation_reason,
        created_at=appt.created_at,
        updated_at=appt.updated_at,
    )


async def _check_conflicts(
    session: AsyncSession,
    staff_id: UUID,
    start_time: datetime,
    end_time: datetime,
    exclude_id: UUID | None = None,
) -> None:
    """Check for scheduling conflicts with existing appointments."""
    query = select(Appointment).where(
        Appointment.staff_id == staff_id,
        Appointment.is_deleted == False,
        Appointment.status.notin_([
            ModelAppointmentStatus.CANCELLED,
            ModelAppointmentStatus.RESCHEDULED,
        ]),
        # Overlap check: existing.start < new.end AND existing.end > new.start
        Appointment.start_time < end_time,
        Appointment.end_time > start_time,
    )
    if exclude_id:
        query = query.where(Appointment.id != exclude_id)

    result = await session.execute(query)
    conflict = result.scalar_one_or_none()
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Scheduling conflict with appointment '{conflict.title}' "
                   f"({conflict.start_time.isoformat()} - {conflict.end_time.isoformat()})",
        )


async def create_appointment(
    session: AsyncSession, payload: AppointmentCreate
) -> AppointmentRead:
    """Create a new appointment with conflict detection."""
    # Verify client
    client_result = await session.execute(
        select(Client).where(Client.id == payload.client_id, Client.is_deleted == False)
    )
    if client_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    # Verify staff
    staff_result = await session.execute(
        select(User).where(User.id == payload.staff_id, User.is_active == True)
    )
    if staff_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff user not found")

    # Check conflicts
    await _check_conflicts(session, payload.staff_id, payload.start_time, payload.end_time)

    # Map schema appointment_type to model enum
    try:
        model_appt_type = ModelAppointmentType(payload.appointment_type.value)
    except ValueError:
        model_appt_type = ModelAppointmentType.OTHER

    appt = Appointment(
        client_id=payload.client_id,
        case_id=payload.case_id,
        staff_id=payload.staff_id,
        appointment_type=model_appt_type,
        title=payload.title,
        description=payload.description,
        start_time=payload.start_time,
        end_time=payload.end_time,
        status=ModelAppointmentStatus.SCHEDULED,
        location=payload.location,
        meeting_link=payload.meeting_link,
    )
    session.add(appt)
    await session.flush()
    await session.refresh(appt)

    return _build_appointment_read(appt)


async def get_appointment(session: AsyncSession, appt_id: UUID) -> AppointmentRead:
    """Get an appointment by ID."""
    appt = await _get_appointment_or_404(session, appt_id)
    return _build_appointment_read(appt)


async def list_appointments(
    session: AsyncSession,
    pagination: PaginationParams,
    staff_id: UUID | None = None,
    client_id: UUID | None = None,
    status_filter: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> PaginatedResponse[AppointmentRead]:
    """List appointments with filters."""
    query = select(Appointment).where(Appointment.is_deleted == False)

    if staff_id:
        query = query.where(Appointment.staff_id == staff_id)
    if client_id:
        query = query.where(Appointment.client_id == client_id)
    if status_filter:
        try:
            query = query.where(Appointment.status == ModelAppointmentStatus(status_filter))
        except ValueError:
            pass
    if start_date:
        query = query.where(Appointment.start_time >= datetime.combine(start_date, time.min))
    if end_date:
        query = query.where(Appointment.start_time <= datetime.combine(end_date, time.max))

    query = query.order_by(Appointment.start_time.asc())
    result = await paginate(session, query, pagination)
    result.items = [_build_appointment_read(appt) for appt in result.items]
    return result


async def update_appointment(
    session: AsyncSession, appt_id: UUID, payload: AppointmentUpdate
) -> AppointmentRead:
    """Update an appointment."""
    appt = await _get_appointment_or_404(session, appt_id)

    update_data = payload.model_dump(exclude_unset=True)

    # Check for conflicts if times are changing
    new_start = update_data.get("start_time", appt.start_time)
    new_end = update_data.get("end_time", appt.end_time)
    if "start_time" in update_data or "end_time" in update_data:
        await _check_conflicts(session, appt.staff_id, new_start, new_end, exclude_id=appt.id)

    for field, value in update_data.items():
        if field == "appointment_type" and value is not None:
            try:
                setattr(appt, field, ModelAppointmentType(value.value if hasattr(value, "value") else value))
            except ValueError:
                setattr(appt, field, ModelAppointmentType.OTHER)
        elif field == "status" and value is not None:
            try:
                setattr(appt, field, ModelAppointmentStatus(value.value if hasattr(value, "value") else value))
            except ValueError:
                pass
        elif field == "is_virtual":
            # No direct is_virtual field on model; skip
            continue
        else:
            setattr(appt, field, value)

    session.add(appt)
    await session.flush()
    await session.refresh(appt)

    return _build_appointment_read(appt)


async def cancel_appointment(
    session: AsyncSession, appt_id: UUID, reason: str | None = None, cancelled_by: UUID | None = None
) -> AppointmentRead:
    """Cancel an appointment."""
    appt = await _get_appointment_or_404(session, appt_id)
    appt.status = ModelAppointmentStatus.CANCELLED
    if reason:
        appt.cancellation_reason = reason
    if cancelled_by:
        appt.cancelled_by_id = cancelled_by
    session.add(appt)
    await session.flush()
    return _build_appointment_read(appt)


# --- Availability ---

# Map integer day_of_week (0=Monday) to DayOfWeek enum
_DAY_MAP = {
    0: DayOfWeek.MONDAY,
    1: DayOfWeek.TUESDAY,
    2: DayOfWeek.WEDNESDAY,
    3: DayOfWeek.THURSDAY,
    4: DayOfWeek.FRIDAY,
    5: DayOfWeek.SATURDAY,
    6: DayOfWeek.SUNDAY,
}

_DAY_REVERSE_MAP = {v: k for k, v in _DAY_MAP.items()}


async def create_availability_slot(
    session: AsyncSession, payload: AvailabilitySlotCreate
) -> AvailabilitySlotRead:
    """Create an availability slot for a staff member."""
    day_enum = _DAY_MAP.get(payload.day_of_week, DayOfWeek.MONDAY)

    slot = StaffAvailability(
        user_id=payload.staff_id,
        day_of_week=day_enum,
        start_time=payload.start_time,
        end_time=payload.end_time,
        is_active=True,
    )
    session.add(slot)
    await session.flush()
    await session.refresh(slot)

    return AvailabilitySlotRead(
        id=slot.id,
        staff_id=slot.user_id,
        day_of_week=_DAY_REVERSE_MAP.get(slot.day_of_week, 0),
        start_time=slot.start_time,
        end_time=slot.end_time,
        is_recurring=True,
        specific_date=None,
        is_active=slot.is_active,
        created_at=slot.created_at,
    )


async def list_availability(
    session: AsyncSession,
    staff_id: UUID,
    target_date: date | None = None,
) -> list[AvailabilitySlotRead]:
    """Get availability slots for a staff member."""
    query = select(StaffAvailability).where(
        StaffAvailability.user_id == staff_id,
        StaffAvailability.is_active == True,
    )

    if target_date:
        day_of_week_int = target_date.weekday()
        day_enum = _DAY_MAP.get(day_of_week_int, DayOfWeek.MONDAY)
        query = query.where(StaffAvailability.day_of_week == day_enum)

    query = query.order_by(StaffAvailability.day_of_week, StaffAvailability.start_time)
    result = await session.execute(query)
    slots = result.scalars().all()

    return [
        AvailabilitySlotRead(
            id=s.id,
            staff_id=s.user_id,
            day_of_week=_DAY_REVERSE_MAP.get(s.day_of_week, 0),
            start_time=s.start_time,
            end_time=s.end_time,
            is_recurring=True,
            specific_date=None,
            is_active=s.is_active,
            created_at=s.created_at,
        )
        for s in slots
    ]


async def compute_available_slots(
    session: AsyncSession,
    staff_id: UUID,
    target_date: date,
    duration_minutes: int = 60,
) -> list[dict]:
    """Compute available time slots for a given day, considering existing appointments.

    Returns a list of {start_time, end_time} dicts representing open slots.
    """
    # Get availability
    availability = await list_availability(session, staff_id, target_date)
    if not availability:
        return []

    # Get existing appointments for that day
    day_start = datetime.combine(target_date, time.min)
    day_end = datetime.combine(target_date, time.max)

    appt_result = await session.execute(
        select(Appointment).where(
            Appointment.staff_id == staff_id,
            Appointment.is_deleted == False,
            Appointment.status.notin_([
                ModelAppointmentStatus.CANCELLED,
                ModelAppointmentStatus.RESCHEDULED,
            ]),
            Appointment.start_time >= day_start,
            Appointment.start_time <= day_end,
        ).order_by(Appointment.start_time)
    )
    existing = appt_result.scalars().all()

    available: list[dict] = []
    duration = timedelta(minutes=duration_minutes)

    for slot in availability:
        slot_start = datetime.combine(target_date, slot.start_time)
        slot_end = datetime.combine(target_date, slot.end_time)

        current = slot_start
        while current + duration <= slot_end:
            candidate_end = current + duration
            # Check if this slot overlaps with any existing appointment
            has_conflict = False
            for appt in existing:
                if current < appt.end_time and candidate_end > appt.start_time:
                    has_conflict = True
                    # Jump past this appointment
                    current = appt.end_time
                    break

            if not has_conflict:
                available.append({
                    "start_time": current.isoformat(),
                    "end_time": candidate_end.isoformat(),
                })
                current = candidate_end
            # If there was a conflict, current was already advanced

    return available


async def get_calendar_view(
    session: AsyncSession,
    start_date: date,
    end_date: date,
    staff_id: UUID | None = None,
    client_id: UUID | None = None,
) -> list[AppointmentRead]:
    """Get a calendar view of appointments for a date range."""
    query = select(Appointment).where(
        Appointment.is_deleted == False,
        Appointment.start_time >= datetime.combine(start_date, time.min),
        Appointment.start_time <= datetime.combine(end_date, time.max),
    )

    if staff_id:
        query = query.where(Appointment.staff_id == staff_id)
    if client_id:
        query = query.where(Appointment.client_id == client_id)

    query = query.order_by(Appointment.start_time.asc())
    result = await session.execute(query)
    appointments = result.scalars().all()

    return [_build_appointment_read(appt) for appt in appointments]


# --- Reminders ---

async def create_reminder(session: AsyncSession, payload: ReminderCreate) -> dict:
    """Create an appointment reminder."""
    # Verify appointment exists
    await _get_appointment_or_404(session, payload.appointment_id)

    # Map ReminderMethod to ReminderType
    method_map = {
        "email": ReminderType.EMAIL,
        "sms": ReminderType.SMS,
        "both": ReminderType.EMAIL,
    }
    reminder_type = method_map.get(payload.method.value, ReminderType.EMAIL)

    reminder = Reminder(
        appointment_id=payload.appointment_id,
        reminder_type=reminder_type,
        scheduled_at=payload.remind_at,
        is_sent=False,
    )
    session.add(reminder)
    await session.flush()
    await session.refresh(reminder)

    return {
        "id": str(reminder.id),
        "appointment_id": str(reminder.appointment_id),
        "remind_at": reminder.scheduled_at.isoformat(),
        "method": payload.method.value,
        "is_sent": reminder.is_sent,
    }
