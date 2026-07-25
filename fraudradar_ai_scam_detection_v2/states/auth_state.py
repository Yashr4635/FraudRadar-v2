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


def get_app_base_url() -> str:
    for var in (
        "APP_BASE_URL",
        "SITE_URL",
        "PUBLIC_APP_URL",
        "REFLEX_PUBLIC_URL",
        "NEXT_PUBLIC_SITE_URL",
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
    if DEPLOYED_SANDBOX_URL:
        return DEPLOYED_SANDBOX_URL.rstrip("/")
    return "http://localhost:3001"


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
            if _is_expected_auth_error(e):
                logging.warning(
                    f"Expected auth validation/rate-limit in login: {e}"
                )
            else:
                logging.exception(f"Login error: {e}")
            self.auth_error = _friendly_auth_error(e, "login")
        self.loading = False

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
                        "email_redirect_to": callback_url,
                        "redirect_to": callback_url,
                    },
                }
            )
            if resp and resp.user:
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
        """Handle Supabase email verification / OAuth return."""

        # FIX 1: define qp once, outside try block, so it's always available
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(str(self.router.url))
        qp = {k: v[0] for k, v in parse_qs(parsed.query).items()}  

        # Handle implicit flow access_token
        access_token = qp.get("access_token")
        refresh_token = qp.get("refresh_token", "")
        link_type = qp.get("type", "")

        # Password recovery must never be treated as a login - route it to
        # /reset-password, forwarding the tokens since get_supabase() creates
        # a fresh client on every call, so no session survives server-side
        # between this function and ResetPasswordState.
        if access_token and link_type == "recovery":
            from urllib.parse import quote
            return rx.redirect(
                f"/reset-password?access_token={quote(access_token)}"
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
                qp.get("error")
                or qp.get("error_code")
                or qp.get("error_description")
                or ""
            )
            if err_code:
                low = str(err_code).lower()
                if "access_denied" in low or "cancel" in low:
                    self.auth_error = "Sign-in was cancelled. Please try again."
                elif "expired" in low or "invalid" in low:
                    self.auth_error = (
                        "This link has expired or is invalid. "
                        "Please request a new one and try again."
                    )
                else:
                    self.auth_error = (
                        "We couldn't complete sign-in. Please try again."
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
                        return rx.redirect("/reset-password")
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

        # Implicit flow: Supabase returns access_token + refresh_token as
        # query params (forwarded from the hash by auth_callback.py JS).
        access_token = qp.get("access_token")
        refresh_token = qp.get("refresh_token", "")

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
                sb.auth.exchange_code_for_session({"auth_code": code})
                logging.info("OAuth code exchanged successfully")
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
            prov = app_meta.get("provider") or "email"
            return str(prov)
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