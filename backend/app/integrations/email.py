"""Email adapter using SMTP."""

from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


class EmailAdapter:
    """SMTP-based email sending adapter."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        self.host = host or settings.SMTP_HOST
        self.port = port or settings.SMTP_PORT
        self.user = user or settings.SMTP_USER
        self.password = password or settings.SMTP_PASSWORD

    def _get_connection(self) -> smtplib.SMTP:
        server = smtplib.SMTP(self.host, self.port)
        server.starttls()
        if self.user and self.password:
            server.login(self.user, self.password)
        return server

    def send(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str | None = None,
        from_email: str | None = None,
        reply_to: str | None = None,
    ) -> bool:
        """Send an email via SMTP. Returns True on success."""
        sender = from_email or self.user or f"noreply@{settings.APP_NAME.lower()}.org"
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email
        if reply_to:
            msg["Reply-To"] = reply_to

        if body_text:
            msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        try:
            with self._get_connection() as server:
                server.sendmail(sender, [to_email], msg.as_string())
            logger.info("Email sent to %s: %s", to_email, subject)
            return True
        except smtplib.SMTPException:
            logger.exception("Failed to send email to %s", to_email)
            return False

    def send_bulk(
        self,
        recipients: list[str],
        subject: str,
        body_html: str,
        body_text: str | None = None,
        from_email: str | None = None,
    ) -> dict[str, bool]:
        """Send the same email to multiple recipients. Returns {email: success}."""
        results: dict[str, bool] = {}
        for email in recipients:
            results[email] = self.send(email, subject, body_html, body_text, from_email)
        return results


email_adapter = EmailAdapter()
