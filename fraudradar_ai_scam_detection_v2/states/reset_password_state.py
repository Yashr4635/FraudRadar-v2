"""
ResetPasswordState
-------------------
Handles the Supabase "recovery" flow for /reset-password.

Reuses the existing Supabase client from auth_state.py via get_supabase().
No separate client is created here.
"""

import asyncio
import json
import re

import reflex as rx

from fraudradar_ai_scam_detection_v2.states.auth_state import get_supabase


# JS run in the browser on page load. Supabase's recovery link lands the
# user on your redirect URL with the session tokens in the URL *hash*
# fragment (#access_token=...&refresh_token=...&type=recovery). The hash
# never reaches the server, so we must read it client-side and hand it
# back to the Reflex event handler via rx.call_script.
_EXTRACT_RECOVERY_TOKENS_JS = """
(function () {
    var hash = window.location.hash.substring(1);
    var params = new URLSearchParams(hash);
    return JSON.stringify({
        access_token: params.get('access_token'),
        refresh_token: params.get('refresh_token'),
        type: params.get('type')
    });
})()
"""


class ResetPasswordState(rx.State):
    # form fields
    new_password: str = ""
    confirm_password: str = ""

    # ui state
    show_new_password: bool = False
    show_confirm_password: bool = False
    is_loading: bool = False
    checking_session: bool = True
    session_ready: bool = False

    # messages
    error_message: str = ""
    success_message: str = ""

    # get_supabase() creates a brand-new client on every call (it's not a
    # singleton), so a session set in one call is gone by the next. These
    # persist the tokens on state so update_password() can re-establish the
    # same recovery session right before calling update_user().
    _recovery_access_token: str = ""
    _recovery_refresh_token: str = ""

    # ---------------- session detection ----------------

    def on_mount(self):
        """Bind this to on_load for the /reset-password route."""
        self.checking_session = True
        self.error_message = ""
        self.success_message = ""
        return rx.call_script(
            _EXTRACT_RECOVERY_TOKENS_JS,
            callback=ResetPasswordState.handle_recovery_tokens,
        )

    async def handle_recovery_tokens(self, raw: str):
        """Receives the JSON string produced by _EXTRACT_RECOVERY_TOKENS_JS."""
        self.checking_session = False
        try:
            data = json.loads(raw) if raw else {}
        except (TypeError, ValueError):
            data = {}

        # router.page.params is deprecated as of Reflex 0.8.1 - parse the
        # query string from router.url directly instead (same pattern used
        # in AuthState.handle_auth_callback).
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(str(self.router.url))
        qp = {k: v[0] for k, v in parse_qs(parsed.query).items()}

        access_token = data.get("access_token") or qp.get("access_token")
        refresh_token = data.get("refresh_token") or qp.get("refresh_token")
        token_type = data.get("type") or qp.get("type")

        # PKCE flow (if enabled in your Supabase project) sends a plain
        # ?code=... query param instead of a hash fragment.
        code = qp.get("code")

        try:
            supabase = get_supabase()
            if access_token and refresh_token and token_type == "recovery":
                supabase.auth.set_session(access_token, refresh_token)
                self._recovery_access_token = access_token
                self._recovery_refresh_token = refresh_token
                self.session_ready = True
            elif code:
                result = supabase.auth.exchange_code_for_session({"auth_code": code})
                session = getattr(result, "session", None)
                if session:
                    self._recovery_access_token = getattr(session, "access_token", "") or ""
                    self._recovery_refresh_token = getattr(session, "refresh_token", "") or ""
                self.session_ready = True
            else:
                self.session_ready = False
                self.error_message = (
                    "This password reset link is invalid or has expired. "
                    "Please request a new one."
                )
        except Exception as e:
            self.session_ready = False
            self.error_message = f"Could not verify reset link: {str(e)}"

    # ---------------- form handlers ----------------

    def set_new_password(self, value: str):
        self.new_password = value
        self.error_message = ""

    def set_confirm_password(self, value: str):
        self.confirm_password = value
        self.error_message = ""

    def toggle_show_new_password(self):
        self.show_new_password = not self.show_new_password

    def toggle_show_confirm_password(self):
        self.show_confirm_password = not self.show_confirm_password

    @rx.var
    def password_strength(self) -> str:
        pwd = self.new_password
        if not pwd:
            return ""
        score = 0
        if len(pwd) >= 8:
            score += 1
        if re.search(r"[A-Z]", pwd):
            score += 1
        if re.search(r"[a-z]", pwd):
            score += 1
        if re.search(r"\d", pwd):
            score += 1
        if re.search(r"[^A-Za-z0-9]", pwd):
            score += 1

        if score <= 2:
            return "weak"
        if score in (3, 4):
            return "medium"
        return "strong"

    @rx.var
    def passwords_match(self) -> bool:
        if not self.confirm_password:
            return True  # don't flag an error before the user finishes typing
        return self.new_password == self.confirm_password

    @rx.var
    def can_submit(self) -> bool:
        return (
            len(self.new_password) >= 8
            and self.new_password == self.confirm_password
            and not self.is_loading
        )

    # ---------------- submit ----------------

    async def update_password(self):
        self.error_message = ""
        self.success_message = ""

        if len(self.new_password) < 8:
            self.error_message = "Password must be at least 8 characters."
            return

        if self.new_password != self.confirm_password:
            self.error_message = "Passwords do not match."
            return

        if self.password_strength == "weak":
            self.error_message = (
                "Password is too weak. Use a mix of upper/lowercase letters, "
                "numbers, and symbols."
            )
            return

        self.is_loading = True
        yield

        try:
            supabase = get_supabase()

            # get_supabase() just created a brand-new, sessionless client -
            # re-establish the recovery session on it before updating,
            # otherwise Supabase rejects with "Auth session missing!".
            if self._recovery_access_token and self._recovery_refresh_token:
                supabase.auth.set_session(
                    self._recovery_access_token, self._recovery_refresh_token
                )

            # Official Supabase Auth API call - updates the user tied to
            # the recovery session established in handle_recovery_tokens.
            supabase.auth.update_user({"password": self.new_password})

            self.is_loading = False
            self.success_message = "Password updated successfully! Redirecting to login..."
            self.new_password = ""
            self.confirm_password = ""
            yield

            await asyncio.sleep(2)

            # Recovery session is single-purpose - sign out so the user
            # lands on Login and authenticates fresh with the new password.
            supabase.auth.sign_out()
            yield rx.redirect("/login")

        except Exception as e:
            self.is_loading = False
            self.error_message = f"Failed to update password: {str(e)}"