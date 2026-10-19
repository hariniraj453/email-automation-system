"""Send email messages using an SMTP server."""

import os
import smtplib
from email.message import EmailMessage


def send_email(
    recipient: str,
    subject: str,
    body: str,
) -> None:
    """Send one email using SMTP configuration from environment variables."""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL", smtp_username or "")

    if not all([smtp_host, smtp_username, smtp_password, sender_email]):
        raise ValueError(
            "Missing SMTP configuration. Check your environment variables."
        )

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)
