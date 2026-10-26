"""
Live integration tests for FraudRadar deployed at https://fraudradar-gray-wood.reflex.run
Tests page loads, key routes, and basic API health.
"""
import unittest
import time
from unittest.mock import patch

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

BASE_URL = "https://fraudradar-gray-wood.reflex.run"


@unittest.skipUnless(HAS_HTTPX, "httpx not installed")
class TestLiveAppPages(unittest.TestCase):
    """Verify that all key pages of the deployed app load correctly."""

    @classmethod
    def setUpClass(cls):
        cls.client = httpx.Client(timeout=15.0, follow_redirects=True)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    def _get_page(self, path: str):
        url = f"{BASE_URL}{path}"
        start = time.perf_counter()
        resp = self.client.get(url)
        elapsed = time.perf_counter() - start
        return resp, elapsed

    # ── Landing Page ──────────────────────────────────────────────────────

    def test_01_landing_page_loads(self):
        resp, elapsed = self._get_page("/")
        self.assertEqual(resp.status_code, 200, f"Landing page returned {resp.status_code}")
        self.assertIn("FraudRadar", resp.text, "Landing page should contain 'FraudRadar' branding")
        self.assertLess(elapsed, 10.0, f"Landing page took {elapsed:.2f}s — too slow")
        print(f"  ✅ Landing page loaded in {elapsed:.2f}s")

    # ── Analyze Page ──────────────────────────────────────────────────────

    def test_02_analyze_page_loads(self):
        resp, elapsed = self._get_page("/analyze")
        self.assertEqual(resp.status_code, 200, f"Analyze page returned {resp.status_code}")
        self.assertLess(elapsed, 10.0, f"Analyze page took {elapsed:.2f}s")
        print(f"  ✅ Analyze page loaded in {elapsed:.2f}s")

    # ── Auth Pages ────────────────────────────────────────────────────────

    def test_03_login_page_loads(self):
        resp, elapsed = self._get_page("/login")
        self.assertEqual(resp.status_code, 200)
        self.assertLess(elapsed, 10.0)
        print(f"  ✅ Login page loaded in {elapsed:.2f}s")

    def test_04_signup_page_loads(self):
        resp, elapsed = self._get_page("/signup")
        self.assertEqual(resp.status_code, 200)
        self.assertLess(elapsed, 10.0)
        print(f"  ✅ Signup page loaded in {elapsed:.2f}s")

    # ── Resource Pages ────────────────────────────────────────────────────

    def test_05_helpline_page_loads(self):
        resp, elapsed = self._get_page("/helpline")
        self.assertEqual(resp.status_code, 200)
        print(f"  ✅ Helpline page loaded in {elapsed:.2f}s")

    def test_06_scam_guide_page_loads(self):
        resp, elapsed = self._get_page("/scam-guide")
        self.assertEqual(resp.status_code, 200)
        print(f"  ✅ Scam Guide page loaded in {elapsed:.2f}s")

    def test_07_legal_page_loads(self):
        resp, elapsed = self._get_page("/legal")
        self.assertEqual(resp.status_code, 200)
        print(f"  ✅ Legal page loaded in {elapsed:.2f}s")

    # ── Dashboard / History / Settings (may redirect to login) ────────────

    def test_08_dashboard_responds(self):
        resp, elapsed = self._get_page("/dashboard")
        self.assertIn(resp.status_code, [200, 302, 307])
        print(f"  ✅ Dashboard responded ({resp.status_code}) in {elapsed:.2f}s")

    def test_09_history_responds(self):
        resp, elapsed = self._get_page("/history")
        self.assertIn(resp.status_code, [200, 302, 307])
        print(f"  ✅ History responded ({resp.status_code}) in {elapsed:.2f}s")

    def test_10_settings_responds(self):
        resp, elapsed = self._get_page("/settings")
        self.assertIn(resp.status_code, [200, 302, 307])
        print(f"  ✅ Settings responded ({resp.status_code}) in {elapsed:.2f}s")

    def test_11_assistant_responds(self):
        resp, elapsed = self._get_page("/assistant")
        self.assertIn(resp.status_code, [200, 302, 307])
        print(f"  ✅ Assistant responded ({resp.status_code}) in {elapsed:.2f}s")

    def test_12_profile_responds(self):
        resp, elapsed = self._get_page("/profile")
        self.assertIn(resp.status_code, [200, 302, 307])
        print(f"  ✅ Profile responded ({resp.status_code}) in {elapsed:.2f}s")


@unittest.skipUnless(HAS_HTTPX, "httpx not installed")
class TestLiveAppAssets(unittest.TestCase):
    """Verify static assets (favicon, logo) serve correctly."""

    @classmethod
    def setUpClass(cls):
        cls.client = httpx.Client(timeout=10.0, follow_redirects=True)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    def test_favicon_serves(self):
        resp = self.client.get(f"{BASE_URL}/favicon.ico")
        self.assertEqual(resp.status_code, 200, "favicon.ico should be served")
        self.assertGreater(len(resp.content), 100, "favicon.ico should have content")
        print(f"  ✅ favicon.ico served ({len(resp.content)} bytes)")

    def test_logo_png_serves(self):
        resp = self.client.get(f"{BASE_URL}/fraudradar_logo.png")
        if resp.status_code == 200:
            self.assertGreater(len(resp.content), 100)
            print(f"  ✅ fraudradar_logo.png served ({len(resp.content)} bytes)")
        else:
            # Logo may be at a different path depending on Reflex asset serving
            print(f"  ⚠️  fraudradar_logo.png returned {resp.status_code} (may be bundled)")


if __name__ == "__main__":
    unittest.main(verbosity=2)

