import unittest
from unittest.mock import MagicMock, patch
import reflex as rx
from fraudradar_ai_scam_detection_v2.states.auth_state import AuthState


class TestOtpAuth(unittest.TestCase):
    def setUp(self):
        self.state = AuthState(_reflex_internal_init=True)
        self.state.loading = False
        self.state.otp_loading = False
        self.state.auth_error = ""
        self.state.auth_success = ""
        self.state.otp_error = ""
        self.state.show_otp_view = False
        self.state.otp_email = ""
        self.state.otp_code = ""

    def test_send_login_otp_invalid_email(self):
        """Invalid emails should be rejected before any API call."""
        self.state.login_email = "notanemail"
        self.state.send_login_otp()
        self.assertIn("valid email", self.state.auth_error.lower())
        self.assertFalse(self.state.show_otp_view)

    def test_send_login_otp_success_options(self):
        """send_login_otp must use should_create_user=False and transition to OTP view."""
        mock_sb = MagicMock()
        mock_sb.auth.sign_in_with_otp.return_value = MagicMock()

        self.state.login_email = "test@example.com"
        with patch("fraudradar_ai_scam_detection_v2.states.auth_state.get_supabase", return_value=mock_sb):
            res = self.state.send_login_otp()

        mock_sb.auth.sign_in_with_otp.assert_called_once()
        call_arg = mock_sb.auth.sign_in_with_otp.call_args[0][0]
        self.assertEqual(call_arg["email"], "test@example.com")
        self.assertEqual(call_arg["options"]["should_create_user"], False)
        self.assertTrue(self.state.show_otp_view)
        self.assertEqual(self.state.otp_email, "test@example.com")
        self.assertIn("verification code sent", self.state.auth_success.lower())

    def test_send_login_otp_user_not_found(self):
        """If user does not exist, provide user-friendly signup message."""
        mock_sb = MagicMock()
        mock_sb.auth.sign_in_with_otp.side_effect = Exception("User not found / Signups not allowed")

        self.state.login_email = "newuser@example.com"
        with patch("fraudradar_ai_scam_detection_v2.states.auth_state.get_supabase", return_value=mock_sb):
            self.state.send_login_otp()

        self.assertIn("no account found", self.state.auth_error.lower())
        self.assertFalse(self.state.show_otp_view)

    def test_verify_email_otp_invalid_length(self):
        """Verification codes with fewer than 4 or more than 12 digits must be rejected."""
        self.state.otp_email = "test@example.com"
        self.state.otp_code = "12"
        self.state.verify_email_otp()
        self.assertIn("valid verification code", self.state.otp_error)

    def test_verify_email_otp_success_8_digit(self):
        """8-digit Supabase codes must verify and redirect to /dashboard."""
        mock_sb = MagicMock()
        mock_session = MagicMock()
        mock_session.access_token = "access-123"
        mock_session.refresh_token = "refresh-456"
        mock_user = MagicMock()
        mock_user.id = "user-789"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = {"full_name": "Test User"}
        mock_res = MagicMock(session=mock_session, user=mock_user)
        mock_sb.auth.verify_otp.return_value = mock_res

        self.state.otp_email = "test@example.com"
        self.state.otp_code = "60269989"

        with patch("fraudradar_ai_scam_detection_v2.states.auth_state.get_supabase", return_value=mock_sb), \
             patch.object(AuthState, "_sync_profile_safe"):
            res = self.state.verify_email_otp()

        mock_sb.auth.verify_otp.assert_called_once()
        call_arg = mock_sb.auth.verify_otp.call_args[0][0]
        self.assertEqual(call_arg["token"], "60269989")
        self.assertTrue(self.state.is_authenticated)
        self.assertEqual(self.state.user_email, "test@example.com")
        self.assertIsNotNone(res)

    def test_verify_email_otp_success_6_digit(self):
        """Valid 6-digit code should verify and redirect to /dashboard."""
        mock_sb = MagicMock()
        mock_session = MagicMock()
        mock_session.access_token = "access-123"
        mock_session.refresh_token = "refresh-456"
        mock_user = MagicMock()
        mock_user.id = "user-789"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = {"full_name": "Test User"}
        mock_res = MagicMock(session=mock_session, user=mock_user)
        mock_sb.auth.verify_otp.return_value = mock_res

        self.state.otp_email = "test@example.com"
        self.state.otp_code = "123456"

        with patch("fraudradar_ai_scam_detection_v2.states.auth_state.get_supabase", return_value=mock_sb), \
             patch.object(AuthState, "_sync_profile_safe"):
            res = self.state.verify_email_otp()

        mock_sb.auth.verify_otp.assert_called_once()
        self.assertTrue(self.state.is_authenticated)
        self.assertEqual(self.state.user_email, "test@example.com")
        self.assertIsNotNone(res)

    def test_route_if_token_present_parses_tokens(self):
        """route_if_token_present dispatches process_auth_callback when access_token in json."""
        raw_json = '{"access_token": "abc123xyz", "type": "magiclink"}'
        res = self.state.route_if_token_present(raw_json)
        self.assertIsNotNone(res)


if __name__ == "__main__":
    unittest.main()
