"""Celery tasks for sending notifications via email and SMS."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Helper to run async code in a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_email(self, notification_id: str) -> dict:
    """Send an email notification."""
    logger.info("Sending email notification %s", notification_id)

    async def _send():
        from uuid import UUID

        from sqlalchemy import select

        from app.constants import NotificationStatus
        from app.core.database import async_session_factory
        from app.integrations.email import email_adapter
        from app.models.communication import Notification
        from app.models.user import User

        async with async_session_factory() as session:
            result = await session.execute(
                select(Notification).where(Notification.id == UUID(notification_id))
            )
            notif = result.scalar_one_or_none()
            if notif is None:
                logger.error("Notification %s not found", notification_id)
                return {"status": "error", "message": "Notification not found"}

            # Get recipient email
            user_result = await session.execute(
                select(User).where(User.id == notif.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user is None or not user.email:
                notif.status = NotificationStatus.FAILED
                session.add(notif)
                await session.commit()
                return {"status": "error", "message": "Recipient email not found"}

            subject = notif.title or "Notification from MigrantsBridge"
            success = email_adapter.send(
                to_email=user.email,
                subject=subject,
                body_html=notif.message,
                body_text=notif.message,
            )

            if success:
                notif.status = NotificationStatus.SENT
            else:
                notif.status = NotificationStatus.FAILED

            session.add(notif)
            await session.commit()

            logger.info(
                "Email notification %s to %s: %s",
                notification_id,
                user.email,
                "sent" if success else "failed",
            )
            return {"status": "sent" if success else "failed", "email": user.email}

    try:
        return _run_async(_send())
    except Exception as exc:
        logger.exception("Email send task failed for notification %s", notification_id)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_sms(self, notification_id: str) -> dict:
    """Send an SMS notification."""
    logger.info("Sending SMS notification %s", notification_id)

    async def _send():
        from uuid import UUID

        from sqlalchemy import select

        from app.constants import NotificationStatus
        from app.core.database import async_session_factory
        from app.integrations.sms import sms_adapter
        from app.models.communication import Notification
        from app.models.user import User

        async with async_session_factory() as session:
            result = await session.execute(
                select(Notification).where(Notification.id == UUID(notification_id))
            )
            notif = result.scalar_one_or_none()
            if notif is None:
                logger.error("Notification %s not found", notification_id)
                return {"status": "error", "message": "Notification not found"}

            # Get recipient phone
            user_result = await session.execute(
                select(User).where(User.id == notif.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user is None or not user.phone:
                notif.status = NotificationStatus.FAILED
                session.add(notif)
                await session.commit()
                return {"status": "error", "message": "Recipient phone not found"}

            result_sms = sms_adapter.send(to_number=user.phone, body=notif.message)
            success = result_sms is not None

            if success:
                notif.status = NotificationStatus.SENT
            else:
                notif.status = NotificationStatus.FAILED

            session.add(notif)
            await session.commit()

            logger.info(
                "SMS notification %s to %s: %s",
                notification_id,
                user.phone,
                "sent" if success else "failed",
            )
            return {"status": "sent" if success else "failed", "phone": user.phone}

    try:
        return _run_async(_send())
    except Exception as exc:
        logger.exception("SMS send task failed for notification %s", notification_id)
        raise self.retry(exc=exc)
