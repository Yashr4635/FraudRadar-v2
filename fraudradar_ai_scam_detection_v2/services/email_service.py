import os
import smtplib
import ssl
import logging
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple, Optional, Dict, Any, List
import httpx

from fraudradar_ai_scam_detection_v2.services import auth_db

logger = logging.getLogger("fraudradar.email_service")


def mask_email(email: str) -> str:
    """Mask email for privacy in UI and logs (e.g., j*****e@domain.com)."""
    if not email or "@" not in email:
        return email or ""
    parts = email.split("@")
    name = parts[0]
    domain = parts[1]
    if len(name) <= 2:
        masked_name = name[0] + "*"
    else:
        masked_name = name[0] + ("*" * min(len(name) - 2, 6)) + name[-1]
    return f"{masked_name}@{domain}"


class EmailDeliveryResult:
    def __init__(
        self,
        success: bool,
        message: str,
        provider: str = "none",
        error: Optional[str] = None,
    ):
        self.success = success
        self.message = message
        self.provider = provider
        self.error = error

    def __bool__(self):
        return self.success


class EmailService:
    """Unified email delivery service supporting SMTP, Resend, SendGrid, and Dev Outbox."""

    _outbox: List[Dict[str, Any]] = []

    @classmethod
    def get_sender_identity(cls) -> Tuple[str, str]:
        """Get (from_email, from_name) from environment variables."""
        from_email = (
            os.getenv("SMTP_FROM_EMAIL")
            or os.getenv("SMTP_USER")
            or os.getenv("RESEND_FROM_EMAIL")
            or "auth@fraudradar.app"
        ).strip()
        from_name = os.getenv("SMTP_FROM_NAME", "FraudRadar Scam Defense").strip()
        return from_email, from_name

    @classmethod
    def is_configured(cls) -> bool:
        """Check if any valid email provider credentials are configured."""
        if os.getenv("SMTP_HOST") and os.getenv("SMTP_USER") and os.getenv("SMTP_PASSWORD"):
            return True
        if os.getenv("RESEND_API_KEY"):
            return True
        if os.getenv("BREVO_API_KEY"):
            return True
        if os.getenv("SENDGRID_API_KEY"):
            return True
        return False

    @classmethod
    def is_dev_mode(cls) -> bool:
        """Check if running in development / test mock mode."""
        dev_env = os.getenv("EMAIL_DEV_MODE", "").strip().lower()
        if dev_env in ("true", "1", "yes", "on"):
            return True
        # If in a test runner or no SMTP configured and not in strict prod
        return os.getenv("PYTEST_CURRENT_TEST") is not None

    @classmethod
    def render_templates(
        cls,
        recipient_email: str,
        recipient_name: str,
        otp_code: str,
        purpose: str,
        expires_minutes: int = 10,
    ) -> Tuple[str, str, str]:
        """
        Generate (subject, html_content, text_content) for FraudRadar authentication OTP.
        """
        name_display = recipient_name.strip() if recipient_name else "User"
        formatted_code = (
            f"{otp_code[:4]} {otp_code[4:]}" if len(otp_code) == 8 else otp_code
        )

        if purpose == "signup":
            purpose_title = "Verify Your Email Address"
            purpose_desc = (
                "Welcome to FraudRadar Scam Defense AI. Use the 8-digit verification code "
                "below to confirm your email and complete your account registration."
            )
            subject = f"Your FraudRadar Verification Code: {formatted_code}"
        elif purpose == "login":
            purpose_title = "Sign In Verification Code"
            purpose_desc = (
                "A sign-in attempt was initiated for your FraudRadar account. "
                "Use the 8-digit code below to securely authenticate. No password is required."
            )
            subject = f"Your FraudRadar Login Code: {formatted_code}"
        else:
            purpose_title = "Security Verification Code"
            purpose_desc = (
                "A security action was requested for your FraudRadar account. "
                "Please enter the 8-digit code below to verify your identity."
            )
            subject = f"Your FraudRadar Verification Code: {formatted_code}"

        # ── Plain text alternative ──────────────────────────────────────────
        text_content = f"""
Hello {name_display},

{purpose_title}

{purpose_desc}

Your 8-digit verification code is:

    {formatted_code}

This code will expire in {expires_minutes} minutes.

SECURITY NOTICE:
FraudRadar will NEVER call, message, or email you asking for this code.
Never share this code with anyone. If you did not request this verification, please disregard this email.

—
FraudRadar Scam Defense AI
Protecting Citizens Against Digital Scams & Fraud
Helpline: 1930 | https://cybercrime.gov.in
"""

        # ── Premium Responsive HTML template ────────────────────────────────
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{purpose_title}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #F8FAFC;
      margin: 0;
      padding: 0;
      -webkit-font-smoothing: antialiased;
    }}
    .container {{
      max-width: 560px;
      margin: 32px auto;
      background: #ffffff;
      border: 1px solid #E2E8F0;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
    }}
    .header {{
      background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
      padding: 28px 32px;
      text-align: center;
      border-bottom: 3px solid #E8471A;
    }}
    .header h1 {{
      color: #ffffff;
      margin: 8px 0 0;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .header p {{
      color: #94A3B8;
      margin: 4px 0 0;
      font-size: 12px;
      font-weight: 500;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }}
    .content {{
      padding: 36px 32px 28px;
    }}
    .greeting {{
      font-size: 16px;
      font-weight: 600;
      color: #0F172A;
      margin: 0 0 12px;
    }}
    .desc {{
      font-size: 14px;
      line-height: 1.6;
      color: #475569;
      margin: 0 0 28px;
    }}
    .code-box {{
      background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
      border: 2px dashed #FDBA74;
      border-radius: 12px;
      padding: 24px;
      text-align: center;
      margin: 0 0 28px;
    }}
    .code-label {{
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      color: #C2410C;
      margin-bottom: 8px;
    }}
    .code-digits {{
      font-family: 'SF Mono', Monaco, Menlo, Consolas, monospace;
      font-size: 34px;
      font-weight: 800;
      letter-spacing: 8px;
      color: #9A3412;
      margin: 0;
    }}
    .expiry-tag {{
      display: inline-block;
      margin-top: 10px;
      font-size: 12px;
      color: #EA580C;
      font-weight: 600;
    }}
    .security-notice {{
      background: #FEF2F2;
      border: 1px solid #FECACA;
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 24px;
    }}
    .security-notice strong {{
      color: #991B1B;
      font-size: 12px;
      display: block;
      margin-bottom: 4px;
    }}
    .security-notice p {{
      color: #B91C1C;
      font-size: 12px;
      line-height: 1.5;
      margin: 0;
    }}
    .footer {{
      background: #F8FAFC;
      border-top: 1px solid #E2E8F0;
      padding: 24px 32px;
      text-align: center;
      font-size: 12px;
      color: #64748B;
      line-height: 1.6;
    }}
    .footer a {{
      color: #E8471A;
      text-decoration: none;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div style="font-size: 28px; line-height: 1;">🛡️</div>
      <h1>FraudRadar</h1>
      <p>Scam Defense & Verification AI</p>
    </div>
    <div class="content">
      <p class="greeting">Hello {name_display},</p>
      <p class="desc">{purpose_desc}</p>
      
      <div class="code-box">
        <div class="code-label">8-Digit Security Code</div>
        <div class="code-digits">{formatted_code}</div>
        <div class="expiry-tag">⏱️ Valid for {expires_minutes} minutes only</div>
      </div>
      
      <div class="security-notice">
        <strong>⚠️ CRITICAL SECURITY WARNING</strong>
        <p>FraudRadar staff, banks, and government agencies will NEVER ask for this verification code. If someone asks you for this number, they are attempting to scam you.</p>
      </div>

      <p style="font-size: 13px; color: #64748B; margin: 0; line-height: 1.5;">
        If you did not request this authentication code, your account may be secure, but you should verify your recent activity.
      </p>
    </div>
    <div class="footer">
      <p style="margin: 0 0 6px;">FraudRadar AI · Protecting Citizens from Digital Scams</p>
      <p style="margin: 0;">In case of cyber financial fraud, report immediately to Helpline <strong>1930</strong> or <a href="https://cybercrime.gov.in" target="_blank">cybercrime.gov.in</a>.</p>
    </div>
  </div>
</body>
</html>"""

        return subject, html_content, text_content

    @classmethod
    def send_email(
        cls,
        recipient_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        purpose: str = "auth",
    ) -> EmailDeliveryResult:
        """
        Dispatch email using the configured delivery provider.
        Priority:
          1. SMTP (Host + Port + User + Password)
          2. Resend API (RESEND_API_KEY)
          3. SendGrid API (SENDGRID_API_KEY)
          4. Dev Mode / Mock Outbox (when explicitly enabled)
        """
        clean_recipient = recipient_email.strip().lower()
        masked_rec = mask_email(clean_recipient)
        from_email, from_name = cls.get_sender_identity()

        # ── 1. Check if SMTP is configured ──────────────────────────────────
        smtp_host = os.getenv("SMTP_HOST", "").strip()
        smtp_user = os.getenv("SMTP_USER", "").strip()
        smtp_password = os.getenv("SMTP_PASSWORD", "").strip()

        if smtp_host and smtp_user and smtp_password:
            return cls._send_via_smtp(
                clean_recipient,
                masked_rec,
                from_email,
                from_name,
                subject,
                html_content,
                text_content,
                purpose,
            )

        # ── 2. Check Resend API ──────────────────────────────────────────────
        resend_key = os.getenv("RESEND_API_KEY", "").strip()
        if resend_key:
            return cls._send_via_resend(
                clean_recipient,
                masked_rec,
                from_email,
                from_name,
                subject,
                html_content,
                text_content,
                purpose,
                resend_key,
            )

        # ── 3. Check Brevo API ───────────────────────────────────────────────
        brevo_key = os.getenv("BREVO_API_KEY", "").strip()
        if brevo_key:
            return cls._send_via_brevo(
                clean_recipient,
                masked_rec,
                from_email,
                from_name,
                subject,
                html_content,
                text_content,
                purpose,
                brevo_key,
            )

        # ── 4. Check SendGrid API ────────────────────────────────────────────
        sendgrid_key = os.getenv("SENDGRID_API_KEY", "").strip()
        if sendgrid_key:
            return cls._send_via_sendgrid(
                clean_recipient,
                masked_rec,
                from_email,
                from_name,
                subject,
                html_content,
                text_content,
                purpose,
                sendgrid_key,
            )

        # ── 4. Dev / Test Mode Outbox ───────────────────────────────────────
        if cls.is_dev_mode():
            logger.warning(
                f"[EMAIL_DEV_OUTBOX] Sent mock email to {masked_rec} (Purpose: {purpose}, Subject: {subject})"
            )
            item = {
                "recipient": clean_recipient,
                "masked_recipient": masked_rec,
                "subject": subject,
                "html_content": html_content,
                "text_content": text_content,
                "purpose": purpose,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
            cls._outbox.append(item)
            auth_db.log_delivery(
                recipient=masked_rec,
                purpose=purpose,
                status="DEV_OUTBOX",
                provider="mock_outbox",
                error_message="",
            )
            return EmailDeliveryResult(
                success=True,
                message="Verification email dispatched (Dev Outbox).",
                provider="mock_outbox",
            )

        # ── 5. Provider missing in production ───────────────────────────────
        err_msg = (
            "Email service is not configured. Please add SMTP credentials "
            "(SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD) in .env."
        )
        logger.error(f"[EMAIL_FAILED] {err_msg} for recipient {masked_rec}")
        auth_db.log_delivery(
            recipient=masked_rec,
            purpose=purpose,
            status="FAILED",
            provider="none",
            error_message=err_msg,
        )
        return EmailDeliveryResult(
            success=False,
            message=err_msg,
            provider="none",
            error=err_msg,
        )

    @classmethod
    def _send_via_smtp(
        cls,
        recipient: str,
        masked_rec: str,
        from_email: str,
        from_name: str,
        subject: str,
        html_content: str,
        text_content: str,
        purpose: str,
    ) -> EmailDeliveryResult:
        """Deliver email using standard authenticated SMTP with STARTTLS or SSL."""
        smtp_host = os.getenv("SMTP_HOST", "").strip()
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "").strip()
        smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
        use_ssl = (
            os.getenv("SMTP_USE_SSL", "false").lower() in ("true", "1")
            or smtp_port == 465
        )
        use_tls = (
            os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1")
            and not use_ssl
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = recipient

        msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        server = None
        try:
            timeout_sec = 10.0
            context = ssl.create_default_context()

            if use_ssl:
                server = smtplib.SMTP_SSL(
                    smtp_host, smtp_port, context=context, timeout=timeout_sec
                )
            else:
                server = smtplib.SMTP(
                    smtp_host, smtp_port, timeout=timeout_sec
                )
                if use_tls:
                    server.starttls(context=context)

            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, [recipient], msg.as_string())

            logger.info(f"[EMAIL_SENT] Successfully delivered to {masked_rec} via SMTP ({smtp_host})")
            auth_db.log_delivery(
                recipient=masked_rec,
                purpose=purpose,
                status="SENT",
                provider=f"smtp:{smtp_host}",
                error_message="",
            )
            return EmailDeliveryResult(
                success=True,
                message=f"Verification code sent to {masked_rec}.",
                provider="smtp",
            )
        except smtplib.SMTPAuthenticationError as auth_err:
            err_msg = f"SMTP Authentication failed. Please check SMTP_USER and SMTP_PASSWORD: {auth_err}"
            logger.error(f"[SMTP_AUTH_ERROR] {err_msg}")
            auth_db.log_delivery(
                recipient=masked_rec,
                purpose=purpose,
                status="FAILED",
                provider="smtp",
                error_message=err_msg,
            )
            return EmailDeliveryResult(
                success=False,
                message="Email service authentication failed. Please contact support.",
                provider="smtp",
                error=err_msg,
            )
        except smtplib.SMTPRecipientsRefused as rec_err:
            err_msg = f"Recipient email was rejected by the mail server: {rec_err}"
            logger.error(f"[SMTP_REC_ERROR] {err_msg}")
            auth_db.log_delivery(
                recipient=masked_rec,
                purpose=purpose,
                status="FAILED",
                provider="smtp",
                error_message=err_msg,
            )
            return EmailDeliveryResult(
                success=False,
                message="Recipient email was rejected. Please verify your email address.",
                provider="smtp",
                error=err_msg,
            )
        except Exception as e:
            err_msg = f"SMTP delivery error: {str(e)}"
            logger.exception(f"[SMTP_ERROR] {err_msg}")
            auth_db.log_delivery(
                recipient=masked_rec,
                purpose=purpose,
                status="FAILED",
                provider="smtp",
                error_message=err_msg,
            )
            return EmailDeliveryResult(
                success=False,
                message=f"Failed to deliver verification email: {str(e)}",
                provider="smtp",
                error=err_msg,
            )
        finally:
            if server:
                try:
                    server.quit()
                except Exception:
                    pass

    @classmethod
    def _send_via_resend(
        cls,
        recipient: str,
        masked_rec: str,
        from_email: str,
        from_name: str,
        subject: str,
        html_content: str,
        text_content: str,
        purpose: str,
        api_key: str,
    ) -> EmailDeliveryResult:
        """Deliver email using Resend REST API."""
        try:
            payload = {
                "from": f"{from_name} <{from_email}>",
                "to": [recipient],
                "subject": subject,
                "html": html_content,
                "text": text_content,
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    "https://api.resend.com/emails", json=payload, headers=headers
                )
                if resp.status_code in (200, 201):
                    auth_db.log_delivery(
                        recipient=masked_rec,
                        purpose=purpose,
                        status="SENT",
                        provider="resend",
                        error_message="",
                    )
                    return EmailDeliveryResult(
                        success=True,
                        message=f"Verification code sent to {masked_rec}.",
                        provider="resend",
                    )
                else:
                    err_text = resp.text
                    logger.error(f"[RESEND_ERROR] {resp.status_code} - {err_text}")
                    auth_db.log_delivery(
                        recipient=masked_rec,
                        purpose=purpose,
                        status="FAILED",
                        provider="resend",
                        error_message=f"{resp.status_code}: {err_text}",
                    )
                    return EmailDeliveryResult(
                        success=False,
                        message="Failed to send verification code via email provider.",
                        provider="resend",
                        error=err_text,
                    )
        except Exception as e:
            err_msg = f"Resend API error: {str(e)}"
            logger.exception(f"[RESEND_EXCEPTION] {err_msg}")
            auth_db.log_delivery(
                recipient=masked_rec,
                purpose=purpose,
                status="FAILED",
                provider="resend",
                error_message=err_msg,
            )
            return EmailDeliveryResult(
                success=False,
                message="Email delivery service encountered a network error.",
                provider="resend",
                error=err_msg,
            )

    @classmethod
    def _send_via_sendgrid(
        cls,
        recipient: str,
        masked_rec: str,
        from_email: str,
        from_name: str,
        subject: str,
        html_content: str,
        text_content: str,
        purpose: str,
        api_key: str,
    ) -> EmailDeliveryResult:
        """Deliver email using SendGrid REST API."""
        try:
            payload = {
                "personalizations": [{"to": [{"email": recipient}]}],
                "from": {"email": from_email, "name": from_name},
                "subject": subject,
                "content": [
                    {"type": "text/plain", "value": text_content},
                    {"type": "text/html", "value": html_content},
                ],
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    json=payload,
                    headers=headers,
                )
                if resp.status_code in (200, 202):
                    auth_db.log_delivery(
                        recipient=masked_rec,
                        purpose=purpose,
                        status="SENT",
                        provider="sendgrid",
                        error_message="",
                    )
                    return EmailDeliveryResult(
                        success=True,
                        message=f"Verification code sent to {masked_rec}.",
                        provider="sendgrid",
                    )
                else:
                    err_text = resp.text
                    logger.error(f"[SENDGRID_ERROR] {resp.status_code} - {err_text}")
                    auth_db.log_delivery(
                        recipient=masked_rec,
                        purpose=purpose,
                        status="FAILED",
                        provider="sendgrid",
                        error_message=f"{resp.status_code}: {err_text}",
                    )
                    return EmailDeliveryResult(
                        success=False,
                        message="Failed to send verification code via email provider.",
                        provider="sendgrid",
                        error=err_text,
                    )
        except Exception as e:
            err_msg = f"SendGrid API error: {str(e)}"
            logger.exception(f"[SENDGRID_EXCEPTION] {err_msg}")
            auth_db.log_delivery(
                recipient=masked_rec,
                purpose=purpose,
                status="FAILED",
                provider="sendgrid",
                error_message=err_msg,
            )
            return EmailDeliveryResult(
                success=False,
                message="Email delivery service encountered a network error.",
                provider="sendgrid",
                error=err_msg,
            )

    @classmethod
    def _send_via_brevo(
        cls,
        recipient: str,
        masked_rec: str,
        from_email: str,
        from_name: str,
        subject: str,
        html_content: str,
        text_content: str,
        purpose: str,
        api_key: str,
    ) -> EmailDeliveryResult:
        """Deliver email using Brevo (formerly Sendinblue) REST API."""
        try:
            payload = {
                "sender": {"name": from_name, "email": from_email},
                "to": [{"email": recipient}],
                "subject": subject,
                "htmlContent": html_content,
                "textContent": text_content,
            }
            headers = {
                "api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    json=payload,
                    headers=headers,
                )
                if resp.status_code in (200, 201):
                    auth_db.log_delivery(
                        recipient=masked_rec,
                        purpose=purpose,
                        status="SENT",
                        provider="brevo",
                        error_message="",
                    )
                    return EmailDeliveryResult(
                        success=True,
                        message=f"Verification code sent to {masked_rec}.",
                        provider="brevo",
                    )
                else:
                    err_text = resp.text
                    logger.error(f"[BREVO_ERROR] {resp.status_code} - {err_text}")
                    auth_db.log_delivery(
                        recipient=masked_rec,
                        purpose=purpose,
                        status="FAILED",
                        provider="brevo",
                        error_message=f"{resp.status_code}: {err_text}",
                    )
                    return EmailDeliveryResult(
                        success=False,
                        message="Failed to send verification code via email provider.",
                        provider="brevo",
                        error=err_text,
                    )
        except Exception as e:
            err_msg = f"Brevo API error: {str(e)}"
            logger.exception(f"[BREVO_EXCEPTION] {err_msg}")
            auth_db.log_delivery(
                recipient=masked_rec,
                purpose=purpose,
                status="FAILED",
                provider="brevo",
                error_message=err_msg,
            )
            return EmailDeliveryResult(
                success=False,
                message="Email delivery service encountered a network error.",
                provider="brevo",
                error=err_msg,
            )

    @classmethod
    def test_connection(cls) -> Tuple[bool, str]:
        """Test authentication and connectivity with configured email provider without sending an email."""
        smtp_host = os.getenv("SMTP_HOST", "").strip()
        smtp_user = os.getenv("SMTP_USER", "").strip()
        smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
        if smtp_host and smtp_user and smtp_password:
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            use_ssl = (
                os.getenv("SMTP_USE_SSL", "false").lower() in ("true", "1")
                or smtp_port == 465
            )
            use_tls = (
                os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1")
                and not use_ssl
            )
            try:
                context = ssl.create_default_context()
                if use_ssl:
                    server = smtplib.SMTP_SSL(
                        smtp_host, smtp_port, context=context, timeout=10.0
                    )
                else:
                    server = smtplib.SMTP(
                        smtp_host, smtp_port, timeout=10.0
                    )
                    if use_tls:
                        server.starttls(context=context)
                server.login(smtp_user, smtp_password)
                server.quit()
                return (
                    True,
                    f"SMTP handshake and login succeeded on {smtp_host}:{smtp_port}.",
                )
            except Exception as e:
                return False, f"SMTP connection failed: {e}"

        resend_key = os.getenv("RESEND_API_KEY", "").strip()
        if resend_key:
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.get(
                        "https://api.resend.com/api-keys",
                        headers={"Authorization": f"Bearer {resend_key}"},
                    )
                    if resp.status_code in (200, 201):
                        return True, "Resend API connection authenticated successfully."
                    return (
                        False,
                        f"Resend API authentication failed: {resp.status_code} {resp.text}",
                    )
            except Exception as e:
                return False, f"Resend API connection error: {e}"

        brevo_key = os.getenv("BREVO_API_KEY", "").strip()
        if brevo_key:
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.get(
                        "https://api.brevo.com/v3/account",
                        headers={"api-key": brevo_key},
                    )
                    if resp.status_code == 200:
                        email = resp.json().get("email", "")
                        return (
                            True,
                            f"Brevo API authenticated successfully for account {email}.",
                        )
                    return (
                        False,
                        f"Brevo API authentication failed: {resp.status_code} {resp.text}",
                    )
            except Exception as e:
                return False, f"Brevo API connection error: {e}"

        sendgrid_key = os.getenv("SENDGRID_API_KEY", "").strip()
        if sendgrid_key:
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.get(
                        "https://api.sendgrid.com/v3/user/profile",
                        headers={"Authorization": f"Bearer {sendgrid_key}"},
                    )
                    if resp.status_code == 200:
                        return True, "SendGrid API authenticated successfully."
                    return (
                        False,
                        f"SendGrid API authentication failed: {resp.status_code} {resp.text}",
                    )
            except Exception as e:
                return False, f"SendGrid API connection error: {e}"

        if cls.is_dev_mode():
            return True, "Development Outbox mode active (mock delivery)."

        return (
            False,
            "No email credentials configured (SMTP_HOST, RESEND_API_KEY, BREVO_API_KEY, SENDGRID_API_KEY).",
        )


