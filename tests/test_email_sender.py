"""Tests for the email sender."""

from unittest.mock import MagicMock, patch

import pytest

from modules.email_sender import send_email


@patch("modules.email_sender.add_email_log")
@patch("modules.email_sender.smtplib.SMTP")
def test_send_email_success(mock_smtp, mock_log):
    """Record a successful SMTP send."""
    server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = server

    with patch.dict(
        "os.environ",
        {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_USERNAME": "test@example.com",
            "SMTP_PASSWORD": "test-password",
            "SENDER_EMAIL": "test@example.com",
        },
    ):
        send_email("recipient@example.com", "Test", "Hello")

    server.send_message.assert_called_once()
    mock_log.assert_called_once_with(
        "recipient@example.com",
        "Test",
        "sent",
    )


@patch("modules.email_sender.add_email_log")
def test_send_email_missing_configuration(mock_log):
    """Reject missing SMTP settings and log the failure."""
    with (
        patch.dict("os.environ", {}, clear=True),
        pytest.raises(ValueError, match="Missing SMTP configuration"),
    ):
        send_email("recipient@example.com", "Test", "Hello")

    mock_log.assert_called_once()
    assert mock_log.call_args.args[2] == "failed"
