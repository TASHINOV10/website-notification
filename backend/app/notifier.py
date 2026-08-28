import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger(__name__)


def send_price_change_email(
    to_email: str, watch_name: str, url: str, old_price: float | None, new_price: float
) -> None:
    subject = f"Price change: {watch_name or url}"

    if old_price is None:
        body = (
            f"We started tracking this listing:\n{url}\n\n"
            f"Current price: {new_price}\n"
        )
    else:
        direction = "dropped" if new_price < old_price else "increased"
        diff = abs(new_price - old_price)
        body = (
            f"The price {direction} for:\n{url}\n\n"
            f"Old price: {old_price}\n"
            f"New price: {new_price}\n"
            f"Change: {diff:.2f}\n"
        )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
    except (OSError, smtplib.SMTPException) as exc:
        logger.error("Failed to send notification email to %s: %s", to_email, exc)
        raise
