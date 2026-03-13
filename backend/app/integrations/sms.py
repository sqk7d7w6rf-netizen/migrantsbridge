"""SMS adapter with Twilio integration."""

from __future__ import annotations

import logging

from app.config import settings

logger = logging.getLogger(__name__)


class SMSAdapter:
    """Twilio-based SMS sending adapter."""

    def __init__(
        self,
        account_sid: str | None = None,
        auth_token: str | None = None,
        from_number: str | None = None,
    ) -> None:
        self.account_sid = account_sid or settings.TWILIO_ACCOUNT_SID
        self.auth_token = auth_token or settings.TWILIO_AUTH_TOKEN
        self.from_number = from_number or settings.TWILIO_PHONE_NUMBER
        self._client = None

    def _get_client(self):
        """Lazily initialize the Twilio client."""
        if self._client is None:
            try:
                from twilio.rest import Client
                self._client = Client(self.account_sid, self.auth_token)
            except ImportError:
                logger.warning("twilio package not installed; SMS sending will be a no-op")
                return None
        return self._client

    def send(self, to_number: str, body: str) -> dict | None:
        """Send an SMS message. Returns message SID info or None on failure."""
        client = self._get_client()
        if client is None:
            logger.warning("SMS not sent (no client): to=%s body=%s", to_number, body[:50])
            return None

        try:
            message = client.messages.create(
                body=body,
                from_=self.from_number,
                to=to_number,
            )
            logger.info("SMS sent to %s, SID: %s", to_number, message.sid)
            return {
                "sid": message.sid,
                "status": message.status,
                "to": to_number,
            }
        except Exception:
            logger.exception("Failed to send SMS to %s", to_number)
            return None

    def send_bulk(self, recipients: list[str], body: str) -> dict[str, dict | None]:
        """Send the same SMS to multiple phone numbers."""
        results: dict[str, dict | None] = {}
        for phone in recipients:
            results[phone] = self.send(phone, body)
        return results


sms_adapter = SMSAdapter()
