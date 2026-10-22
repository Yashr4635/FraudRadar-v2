import os
import unittest
from unittest.mock import MagicMock, patch
import reflex as rx

from fraudradar_ai_scam_detection_v2.states.auth_state import (
    AuthState,
    get_app_base_url,
    get_auth_callback_url,
)


class TestGoogleAuth(unittest.TestCase):
    def setUp(self):
        self.state = AuthState(_reflex_internal_init=True)
        self.state.loading = False
        self.state.google_loading = False
        self.state.auth_error = ""
        self.state.auth_success = ""

    def test_app_base_url_default_localhost(self):
        """When no external deployment variables are set, default to localhost:3000."""
        with patch.dict(os.environ, {}, clear=True):
            base_url = get_app_base_url()
            self.assertEqual(base_url, "http://localhost:3000")

    def test_app_base_url_custom_env(self):
        """Custom APP_BASE_URL or SITE_URL should be honored."""
        with patch.dict(os.environ, {"APP_BASE_URL": "https://fraudradar.ai"}):
            self.assertEqual(get_app_base_url(), "https://fraudradar.ai")

    def test_app_base_url_render(self):
        """Render deployment environment variables should be auto-detected."""
        with patch.dict(os.environ, {"RENDER_EXTERNAL_URL": "https://fraudradar-v2.onrender.com"}, clear=True):
            self.assertEqual(get_app_base_url(), "https://fraudradar-v2.onrender.com")

    def test_get_auth_callback_url(self):
        """Callback URL should always point to /auth/callback."""
        with patch.dict(os.environ, {"APP_BASE_URL": "http://localhost:3000"}):
            self.assertEqual(get_auth_callback_url(), "http://localhost:3000/auth/callback")

    def test_login_with_google_unconfigured_supabase(self):
        """When Supabase is not configured, login_with_google should set an informative error."""
        with patch("fraudradar_ai_scam_detection_v2.states.auth_state.get_supabase", return_value=None):
            self.state.login_with_google()
            self.assertIn("Authentication service is not configured", self.state.auth_error)
            self.assertFalse(self.state.google_loading)

    def test_login_with_google_success(self):
        """When Supabase returns an OAuth redirect URL, it should return rx.redirect."""
        mock_sb = MagicMock()
        mock_oauth_res = MagicMock()
        mock_oauth_res.url = "https://accounts.google.com/o/oauth2/v2/auth?client_id=123"
        mock_sb.auth.sign_in_with_oauth.return_value = mock_oauth_res

        with patch("fraudradar_ai_scam_detection_v2.states.auth_state.get_supabase", return_value=mock_sb):
            res = self.state.login_with_google()
            mock_sb.auth.sign_in_with_oauth.assert_called_once()
            call_args = mock_sb.auth.sign_in_with_oauth.call_args[0][0]
            self.assertEqual(call_args["provider"], "google")
            self.assertIn("/auth/callback", call_args["options"]["redirect_to"])
            self.assertFalse(self.state.google_loading)
            self.assertEqual(self.state.auth_error, "")

    def test_login_with_google_api_exception(self):
        """When sign_in_with_oauth raises an exception, it should be caught and surfaced gracefully."""
        mock_sb = MagicMock()
        mock_sb.auth.sign_in_with_oauth.side_effect = RuntimeError("Network timeout contacting Supabase")

        with patch("fraudradar_ai_scam_detection_v2.states.auth_state.get_supabase", return_value=mock_sb):
            self.state.login_with_google()
            self.assertTrue(len(self.state.auth_error) > 0)
            self.assertIn("try again", self.state.auth_error.lower())
            self.assertFalse(self.state.google_loading)

    def test_extract_provider_google(self):
        """Ensure provider extraction identifies Google metadata."""
        # 1. From app_metadata provider
        user1 = MagicMock()
        user1.app_metadata = {"provider": "google"}
        self.assertEqual(self.state._extract_provider(user1), "google")

        # 2. From app_metadata providers list
        user2 = MagicMock()
        user2.app_metadata = {"providers": ["google"]}
        self.assertEqual(self.state._extract_provider(user2), "google")

        # 3. From identities
        user3 = MagicMock()
        user3.app_metadata = {}
        identity = MagicMock()
        identity.provider = "google"
        user3.identities = [identity]
        self.assertEqual(self.state._extract_provider(user3), "google")

        # 4. Default fallback
        user4 = MagicMock()
        user4.app_metadata = {}
        user4.identities = []
        self.assertEqual(self.state._extract_provider(user4), "email")

    def test_apply_user_session_google_profile(self):
        """User metadata from Google (name and avatar/picture) should be properly mapped."""
        user = MagicMock()
        user.id = "goog-usr-456"
        user.email = "testuser@gmail.com"
        user.user_metadata = {
            "full_name": "Rohan Patel",
            "picture": "https://lh3.googleusercontent.com/a/random-avatar",
        }
        session = MagicMock()
        session.access_token = "access-xyz"
        session.refresh_token = "refresh-xyz"

        self.state._apply_user_session(user, session, provider="google")

        self.assertTrue(self.state.is_authenticated)
        self.assertEqual(self.state.user_id, "goog-usr-456")
        self.assertEqual(self.state.user_email, "testuser@gmail.com")
        self.assertEqual(self.state.user_name, "Rohan Patel")
        self.assertEqual(self.state.user_avatar_url, "https://lh3.googleusercontent.com/a/random-avatar")
        self.assertEqual(self.state.user_provider, "google")


if __name__ == "__main__":
    unittest.main()
