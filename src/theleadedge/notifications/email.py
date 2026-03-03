"""Async SMTP email sender for TheLeadEdge.

Sends HTML emails via aiosmtplib with STARTTLS.  Designed for the daily
briefing email but usable for any outbound notification.

CRITICAL: NEVER log recipient email addresses or any PII.  Only the
subject line and success/failure status are logged.
"""

from __future__ import annotations

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
import structlog

logger = structlog.get_logger()


class EmailSender:
    """Async SMTP email sender.

    Parameters
    ----------
    host:
        SMTP server hostname (e.g. ``smtp.gmail.com``).
    port:
        SMTP server port (typically 587 for STARTTLS).
    username:
        SMTP authentication username.
    password:
        SMTP authentication password (app-specific password for Gmail).
    from_name:
        Display name for the From header.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        from_name: str = "TheLeadEdge",
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_name = from_name

    async def send(self, to: str, subject: str, html_body: str) -> bool:
        """Send an HTML email.

        Parameters
        ----------
        to:
            Recipient email address.  NEVER logged.
        subject:
            Email subject line (safe to log).
        html_body:
            HTML content body.

        Returns
        -------
        bool
            ``True`` if the email was sent successfully, ``False`` otherwise.
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.username}>"
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html"))

        try:
            await aiosmtplib.send(
                msg,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                start_tls=True,
            )
            logger.info("email_sent", subject=subject)
            return True
        except Exception as exc:
            logger.error("email_send_failed", subject=subject, error=str(exc))
            return False
