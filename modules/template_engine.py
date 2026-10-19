"""Create personalized email messages from templates."""

from string import Template


def render_email(
    template: str,
    recipient_name: str,
    **details: str,
) -> str:
    """Replace placeholders with recipient information."""
    values = {"name": recipient_name.strip(), **details}
    return Template(template).safe_substitute(values)


def create_email(
    recipient_name: str,
    subject_template: str,
    body_template: str,
    **details: str,
) -> tuple[str, str]:
    """Generate a personalized email subject and body."""
    subject = render_email(
        subject_template, recipient_name, **details
    )
    body = render_email(
        body_template, recipient_name, **details
    )
    return subject, body
