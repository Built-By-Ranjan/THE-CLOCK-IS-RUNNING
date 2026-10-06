import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    """Raised when OTP email delivery fails."""
    pass


class EmailService:
    @staticmethod
    def send_otp_email(to_email: str, otp: str) -> bool:
        """
        Send the 6-digit MFA OTP verification code to the specified email via Gmail SMTP.
        Ensures credentials and plaintext OTP are never logged or leaked.
        Does not connect during startup; establishes an ephemeral connection on demand.
        """
        if not settings.SMTP_HOST:
            logger.error("SMTP host is not configured.")
            raise EmailDeliveryError("SMTP service is not configured.")

        # Build message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "THE CLOCK IS RUNNING — Your Security Verification Code"
        from_address = settings.SMTP_FROM or settings.SMTP_USERNAME or "noreply@security.local"
        msg["From"] = from_address
        msg["To"] = to_email

        plain_text = (
            f"Hello,\n\n"
            f"Your security verification code for signing into {settings.PROJECT_NAME} is:\n\n"
            f"    {otp}\n\n"
            f"This code will expire in {settings.OTP_EXPIRY_MINUTES} minutes.\n"
            f"For your security, do not share this code with anyone.\n\n"
            f"If you did not request this verification code, please contact your security administrator immediately.\n"
        )

        html_text = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Security Verification Code</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px; color: #1e293b;">
  <div style="max-width: 480px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.1em; color: #64748b; text-transform: uppercase; margin-bottom: 8px;">
      {settings.PROJECT_NAME}
    </div>
    <h2 style="font-size: 20px; font-weight: 700; color: #0f172a; margin-top: 0; margin-bottom: 16px;">
      Security Verification Code
    </h2>
    <p style="font-size: 14px; line-height: 1.5; color: #475569; margin-bottom: 24px;">
      Use the following single-use code to sign into <strong>{settings.PROJECT_NAME}</strong>:
    </p>
    <div style="background-color: #f1f5f9; border-radius: 6px; padding: 16px; text-align: center; margin-bottom: 24px;">
      <span style="font-size: 32px; font-weight: 700; letter-spacing: 0.25em; font-family: monospace; color: #0f172a;">
        {otp}
      </span>
    </div>
    <p style="font-size: 13px; color: #64748b; line-height: 1.4; margin-bottom: 8px;">
      &bull; This code expires in <strong>{settings.OTP_EXPIRY_MINUTES} minutes</strong>.<br>
      &bull; Do not share this code with anyone.
    </p>
    <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8;">
      If you did not initiate this login request, please alert your SOC administrator immediately.
    </div>
  </div>
</body>
</html>"""

        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(html_text, "html", "utf-8"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10.0) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            return True
        except (smtplib.SMTPException, OSError) as exc:
            logger.error("Failed to deliver security verification email: %s", type(exc).__name__)
            raise EmailDeliveryError("Failed to deliver security verification code.") from exc
