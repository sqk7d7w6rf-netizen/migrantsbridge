"""Celery tasks for appointment reminders."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Helper to run async code in a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task
def send_appointment_reminders() -> dict:
    """Periodic task to send appointment reminders.

    Finds reminders that are due (scheduled_at <= now and not yet sent),
    sends them via the appropriate channel, and marks them as sent.

    Should be scheduled via Celery Beat to run every 5-15 minutes.
    """
    logger.info("Checking for due appointment reminders")

    async def _process():
        from uuid import UUID

        from sqlalchemy import select

        from app.constants import ReminderType
        from app.core.database import async_session_factory
        from app.integrations.email import email_adapter
        from app.integrations.sms import sms_adapter
        from app.models.client import Client
        from app.models.scheduling import Appointment, Reminder

        now = datetime.now(timezone.utc)
        sent_count = 0
        failed_count = 0

        async with async_session_factory() as session:
            result = await session.execute(
                select(Reminder).where(
                    Reminder.is_sent == False,
                    Reminder.scheduled_at <= now,
                )
            )
            reminders = result.scalars().all()

            if not reminders:
                logger.info("No due reminders found")
                return {"status": "success", "sent": 0, "failed": 0}

            for reminder in reminders:
                try:
                    # Get appointment details (uses selectin relationship)
                    appointment = reminder.appointment
                    if appointment is None:
                        appt_result = await session.execute(
                            select(Appointment).where(Appointment.id == reminder.appointment_id)
                        )
                        appointment = appt_result.scalar_one_or_none()

                    if appointment is None:
                        reminder.is_sent = True
                        session.add(reminder)
                        continue

                    # Get client details (uses selectin relationship)
                    client = appointment.client
                    if client is None:
                        client_result = await session.execute(
                            select(Client).where(Client.id == appointment.client_id)
                        )
                        client = client_result.scalar_one_or_none()

                    if client is None:
                        reminder.is_sent = True
                        session.add(reminder)
                        continue

                    # Build message
                    message = (
                        f"Reminder: You have an appointment '{appointment.title}' "
                        f"scheduled for {appointment.start_time.strftime('%B %d, %Y at %I:%M %p')}"
                    )
                    if appointment.location:
                        message += f" at {appointment.location}"
                    if appointment.meeting_link:
                        message += f". Join link: {appointment.meeting_link}"

                    success = False
                    reminder_type = reminder.reminder_type

                    if reminder_type in (ReminderType.EMAIL, ) and client.email:
                        subject = f"Appointment Reminder: {appointment.title}"
                        html_body = f"<p>{message}</p>"
                        email_success = email_adapter.send(
                            to_email=client.email,
                            subject=subject,
                            body_html=html_body,
                            body_text=message,
                        )
                        success = success or email_success

                    if reminder_type in (ReminderType.SMS, ) and client.phone:
                        sms_result = sms_adapter.send(to_number=client.phone, body=message)
                        success = success or (sms_result is not None)

                    if reminder_type == ReminderType.IN_APP:
                        # In-app reminders don't need external sending
                        success = True

                    reminder.is_sent = True
                    reminder.sent_at = now
                    session.add(reminder)

                    if success:
                        sent_count += 1
                        logger.info(
                            "Reminder sent for appointment %s to client %s via %s",
                            appointment.id,
                            client.id,
                            reminder_type.value,
                        )
                    else:
                        failed_count += 1
                        logger.warning(
                            "Reminder delivery failed for appointment %s",
                            appointment.id,
                        )

                except Exception:
                    failed_count += 1
                    logger.exception("Error processing reminder %s", reminder.id)
                    # Still mark as sent to avoid infinite retries
                    reminder.is_sent = True
                    session.add(reminder)

            await session.commit()

        logger.info("Reminder task complete: %d sent, %d failed", sent_count, failed_count)
        return {"status": "success", "sent": sent_count, "failed": failed_count}

    return _run_async(_process())
