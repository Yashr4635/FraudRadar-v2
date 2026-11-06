import os
import re
import secrets
import datetime
import logging
from typing import Tuple, Optional, Dict, Any
import jwt

from fraudradar_ai_scam_detection_v2.services.auth_db import (
    store_otp,
    verify_and_consume_otp,
    check_rate_limit,
    get_user_by_email,
    create_user,
    mark_user_verified,
    update_last_login,
)
from fraudradar_ai_scam_detection_v2.services.email_service import (
    EmailService,
    mask_email,
)

logger = logging.getLogger("fraudradar.otp_service")

JWT_SECRET = (
    os.getenv("JWT_SECRET")
    or os.getenv("SUPABASE_KEY")
    or "fraudradar-secure-jwt-key-2026-production"
)
JWT_ALGORITHM = "HS256"


def generate_8_digit_otp() -> str:
    """Generate a cryptographically secure 8-digit OTP with leading zeros preserved."""
    # 00000000 to 99999999
    code = secrets.randbelow(100_000_000)
    return f"{code:08d}"


def is_valid_email(email: str) -> bool:
    """Strict email validation."""
    if not email or "@" not in email:
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def send_auth_otp(
    email: str,
    purpose: str,
    recipient_name: str = "",
) -> Tuple[bool, str, str]:
    """
    Generate and dispatch an 8-digit OTP to the recipient email.

    Returns:
        (success: bool, user_message: str, masked_email: str)
    """
    clean_email = (email or "").strip().lower()
    if not is_valid_email(clean_email):
        return False, "Please enter a valid email address.", ""

    # Rate limiting: Max 5 requests per 15 minutes per email + purpose
    allowed, rate_msg = check_rate_limit(
        clean_email, purpose, window_seconds=900, max_requests=5
    )
    if not allowed:
        return False, rate_msg, mask_email(clean_email)

    # Cryptographically secure 8-digit OTP
    otp_code = generate_8_digit_otp()

    # Store hashed OTP at rest with 10-minute TTL and max 5 attempts
    store_otp(
        email=clean_email,
        purpose=purpose,
        otp=otp_code,
        expires_in_seconds=600,
        max_attempts=5,
    )

    # Render branded FraudRadar HTML and text templates
    subject, html_body, text_body = EmailService.render_templates(
        recipient_email=clean_email,
        recipient_name=recipient_name,
        otp_code=otp_code,
        purpose=purpose,
        expires_minutes=10,
    )

    # Send email through Unified Email Delivery Service
    delivery = EmailService.send_email(
        recipient_email=clean_email,
        subject=subject,
        html_content=html_body,
        text_content=text_body,
        purpose=purpose,
    )

    masked = mask_email(clean_email)

    if not delivery.success:
        # Invalidate the pending OTP so no unverified dangling code remains
        from fraudradar_ai_scam_detection_v2.services.auth_db import get_connection
        conn = get_connection()
        try:
            with conn:
                conn.execute(
                    "UPDATE otps SET consumed = 1 WHERE email = ? AND purpose = ?;",
                    (clean_email, purpose),
                )
        finally:
            conn.close()

        logger.error(f"OTP delivery failed to {masked}: {delivery.message}")
        return False, delivery.message, masked

    return True, f"Verification code sent to {masked}.", masked


def verify_auth_otp(
    email: str,
    purpose: str,
    code: str,
) -> Tuple[bool, str]:
    """
    Verify an 8-digit OTP with constant-time comparison, single-use invalidation,
    and attempt locking.
    """
    clean_email = (email or "").strip().lower()
    clean_code = re.sub(r"\D", "", code or "").strip()

    if not clean_email or "@" not in clean_email:
        return False, "Email address is missing or invalid."

    if len(clean_code) != 8:
        return False, "Please enter the complete 8-digit verification code."

    return verify_and_consume_otp(clean_email, purpose, clean_code)


def create_user_jwt(user: Dict[str, Any], expiry_days: int = 7) -> str:
    """Generate a signed HS256 JWT for an authenticated user."""
    now = datetime.datetime.now(datetime.timezone.utc)
    exp = now + datetime.timedelta(days=expiry_days)
    payload = {
        "sub": str(user.get("id")),
        "email": str(user.get("email")),
        "name": str(user.get("full_name") or user.get("name") or "User"),
        "role": "authenticated",
        "provider": str(user.get("provider") or "email"),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_user_jwt(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a user session JWT."""
    if not token or not isinstance(token, str):
        return None
    try:
        payload = jwt.decode(token.strip(), JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception as e:
        logger.debug(f"JWT verification notice: {e}")
        return None

