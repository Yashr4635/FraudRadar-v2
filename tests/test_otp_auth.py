import os
import unittest
from unittest.mock import patch
import reflex as rx

# Enable dev mode for tests to capture emails in outbox
os.environ["EMAIL_DEV_MODE"] = "true"

from fraudradar_ai_scam_detection_v2.states.auth_state import AuthState
from fraudradar_ai_scam_detection_v2.services import (
    auth_db,
    otp_service,
    EmailService,
    mask_email,
)


class TestUnifiedOtpAuthentication(unittest.TestCase):
    def setUp(self):
        EmailService._outbox.clear()
        conn = auth_db.get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM users;")
                conn.execute("DELETE FROM otps;")
                conn.execute("DELETE FROM pending_signups;")
                conn.execute("DELETE FROM delivery_logs;")
        finally:
            conn.close()
        self.state = AuthState(_reflex_internal_init=True)
        self.state.loading = False
        self.state.otp_loading = False
        self.state.auth_error = ""
        self.state.auth_success = ""
        self.state.otp_error = ""
        self.state.show_otp_view = False
        self.state.otp_email = ""
        self.state.otp_code = ""
        self.state.access_token = ""
        self.state.refresh_token = ""
        self.state.is_authenticated = False
        self.state.can_resend = True
        self.state.resend_cooldown = 0

    # ─── Email Masking & Utilities ──────────────────────────────────────────

    def test_email_masking(self):
        """Emails must be masked for user privacy in UI and logs."""
        self.assertEqual(mask_email("alice@gmail.com"), "a***e@gmail.com")
        self.assertEqual(mask_email("robert.smith@company.org"), "r******h@company.org")
        self.assertEqual(mask_email("ab@test.com"), "a*@test.com")

    def test_otp_generation_format(self):
        """OTP must be exactly 8 digits with leading zeros supported."""
        for _ in range(50):
            code = otp_service.generate_8_digit_otp()
            self.assertEqual(len(code), 8)
            self.assertTrue(code.isdigit())

    # ─── Signup Flow (New Users) ────────────────────────────────────────────

    def test_signup_flow_success(self):
        """New user signup: validates input, sends 8-digit OTP, verifies and signs in."""
        test_email = "new_signup_user@example.com"
        self.state.signup_name = "Jane Doe"
        self.state.signup_email = test_email
        self.state.signup_password = "SecurePassword123!"
        self.state.signup_confirm = "SecurePassword123!"
        self.state.accept_terms = True

        # 1. Trigger signup
        self.state.signup()

        # Must transition to OTP view and show accurate masked email
        self.assertTrue(self.state.show_otp_view)
        self.assertEqual(self.state.otp_email, test_email)
        self.assertEqual(self.state.otp_type, "signup")
        self.assertIn("verification code", self.state.auth_success.lower())

        # Email must have been dispatched to outbox
        self.assertTrue(len(EmailService._outbox) > 0)
        sent_email = EmailService._outbox[-1]
        self.assertEqual(sent_email["recipient"], test_email)
        self.assertEqual(sent_email["purpose"], "signup")

        # Extract 8-digit OTP from email body
        import re
        match = re.search(r"\b(\d{4}\s\d{4})\b", sent_email["text_content"])
        self.assertIsNotNone(match)
        raw_code = match.group(1).replace(" ", "")
        self.assertEqual(len(raw_code), 8)

        # 2. User enters the 8-digit OTP
        self.state.otp_code = raw_code
        res = self.state.verify_email_otp()

        # User is authenticated and redirected to dashboard
        self.assertTrue(self.state.is_authenticated)
        self.assertEqual(self.state.user_email, test_email)
        self.assertEqual(self.state.user_name, "Jane Doe")
        self.assertTrue(len(self.state.access_token) > 20)
        self.assertFalse(self.state.show_otp_view)

        # User record exists in local DB and is verified
        db_user = auth_db.get_user_by_email(test_email)
        self.assertIsNotNone(db_user)
        self.assertEqual(db_user["is_verified"], 1)

    def test_signup_duplicate_email_rejected(self):
        """Cannot register with an already verified email."""
        dup_email = "existing_user@example.com"
        auth_db.create_user(dup_email, "Existing User", "Pass123!", is_verified=True)

        self.state.signup_name = "Imp"
        self.state.signup_email = dup_email
        self.state.signup_password = "Password123!"
        self.state.signup_confirm = "Password123!"
        self.state.accept_terms = True

        self.state.signup()

        self.assertFalse(self.state.show_otp_view)
        self.assertIn("already exists", self.state.auth_error.lower())

    # ─── Login Flow (Existing Users) ────────────────────────────────────────

    def test_login_otp_unregistered_email_rejected(self):
        """Unregistered email on login must be rejected without creating account."""
        self.state.login_email = "non_existent_user@example.com"
        self.state.send_login_otp()

        self.assertFalse(self.state.show_otp_view)
        self.assertIn("no account found", self.state.auth_error.lower())

        # Verify no user was created
        self.assertIsNone(auth_db.get_user_by_email("non_existent_user@example.com"))

    def test_login_otp_success_for_existing_user(self):
        """Existing verified user receives 8-digit OTP and logs in successfully."""
        login_email = "verified_member@example.com"
        user = auth_db.create_user(login_email, "Verified Member", is_verified=True)

        self.state.login_email = login_email
        self.state.send_login_otp()

        self.assertTrue(self.state.show_otp_view)
        self.assertEqual(self.state.otp_email, login_email)
        self.assertEqual(self.state.otp_type, "login")

        # Email delivered
        self.assertTrue(len(EmailService._outbox) > 0)
        sent_email = EmailService._outbox[-1]
        self.assertEqual(sent_email["recipient"], login_email)

        import re
        match = re.search(r"\b(\d{4}\s\d{4})\b", sent_email["text_content"])
        self.assertIsNotNone(match)
        code = match.group(1).replace(" ", "")

        # Verify OTP
        self.state.otp_code = code
        self.state.verify_email_otp()

        self.assertTrue(self.state.is_authenticated)
        self.assertEqual(self.state.user_email, login_email)
        self.assertFalse(self.state.show_otp_view)

    # ─── Security Checks ────────────────────────────────────────────────────

    def test_otp_single_use_enforcement(self):
        """OTP cannot be reused a second time."""
        email = "single_use@example.com"
        auth_db.create_user(email, "Single Use User", is_verified=True)

        self.state.login_email = email
        self.state.send_login_otp()

        import re
        match = re.search(r"\b(\d{4}\s\d{4})\b", EmailService._outbox[-1]["text_content"])
        code = match.group(1).replace(" ", "")

        # 1st verification succeeds
        self.state.otp_code = code
        self.state.verify_email_otp()
        self.assertTrue(self.state.is_authenticated)

        # 2nd verification attempt must fail
        ok, msg = auth_db.verify_and_consume_otp(email, "login", code)
        self.assertFalse(ok)
        self.assertIn("no active verification code", msg.lower())

    def test_incorrect_otp_attempt_lockout(self):
        """Entering incorrect OTP decrements attempts and locks out after 5 failures."""
        email = "lockout_test@example.com"
        auth_db.create_user(email, "Lockout User", is_verified=True)
        auth_db.store_otp(email, "login", "88888888", max_attempts=5)

        # 4 wrong attempts
        for i in range(1, 5):
            ok, msg = auth_db.verify_and_consume_otp(email, "login", "00000000")
            self.assertFalse(ok)
            self.assertIn("remaining", msg.lower())

        # 5th wrong attempt triggers invalidation
        ok, msg = auth_db.verify_and_consume_otp(email, "login", "00000000")
        self.assertFalse(ok)
        self.assertIn("maximum attempts exceeded", msg.lower())

        # Correct code now fails because OTP was locked out
        ok, msg = auth_db.verify_and_consume_otp(email, "login", "88888888")
        self.assertFalse(ok)

    def test_purpose_separation(self):
        """Signup OTP cannot verify a login request, and vice-versa."""
        email = "purpose_test@example.com"
        auth_db.store_otp(email, "signup", "12345678")

        # Attempting to verify as 'login' must fail
        ok, msg = auth_db.verify_and_consume_otp(email, "login", "12345678")
        self.assertFalse(ok)

        # Verifying as 'signup' succeeds
        ok, msg = auth_db.verify_and_consume_otp(email, "signup", "12345678")
        self.assertTrue(ok)

    def test_old_otp_invalidation_on_resend(self):
        """Requesting a new OTP invalidates the previous one."""
        email = "resend_invalidation@example.com"
        auth_db.create_user(email, "Resend User", is_verified=True)

        self.state.login_email = email
        self.state.send_login_otp()

        import re
        first_code = re.search(r"\b(\d{4}\s\d{4})\b", EmailService._outbox[-1]["text_content"]).group(1).replace(" ", "")

        # Resend code
        self.state.can_resend = True
        self.state.resend_cooldown = 0
        self.state.resend_otp_code()

        second_code = re.search(r"\b(\d{4}\s\d{4})\b", EmailService._outbox[-1]["text_content"]).group(1).replace(" ", "")
        self.assertNotEqual(first_code, second_code)

        # First code must now be invalid
        ok, _ = auth_db.verify_and_consume_otp(email, "login", first_code)
        self.assertFalse(ok)

        # Second code is valid
        ok, _ = auth_db.verify_and_consume_otp(email, "login", second_code)
        self.assertTrue(ok)

    # ─── Session Management & Logout ────────────────────────────────────────

    def test_jwt_session_restoration_and_logout(self):
        """Signed JWT allows session restoration, and logout clears session."""
        user = auth_db.create_user("session_user@example.com", "Session User", is_verified=True)
        token = otp_service.create_user_jwt(user)

        self.state.access_token = token
        restored = self.state._restore_session_sync()
        self.assertTrue(restored)
        self.assertTrue(self.state.is_authenticated)
        self.assertEqual(self.state.user_email, "session_user@example.com")

        # Logout
        self.state.logout()
        self.assertFalse(self.state.is_authenticated)
        self.assertEqual(self.state.access_token, "")


if __name__ == "__main__":
    unittest.main()
