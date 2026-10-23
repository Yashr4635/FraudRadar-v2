import os
import logging
import datetime
from dotenv import load_dotenv
import reflex as rx

import secrets
import hashlib
import base64

def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode()
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()
    return code_verifier, code_challenge



load_dotenv()

try:
    from supabase import create_client, Client
except Exception:
    logging.exception("Unexpected error")
    create_client = None
    Client = None


PROFILES_TABLE = "profiles"
SCAN_HISTORY_TABLE = "scan_history"

DEPLOYED_SANDBOX_URL = (
    "https://8080-c7830b68-cdf4-4aa9-8d7f-9c7ceef90fe6.build.reflexsandbox.com"
)

# Reads Supabase's implicit-flow hash fragment directly, client-side, and
# hands it back to the Python event handler via rx.call_script. This avoids
# a race between on_mount (which fires immediately, before the hash is
# visible server-side) and a separate full-page-reload script that used to
# try to forward the hash as query params - that reload could lose the race
# against on_mount's own fallback redirect.
_EXTRACT_AUTH_HASH_JS = """
(function () {
    var hash = window.location.hash.substring(1);
    var params = new URLSearchParams(hash);
    return JSON.stringify({
        access_token: params.get('access_token'),
        refresh_token: params.get('refresh_token'),
        type: params.get('type'),
        error: params.get('error'),
        error_code: params.get('error_code'),
        error_description: params.get('error_description')
    });
})()
"""


def get_app_base_url() -> str:
    for var in (
        "APP_BASE_URL",
        "SITE_URL",
        "PUBLIC_APP_URL",
        "REFLEX_PUBLIC_URL",
        "NEXT_PUBLIC_SITE_URL",
        "RAILWAY_PUBLIC_DOMAIN",
        "RAILWAY_STATIC_URL",
        "RENDER_EXTERNAL_URL",
        "RENDER_EXTERNAL_HOSTNAME",
        "VERCEL_URL",
    ):
        val = os.getenv(var)
        if val:
            v = val.strip()
            if not v:
                continue
            if not v.startswith("http://") and not v.startswith("https://"):
                v = "https://" + v
            return v.rstrip("/")
    sandbox = os.getenv("REFLEX_SANDBOX_URL") or os.getenv("CODESPACE_NAME")
    if sandbox:
        s = sandbox.strip().rstrip("/")
        if not s.startswith("http"):
            s = "https://" + s
        return s
    if os.getenv("DEPLOYED_SANDBOX_URL"):
        return os.getenv("DEPLOYED_SANDBOX_URL").strip().rstrip("/")
    return os.getenv("FRONTEND_URL", "http://localhost:3000")


def get_auth_callback_url() -> str:
    base = get_app_base_url().rstrip("/")
    return f"{base}/auth/callback"


def _is_expected_auth_error(e: Exception) -> bool:
    msg = str(e).lower()
    expected_keywords = [
        "rate limit",
        "too many",
        "security purposes",
        "invalid login",
        "invalid credentials",
        "invalid email or password",
        "email not confirmed",
        "email not verified",
        "user already registered",
        "already been registered",
        "already exists",
        "user not found",
        "no user found",
        "password should be",
        "password is too short",
        "weak password",
        "invalid email",
        "unable to validate email",
        "signup is disabled",
        "signups not allowed",
        "expired",
        "invalid token",
        "invalid link",
        "otp expired",
        "access denied",
        "oauth",
        "cancelled",
        "canceled",
    ]
    return any(k in msg for k in expected_keywords)


def _friendly_auth_error(e: Exception, context: str = "") -> str:
    msg = str(e) if e else ""
    low = msg.lower()
    import re

    m = re.search(r"after\s+(\d+)\s+seconds", low)
    if "email rate limit exceeded" in low:
        return "Too many email requests. Please wait a moment and try again."
    if (
        "security purposes" in low
        or "rate limit" in low
        or "too many" in low
        or m
    ):
        secs = m.group(1) if m else None
        if secs:
            return (
                f"Too many attempts. Please wait {secs} seconds and try again."
            )
        return "Too many attempts. Please wait a moment and try again."
    if (
        "invalid login" in low
        or "invalid credentials" in low
        or "invalid email or password" in low
        or "wrong password" in low
        or "incorrect password" in low
    ):
        return "Incorrect email or password. Please try again."
    if "email not confirmed" in low or "email not verified" in low:
        return (
            "Please verify your email before signing in. "
            "Check your inbox for the confirmation link."
        )
    if (
        "user already registered" in low
        or "already been registered" in low
        or "already exists" in low
        or "duplicate" in low
    ):
        return (
            "An account with this email already exists. "
            "Try signing in or use 'Forgot password?' to reset it."
        )
    if "user not found" in low or "no user found" in low:
        return "No account found with this email. Please sign up first."
    if (
        "password should be" in low
        or "password is too short" in low
        or "weak password" in low
    ):
        return "Password is too weak. Use at least 6 characters."
    if "invalid email" in low or "unable to validate email" in low:
        return "Please enter a valid email address."
    if (
        "expired" in low
        or "invalid token" in low
        or "invalid link" in low
        or "otp expired" in low
    ):
        return (
            "This link has expired or is invalid. "
            "Please request a new one and try again."
        )
    if "access denied" in low or "cancelled" in low or "canceled" in low:
        return "Sign-in was cancelled. Please try again."
    if "oauth" in low or "provider" in low:
        return "Could not complete sign-in with provider. Please try again."
    if (
        "network" in low
        or "timeout" in low
        or "connection" in low
        or "unreachable" in low
        or "dns" in low
    ):
        return "Network issue. Check your connection and try again."
    if "signup is disabled" in low or "signups not allowed" in low:
        return "Signups are currently disabled. Please contact support."
    short = msg.strip()
    if len(short) > 140:
        short = short[:140] + "…"
    if not short:
        ctx = (context or "request").strip()
        return f"{ctx.capitalize()} failed. Please try again."
    return short


def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if url and key and create_client:
        try:
            from supabase import ClientOptions
            return create_client(
                url,
                key,
                options=ClientOptions(flow_type="implicit")
            )
        except Exception as e:
            logging.exception(f"Supabase init failed: {e}")
            return None
    return None


class AuthState(rx.State):
    is_authenticated: bool = False
    user_id: str = ""
    user_email: str = ""
    user_name: str = ""
    user_avatar_url: str = ""
    user_provider: str = "email"
    last_login_at: str = ""
    access_token: str = ""
    refresh_token: str = ""
    auth_error: str = ""
    auth_success: str = ""
    _code_verifier: str = ""
    loading: bool = False
    google_loading: bool = False
    remember_me: bool = True

    login_email: str = ""
    login_password: str = ""
    show_login_password: bool = False

    signup_name: str = ""
    signup_email: str = ""
    signup_password: str = ""
    signup_confirm: str = ""
    show_signup_password: bool = False
    accept_terms: bool = False

    # Forgot password flow
    forgot_email: str = ""
    forgot_loading: bool = False
    forgot_success: str = ""
    forgot_error: str = ""
    show_forgot_modal: bool = False

    # Change password flow (post-recovery or settings)
    new_password: str = ""
    confirm_password: str = ""
    show_new_password: bool = False
    change_password_loading: bool = False
    change_password_success: str = ""
    change_password_error: str = ""

    # OTP / Email verification flow
    show_otp_view: bool = False
    otp_email: str = ""
    otp_code: str = ""
    otp_type: str = "signup"
    otp_loading: bool = False
    otp_error: str = ""
    otp_success: str = ""

    @rx.event
    def set_login_email(self, v: str):
        self.login_email = v

    @rx.event
    def set_login_password(self, v: str):
        self.login_password = v

    @rx.event
    def toggle_login_password(self):
        self.show_login_password = not self.show_login_password

    @rx.event
    def set_signup_name(self, v: str):
        self.signup_name = v

    @rx.event
    def set_signup_email(self, v: str):
        self.signup_email = v

    @rx.event
    def set_signup_password(self, v: str):
        self.signup_password = v

    @rx.event
    def set_signup_confirm(self, v: str):
        self.signup_confirm = v

    @rx.event
    def toggle_signup_password(self):
        self.show_signup_password = not self.show_signup_password

    @rx.event
    def toggle_terms(self):
        self.accept_terms = not self.accept_terms

    @rx.event
    def toggle_remember_me(self):
        self.remember_me = not self.remember_me

    @rx.event
    def clear_messages(self):
        self.auth_error = ""
        self.auth_success = ""
        self.forgot_error = ""
        self.forgot_success = ""
        self.change_password_error = ""
        self.change_password_success = ""

    # ---------- Forgot Password ----------
    @rx.event
    def set_forgot_email(self, v: str):
        self.forgot_email = v

    @rx.event
    def open_forgot_modal(self):
        self.show_forgot_modal = True
        self.forgot_email = self.login_email
        self.forgot_error = ""
        self.forgot_success = ""

    @rx.event
    def close_forgot_modal(self):
        self.show_forgot_modal = False

    @rx.event
    def send_password_reset(self):
        if self.forgot_loading:
            return
        self.forgot_error = ""
        self.forgot_success = ""
        email = (self.forgot_email or "").strip()
        if not email or "@" not in email:
            self.forgot_error = "Please enter a valid email address."
            return
        sb = get_supabase()
        if sb is None:
            self.forgot_error = (
                "Authentication is not configured. Please contact support."
            )
            return
        self.forgot_loading = True
        try:
            sb.auth.reset_password_for_email(
                email,
                {"redirect_to": get_auth_callback_url()},
            )
            self.forgot_success = (
                "Password reset link sent. Check your email inbox."
            )
        except Exception as e:
            if _is_expected_auth_error(e):
                logging.warning(f"Expected auth error in reset: {e}")
            else:
                logging.exception(f"Reset password error: {e}")
            self.forgot_error = _friendly_auth_error(e, "password reset")
        self.forgot_loading = False

    # ---------- Change Password ----------
    @rx.event
    def set_new_password(self, v: str):
        self.new_password = v

    @rx.event
    def set_confirm_password(self, v: str):
        self.confirm_password = v

    @rx.event
    def toggle_new_password(self):
        self.show_new_password = not self.show_new_password

    @rx.event
    def change_password(self):
        self.change_password_error = ""
        self.change_password_success = ""
        if len(self.new_password) < 6:
            self.change_password_error = (
                "Password must be at least 6 characters."
            )
            return
        if self.new_password != self.confirm_password:
            self.change_password_error = "Passwords do not match."
            return
        sb = get_supabase()
        if sb is None:
            self.change_password_error = (
                "Authentication is not configured. Please contact support."
            )
            return
        self.change_password_loading = True
        try:
            sb.auth.update_user({"password": self.new_password})
            self.change_password_success = "Password updated successfully."
            self.new_password = ""
            self.confirm_password = ""
        except Exception as e:
            if _is_expected_auth_error(e):
                logging.warning(f"Expected change password error: {e}")
            else:
                logging.exception(f"Change password error: {e}")
            self.change_password_error = _friendly_auth_error(
                e, "change password"
            )
        self.change_password_loading = False

    @rx.event
    def login(self):
        if self.loading:
            return
        self.auth_error = ""
        self.auth_success = ""
        if not self.login_email or "@" not in self.login_email:
            self.auth_error = "Please enter a valid email address."
            return
        if len(self.login_password) < 6:
            self.auth_error = "Password must be at least 6 characters."
            return
        sb = get_supabase()
        if sb is None:
            self.auth_error = (
                "Authentication service is not configured. "
                "Please contact your administrator."
            )
            return
        self.loading = True
        try:
            resp = sb.auth.sign_in_with_password(
                {"email": self.login_email, "password": self.login_password}
            )
            if resp and resp.user:
                self._apply_user_session(resp.user, resp.session, "email")
                self.auth_success = "Welcome back!"
                self.loading = False
                self._sync_profile_safe()
                return rx.redirect("/dashboard")
            else:
                self.auth_error = "Invalid email or password."
        except Exception as e:
            msg = str(e).lower()
            if "not confirmed" in msg or "email not confirmed" in msg:
                self.otp_email = self.login_email
                self.otp_type = "signup"
                self.show_otp_view = True
                self.auth_error = ""
                self.auth_success = f"Please enter the verification code sent to {self.login_email} to activate your account."
                self.loading = False
                return
            if _is_expected_auth_error(e):
                logging.warning(
                    f"Expected auth validation/rate-limit in login: {e}"
                )
            else:
                logging.exception(f"Login error: {e}")
            self.auth_error = _friendly_auth_error(e, "login")
        self.loading = False

    @rx.event
    def set_otp_code(self, v: str):
        self.otp_code = v.strip()

    @rx.event
    def set_otp_email(self, v: str):
        self.otp_email = v.strip()

    @rx.event
    def cancel_otp_view(self):
        self.show_otp_view = False
        self.otp_code = ""
        self.otp_error = ""

    @rx.event
    def open_otp_login(self):
        email = (self.login_email or "").strip()
        if not email or "@" not in email:
            self.auth_error = "Please enter your email address first."
            return
        self.otp_email = email
        self.otp_type = "email"
        return self.send_login_otp()

    @rx.event
    def send_login_otp(self):
        email = (self.otp_email or self.login_email).strip()
        if not email or "@" not in email:
            self.auth_error = "Please enter a valid email address."
            return
        sb = get_supabase()
        if sb is None:
            self.auth_error = "Authentication service is not configured."
            return
        self.otp_loading = True
        self.auth_error = ""
        self.auth_success = ""
        self.otp_error = ""
        try:
            sb.auth.sign_in_with_otp({
                "email": email,
            })
            self.otp_email = email
            self.otp_type = "email"
            self.show_otp_view = True
            self.auth_success = f"Verification code sent to {email}. Please enter the 6-digit code below."
        except Exception as e:
            logging.exception(f"Send OTP error: {e}")
            self.auth_error = _friendly_auth_error(e, "send verification code")
        finally:
            self.otp_loading = False

    @rx.event
    def verify_email_otp(self):
        code = self.otp_code.strip()
        email = (self.otp_email or self.login_email or self.signup_email).strip()
        if not code:
            self.otp_error = "Please enter the verification code."
            return
        if not email:
            self.otp_error = "Email address missing. Please go back and try again."
            return
        sb = get_supabase()
        if sb is None:
            self.otp_error = "Authentication service is not configured."
            return
        self.otp_loading = True
        self.otp_error = ""
        try:
            primary_type = self.otp_type or "signup"
            secondary_type = "email" if primary_type == "signup" else "signup"
            result = None
            try:
                result = sb.auth.verify_otp({
                    "email": email,
                    "token": code,
                    "type": primary_type,
                })
            except Exception as e1:
                logging.info(f"verify_otp {primary_type} failed: {e1}, trying {secondary_type}")
                try:
                    result = sb.auth.verify_otp({
                        "email": email,
                        "token": code,
                        "type": secondary_type,
                    })
                except Exception:
                    raise e1

            if result and result.user:
                provider = self._extract_provider(result.user)
                self._apply_user_session(
                    result.user,
                    result.session,
                    provider,
                    fallback_name=self.signup_name,
                )
                self.auth_success = "Email verified successfully!"
                self.show_otp_view = False
                self.otp_code = ""
                self._sync_profile_safe()
                return rx.redirect("/dashboard")
            else:
                self.otp_error = "Invalid or expired verification code."
        except Exception as e:
            logging.exception(f"Verify OTP error: {e}")
            msg = str(e).lower()
            if "expired" in msg or "invalid" in msg or "token" in msg:
                self.otp_error = "Invalid or expired verification code. Please request a new one."
            else:
                self.otp_error = _friendly_auth_error(e, "verification")
        finally:
            self.otp_loading = False

    @rx.event
    def resend_otp_code(self):
        email = (self.otp_email or self.login_email or self.signup_email).strip()
        if not email:
            self.otp_error = "Email address is missing."
            return
        sb = get_supabase()
        if sb is None:
            self.otp_error = "Authentication service is not configured."
            return
        self.otp_loading = True
        self.otp_error = ""
        try:
            otp_type = self.otp_type or "signup"
            sb.auth.resend({
                "type": otp_type,
                "email": email,
            })
            self.auth_success = f"A new verification code has been sent to {email}."
        except Exception as e:
            try:
                sb.auth.sign_in_with_otp({"email": email})
                self.auth_success = f"A new verification code has been sent to {email}."
            except Exception as e2:
                logging.exception(f"Resend OTP error: {e2}")
                self.otp_error = _friendly_auth_error(e2, "resend code")
        finally:
            self.otp_loading = False

    @rx.event
    def login_with_google(self):
        if self.loading or self.google_loading:
            return
        self.auth_error = ""
        self.auth_success = ""
        sb = get_supabase()
        if sb is None:
            self.auth_error = (
                "Authentication service is not configured. "
                "Please configure SUPABASE_URL and SUPABASE_KEY in your .env file."
            )
            return
        self.google_loading = True
        try:
            callback_url = None
            try:
                headers = getattr(self.router, "headers", None)
                if headers:
                    origin = getattr(headers, "origin", "") or getattr(headers, "host", "")
                    if origin:
                        origin_str = str(origin).strip()
                        if not origin_str.startswith("http"):
                            origin_str = f"https://{origin_str}"
                        callback_url = f"{origin_str.rstrip('/')}/auth/callback"
            except Exception:
                pass

            if not callback_url:
                current_url = str(getattr(self.router, "url", "") or "")
                if current_url.startswith("http"):
                    from urllib.parse import urlparse
                    parsed = urlparse(current_url)
                    scheme = parsed.scheme or ("http" if "localhost" in parsed.netloc else "https")
                    callback_url = f"{scheme}://{parsed.netloc}/auth/callback"

            if not callback_url:
                callback_url = get_auth_callback_url()

            logging.info(f"Initiating Google OAuth redirect to: {callback_url}")
            res = sb.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": callback_url,
                },
            })
            oauth_url = getattr(res, "url", None)
            if oauth_url:
                self.google_loading = False
                return rx.redirect(oauth_url)
            else:
                self.auth_error = "Could not initialize Google sign-in. Please try again."
        except Exception as e:
            if _is_expected_auth_error(e):
                logging.warning(f"Expected auth validation in Google OAuth: {e}")
            else:
                logging.exception(f"Google sign-in error: {e}")
            self.auth_error = _friendly_auth_error(e, "Google sign-in")
        finally:
            self.google_loading = False

    @rx.event
    def signup(self):
        if self.loading:
            return
        self.auth_error = ""
        self.auth_success = ""
        if not self.signup_name.strip():
            self.auth_error = "Please enter your name."
            return
        if not self.signup_email or "@" not in self.signup_email:
            self.auth_error = "Please enter a valid email."
            return
        if len(self.signup_password) < 6:
            self.auth_error = "Password must be at least 6 characters."
            return
        if self.signup_password != self.signup_confirm:
            self.auth_error = "Passwords do not match."
            return
        if not self.accept_terms:
            self.auth_error = "Please accept the terms to continue."
            return
        sb = get_supabase()
        if sb is None:
            self.auth_error = (
                "Authentication service is not configured. "
                "Please contact your administrator."
            )
            return
        self.loading = True
        try:
            callback_url = get_auth_callback_url()
            resp = sb.auth.sign_up(
                {
                    "email": self.signup_email,
                    "password": self.signup_password,
                    "options": {
                        "data": {"full_name": self.signup_name},
                    },
                }
            )
            if resp and resp.user:
                if not resp.session:
                    self.otp_email = self.signup_email
                    self.otp_type = "signup"
                    self.show_otp_view = True
                    self.auth_success = f"Account created! We've sent a 6-digit confirmation code to {self.signup_email}."
                    self.loading = False
                    return
                self._apply_user_session(
                    resp.user,
                    resp.session,
                    "email",
                    fallback_name=self.signup_name,
                )
                self.auth_success = "Account created successfully!"
                self.loading = False
                self._sync_profile_safe()
                if resp.session:
                    return rx.redirect("/dashboard")
                return rx.redirect("/login")
            else:
                self.auth_error = "Signup failed. Please try again."
        except Exception as e:
            if _is_expected_auth_error(e):
                logging.warning(
                    f"Expected auth validation/rate-limit in signup: {e}"
                )
            else:
                logging.exception(f"Signup error: {e}")
            self.auth_error = _friendly_auth_error(e, "signup")
        self.loading = False

    @rx.event
    def logout(self):
        sb = get_supabase()
        if sb is not None:
            try:
                sb.auth.sign_out()
            except Exception as e:
                logging.exception(f"Logout error: {e}")
        self.is_authenticated = False
        self.user_id = ""
        self.user_email = ""
        self.user_name = ""
        self.user_avatar_url = ""
        self.user_provider = "email"
        self.last_login_at = ""
        self.access_token = ""
        self.refresh_token = ""
        self.auth_error = ""
        self.auth_success = ""
        self.loading = False
        self.google_loading = False
        self.show_otp_view = False
        self.otp_email = ""
        self.otp_code = ""
        self.otp_error = ""
        self.otp_success = ""
        self.otp_loading = False
        self.forgot_loading = False
        self.forgot_email = ""
        self.forgot_error = ""
        self.forgot_success = ""
        self.show_forgot_modal = False
        self.change_password_loading = False
        self.change_password_error = ""
        self.change_password_success = ""
        self.new_password = ""
        self.confirm_password = ""
        self.login_email = ""
        self.login_password = ""
        self.signup_name = ""
        self.signup_email = ""
        self.signup_password = ""
        self.signup_confirm = ""
        self.show_login_password = False
        self.show_signup_password = False
        self.accept_terms = False
        return rx.redirect("/login")

    @rx.event
    def require_auth(self):
        if not self.is_authenticated:
            try:
                self._restore_session_sync()
            except Exception as e:
                logging.exception(f"require_auth restore: {e}")
        if not self.is_authenticated:
            return rx.redirect("/login")

    @rx.event
    def handle_auth_callback(self):
        """Handle Supabase email verification / OAuth return.

        Kicks off client-side hash extraction first (rx.call_script) instead
        of processing query params immediately - on the very first page
        load, tokens from an implicit-flow link are only in the URL hash,
        which the server can never see. Processing used to fall through to
        a generic "no tokens found" fallback before the hash-forwarding
        script had a chance to run, which is what caused a recovery link
        to bounce to /login with a misleading "Email verified" message.
        """
        return rx.call_script(
            _EXTRACT_AUTH_HASH_JS,
            callback=AuthState.process_auth_callback,
        )

    @rx.event
    def process_auth_callback(self, raw: str):
        """Actual callback logic. `raw` is the JSON string produced by
        _EXTRACT_AUTH_HASH_JS - guaranteed to reflect the page's hash at
        the time this runs, so there's no more race with query-param-only
        parsing."""
        import json as _json
        try:
            hash_data = _json.loads(raw) if raw else {}
        except (TypeError, ValueError):
            hash_data = {}

        # FIX 1: define qp once, outside try block, so it's always available
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(str(self.router.url))
        qp = {k: v[0] for k, v in parse_qs(parsed.query).items()}  

        # Handle implicit flow access_token - prefer hash-extracted values
        # (the real source for implicit-flow links), fall back to query
        # params for flows that arrive via ?access_token=... directly.
        access_token = hash_data.get("access_token") or qp.get("access_token")
        refresh_token = hash_data.get("refresh_token") or qp.get("refresh_token", "")
        link_type = hash_data.get("type") or qp.get("type", "")

        # Password recovery must never be treated as a login - route it to
        # /reset-password, forwarding the tokens since get_supabase() creates
        # a fresh client on every call, so no session survives server-side
        # between this function and ResetPasswordState.
        #
        # NOTE: trailing slash on "/reset-password/" is required. Reflex's
        # static export serves this route as reset-password/index.html, so
        # a redirect to the no-slash path 404s on the host (Railway) before
        # the reset-password page ever gets a chance to load. This was the
        # root cause of the "click email link -> 404 -> refresh -> works"
        # bug: refreshing manually re-issued the request with the slash
        # already present in the address bar (or the browser normalized it),
        # masking the fact that the redirect itself was wrong.
        if access_token and link_type == "recovery":
            from urllib.parse import quote
            return rx.redirect(
                f"/reset-password/?access_token={quote(access_token)}"
                f"&refresh_token={quote(refresh_token)}&type=recovery"
            )

        if access_token:
            try:
                sb = get_supabase()
                if sb is None:
                    self.auth_error = "Authentication service is not configured."
                    return rx.redirect("/login")
                result = sb.auth.set_session(access_token, refresh_token)
                user = result.user
                if user:
                    provider = self._extract_provider(user)
                    self._apply_user_session(user, result.session, provider)
                    self._sync_profile_safe()
                    return rx.redirect("/dashboard")
            except Exception as e:
                logging.exception(f"Token session failed: {e}")
            return rx.redirect("/login")  # this line must be indented to match try:

         

        # Detect provider-side errors
        try:
            err_code = (
                hash_data.get("error")
                or qp.get("error")
                or hash_data.get("error_code")
                or qp.get("error_code")
                or ""
            )
            err_desc = (
                hash_data.get("error_description")
                or qp.get("error_description")
                or ""
            )
            if err_code or err_desc:
                logging.warning(f"OAuth callback error: code={err_code}, desc={err_desc}")
                combined = f"{err_code} {err_desc}".lower()
                if "access_denied" in combined or "cancel" in combined:
                    self.auth_error = "Sign-in was cancelled. Please try again."
                elif "expired" in combined or "invalid" in combined:
                    self.auth_error = (
                        "This link has expired or is invalid. "
                        "Please request a new one and try again."
                    )
                elif "exchange external code" in combined:
                    self.auth_error = (
                        "Google sign-in configuration error: Unable to exchange code. "
                        "Please verify your Google Client Secret in Supabase Providers, "
                        "and ensure the redirect URI is saved in Google Cloud."
                    )
                elif err_desc:
                    clean_desc = err_desc.replace("+", " ").strip()
                    self.auth_error = f"Sign-in error: {clean_desc}"
                else:
                    self.auth_error = (
                        "We couldn't complete sign-in. Please check provider settings and try again."
                    )
                return rx.redirect("/login")
        except Exception:
            logging.exception("callback query parse")

        # FIX 5: Email verification path using verify_otp
        token_hash = qp.get("token_hash")
        verify_type = qp.get("type")

        if token_hash and verify_type:
            try:
                sb = get_supabase()
                if sb is None:
                    self.auth_error = "Authentication service is not configured."
                    return rx.redirect("/login")
                result = sb.auth.verify_otp({
                    "token_hash": token_hash,
                    "type": verify_type,
                })
                user = result.user
                if user:
                    if verify_type == "recovery":
                        # Trailing slash required - see note above.
                        return rx.redirect("/reset-password/")
                    provider = self._extract_provider(user)
                    self._apply_user_session(user, result.session, provider)
                    self._sync_profile_safe()
                    return rx.redirect("/dashboard")
            except Exception as e:
                logging.exception(f"Email verification failed: {e}")
            return rx.redirect("/login")

        # OAuth path
        sb = get_supabase()
        if sb is None:
            self.auth_error = (
                "Authentication service is not configured. "
                "Please contact your administrator."
            )
            return rx.redirect("/login")

        # Implicit flow: Supabase returns access_token + refresh_token,
        # either in the hash (extracted above) or as query params.
        access_token = hash_data.get("access_token") or qp.get("access_token")
        refresh_token = hash_data.get("refresh_token") or qp.get("refresh_token", "")

        if access_token:
            logging.info("OAuth implicit: access_token received, setting session")
            try:
                sb.auth.set_session(access_token, refresh_token)
                logging.info("OAuth session set successfully")
            except Exception as e:
                logging.exception(f"set_session failed: {e}")
                self.auth_error = "We couldn't complete sign in. Please try again."
                return rx.redirect("/login")

        # Also handle PKCE code flow as fallback (e.g. email magic links)
        code = qp.get("code")
        if code and not access_token:
            logging.info(f"OAuth code flow: exchanging code")
            try:
                auth_resp = sb.auth.exchange_code_for_session({"auth_code": code})
                logging.info("OAuth code exchanged successfully")
                if auth_resp and getattr(auth_resp, "user", None):
                    provider = self._extract_provider(auth_resp.user)
                    self._apply_user_session(auth_resp.user, auth_resp.session, provider)
                    self.auth_success = "Welcome to FraudRadar!"
                    self._sync_profile_safe()
                    return rx.redirect("/dashboard")
            except Exception as e:
                logging.exception(f"OAuth exchange failed: {e}")
                self.auth_error = "We couldn't complete sign in. Please try again."
                return rx.redirect("/login")

        try:
            session_resp = sb.auth.get_session()
            session = getattr(session_resp, "session", None) or session_resp
            user = None
            if session:
                user = getattr(session, "user", None)
                if user is None and isinstance(session, dict):
                    user = session.get("user")
            if user:
                provider = self._extract_provider(user)
                self._apply_user_session(user, session, provider)
                self.auth_success = "Welcome to FraudRadar!"
                self._sync_profile_safe()
                return rx.redirect("/dashboard")
        except Exception as e:
            logging.exception(f"Auth callback error: {e}")

        if self.is_authenticated:
            return rx.redirect("/dashboard")

        self.auth_success = (
            "Email verified successfully. Please sign in to continue."
        )
        return rx.redirect("/login")

    def _restore_session_sync(self) -> bool:
        if self.is_authenticated:
            return True
        sb = get_supabase()
        if sb is None:
            return False
        try:
            session_resp = sb.auth.get_session()
            session = getattr(session_resp, "session", None) or session_resp
            user = None
            if session:
                user = getattr(session, "user", None)
                if user is None and isinstance(session, dict):
                    user = session.get("user")
            if user:
                provider = self._extract_provider(user)
                self._apply_user_session(user, session, provider)
                try:
                    self._sync_profile_safe()
                except Exception as e:
                    logging.exception(f"profile sync (restore): {e}")
                return True
        except Exception as e:
            logging.exception(f"Session restore error: {e}")
        return False

    @rx.event
    def restore_session(self):
        try:
            self._restore_session_sync()
        except Exception as e:
            logging.exception(f"restore_session: {e}")

    def _extract_provider(self, user) -> str:
        try:
            app_meta = (
                getattr(user, "app_metadata", None)
                or (
                    user.get("app_metadata", {})
                    if isinstance(user, dict)
                    else {}
                )
                or {}
            )
            prov = app_meta.get("provider")
            if not prov and app_meta.get("providers"):
                providers = app_meta.get("providers")
                if isinstance(providers, list) and len(providers) > 0:
                    prov = providers[0]
            if not prov and hasattr(user, "identities") and user.identities:
                for ident in user.identities:
                    ident_prov = getattr(ident, "provider", None) or (
                        ident.get("provider") if isinstance(ident, dict) else None
                    )
                    if ident_prov:
                        prov = ident_prov
                        break
            return str(prov or "email")
        except Exception:
            logging.exception("provider extract")
            return "email"

    def _apply_user_session(
        self, user, session, provider: str, fallback_name: str = ""
    ) -> None:
        try:
            uid = getattr(user, "id", None) or (
                user.get("id") if isinstance(user, dict) else ""
            )
            email = getattr(user, "email", None) or (
                user.get("email") if isinstance(user, dict) else ""
            )
            meta = (
                getattr(user, "user_metadata", None)
                or (
                    user.get("user_metadata", {})
                    if isinstance(user, dict)
                    else {}
                )
                or {}
            )
            access = ""
            refresh = ""
            if session is not None:
                access = getattr(session, "access_token", "") or (
                    session.get("access_token", "")
                    if isinstance(session, dict)
                    else ""
                )
                refresh = getattr(session, "refresh_token", "") or (
                    session.get("refresh_token", "")
                    if isinstance(session, dict)
                    else ""
                )

            name = (
                meta.get("full_name")
                or meta.get("name")
                or fallback_name
                or (email.split("@")[0].title() if email else "User")
            )
            avatar = meta.get("avatar_url") or meta.get("picture") or ""

            self.is_authenticated = True
            self.user_id = uid or ""
            self.user_email = email or ""
            self.user_name = name
            self.user_avatar_url = avatar or ""
            self.user_provider = provider or "email"
            self.access_token = access or ""
            self.refresh_token = refresh or ""
            self.last_login_at = datetime.datetime.utcnow().isoformat()
        except Exception as e:
            logging.exception(f"apply session: {e}")

    def _sync_profile_safe(self) -> None:
        if not self.is_authenticated or not self.user_id:
            return
        sb = get_supabase()
        if sb is None:
            return
        payload = {
            "id": self.user_id,
            "email": self.user_email,
            "full_name": self.user_name,
            "avatar_url": self.user_avatar_url,
            "provider": self.user_provider,
            "last_login_at": self.last_login_at,
        }
        try:
            sb.table(PROFILES_TABLE).upsert(payload).execute()
        except Exception as e:
            msg = str(e)
            if "PGRST205" in msg or "Could not find the table" in msg:
                logging.debug(
                    f"profiles table not provisioned; skipping sync: {msg[:120]}"
                )
                return
            try:
                sb.table(PROFILES_TABLE).upsert(
                    {
                        "id": self.user_id,
                        "email": self.user_email,
                        "full_name": self.user_name,
                    }
                ).execute()
            except Exception as e2:
                logging.exception(f"profile upsert failed: {e2}")