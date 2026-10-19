"""Send email messages using SMTP and record delivery attempts."""

import logging
import os
import smtplib
import sqlite3
from email.message import EmailMessage

from dotenv import load_dotenv

from modules.email_logs import add_email_log

load_dotenv()

logger = logging.getLogger(__name__)


def send_email(
    recipient: str,
    subject: str,
    body: str,
) -> None:
    """Send one email and record whether the attempt succeeded."""
    try:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        sender_email = os.getenv("SENDER_EMAIL", smtp_username or "")

        if not all([smtp_host, smtp_username, smtp_password, sender_email]):
            raise ValueError(
                "Missing SMTP configuration. " "Check your environment variables."
            )

        message = EmailMessage()
        message["From"] = sender_email
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(
            smtp_host,
            smtp_port,
            timeout=30,
        ) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

    except (
        ValueError,
        OSError,
        smtplib.SMTPException,
    ) as error:
        try:
            add_email_log(
                recipient,
                subject,
                "failed",
                str(error),
            )
        except (sqlite3.Error, OSError):
            logger.exception("Could not record failed email attempt")

        raise

    else:
        add_email_log(
            recipient,
            subject,
            "sent",
        )
