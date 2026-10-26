import os
import unittest
from unittest.mock import patch, MagicMock
import httpx

from fraudradar_ai_scam_detection_v2.states.scan_state import (
    _check_google_safe_browsing,
    _check_virustotal,
    _check_phishtank,
    check_urls_external,
    _normalize_verdict,
    _is_safe_notification,
    _is_credential_request,
    _has_suspicious_url_or_threat,
    ScanState,
)


class TestGoogleSafeBrowsing(unittest.TestCase):
    """Independent unit tests for Google Safe Browsing integration."""

    def test_missing_env_var(self):
        with patch.dict(os.environ, {}, clear=True):
            res = _check_google_safe_browsing("https://example.com")
            self.assertFalse(res["checked"])
            self.assertEqual(res["status"], "NOT_CONFIGURED")

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._httpx.post")
    def test_invalid_api_key_400(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_post.return_value = mock_resp
        with patch.dict(os.environ, {"GOOGLE_SAFE_BROWSING_API_KEY": "fake_invalid_key"}):
            res = _check_google_safe_browsing("https://example.com")
            self.assertFalse(res["checked"])
            self.assertEqual(res["status"], "ERROR")
            self.assertIn("Invalid API key", res["error"])

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._httpx.post")
    def test_quota_exceeded_429(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_post.return_value = mock_resp
        with patch.dict(os.environ, {"GOOGLE_SAFE_BROWSING_API_KEY": "fake_key"}):
            res = _check_google_safe_browsing("https://example.com")
            self.assertFalse(res["checked"])
            self.assertEqual(res["status"], "RATE_LIMITED")

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._httpx.post")
    def test_timeout(self, mock_post):
        mock_post.side_effect = httpx.TimeoutException("Connection timed out")
        with patch.dict(os.environ, {"GOOGLE_SAFE_BROWSING_API_KEY": "fake_key"}):
            res = _check_google_safe_browsing("https://example.com")
            self.assertFalse(res["checked"])
            self.assertEqual(res["status"], "TIMEOUT")

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._httpx.post")
    def test_server_error_500(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_post.return_value = mock_resp
        with patch.dict(os.environ, {"GOOGLE_SAFE_BROWSING_API_KEY": "fake_key"}):
            res = _check_google_safe_browsing("https://example.com")
            self.assertFalse(res["checked"])
            self.assertEqual(res["status"], "ERROR")

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._httpx.post")
    def test_malformed_response(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = "not a dict"
        mock_post.return_value = mock_resp
        with patch.dict(os.environ, {"GOOGLE_SAFE_BROWSING_API_KEY": "fake_key"}):
            res = _check_google_safe_browsing("https://example.com")
            self.assertFalse(res["checked"])
            self.assertEqual(res["status"], "ERROR")

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._httpx.post")
    def test_malicious_match(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "matches": [{"threatType": "MALWARE", "platformType": "ANY_PLATFORM"}]
        }
        mock_post.return_value = mock_resp
        with patch.dict(os.environ, {"GOOGLE_SAFE_BROWSING_API_KEY": "fake_key"}):
            res = _check_google_safe_browsing("http://malware-site.xyz")
            self.assertTrue(res["checked"])
            self.assertEqual(res["status"], "MALICIOUS")
            self.assertTrue(res["is_dangerous"])
            self.assertEqual(res["threats"], ["MALWARE"])

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._httpx.post")
    def test_clean_no_match(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {}
        mock_post.return_value = mock_resp
        with patch.dict(os.environ, {"GOOGLE_SAFE_BROWSING_API_KEY": "fake_key"}):
            res = _check_google_safe_browsing("https://amazon.in")
            self.assertTrue(res["checked"])
            self.assertEqual(res["status"], "SAFE")
            self.assertFalse(res["is_dangerous"])


class TestVirusTotal(unittest.TestCase):
    """Independent unit tests for VirusTotal API integration."""

    def test_missing_env_var(self):
        with patch.dict(os.environ, {}, clear=True):
            res = _check_virustotal("https://example.com")
            self.assertFalse(res["checked"])
            self.assertEqual(res["status"], "NOT_CONFIGURED")

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._httpx.get")
    def test_invalid_api_key_401(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_get.return_value = mock_resp
        with patch.dict(os.environ, {"VIRUSTOTAL_API_KEY": "fake_invalid_key"}):
            res = _check_virustotal("https://example.com")
            self.assertFalse(res["checked"])
            self.assertEqual(res["status"], "ERROR")
            self.assertIn("Invalid API key", res["error"])

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._httpx.get")
    def test_quota_exceeded_429(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_get.return_value = mock_resp
        with patch.dict(os.environ, {"VIRUSTOTAL_API_KEY": "fake_key"}):
            res = _check_virustotal("https://example.com")
            self.assertFalse(res["checked"])
            self.assertEqual(res["status"], "RATE_LIMITED")

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._httpx.get")
    def test_timeout(self, mock_get):
        mock_get.side_effect = httpx.TimeoutException("Read timed out")
        with patch.dict(os.environ, {"VIRUSTOTAL_API_KEY": "fake_key"}):
            res = _check_virustotal("https://example.com")
            self.assertFalse(res["checked"])
            self.assertEqual(res["status"], "TIMEOUT")

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._httpx.get")
    def test_not_found_404(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp
        with patch.dict(os.environ, {"VIRUSTOTAL_API_KEY": "fake_key"}):
            res = _check_virustotal("https://brand-new-domain-never-seen.com")
            self.assertFalse(res["checked"])
            self.assertEqual(res["status"], "NOT_FOUND")

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._httpx.get")
    def test_malicious_match(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "attributes": {
                    "last_analysis_stats": {
                        "malicious": 8,
                        "suspicious": 2,
                        "harmless": 60,
                        "undetected": 5,
                    }
                }
            }
        }
        mock_get.return_value = mock_resp
        with patch.dict(os.environ, {"VIRUSTOTAL_API_KEY": "fake_key"}):
            res = _check_virustotal("http://phishing-site.xyz")
            self.assertTrue(res["checked"])
            self.assertEqual(res["status"], "MALICIOUS")
            self.assertTrue(res["is_dangerous"])
            self.assertEqual(res["malicious_count"], 8)

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._httpx.get")
    def test_clean_no_match(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "attributes": {
                    "last_analysis_stats": {
                        "malicious": 0,
                        "suspicious": 0,
                        "harmless": 75,
                        "undetected": 3,
                    }
                }
            }
        }
        mock_get.return_value = mock_resp
        with patch.dict(os.environ, {"VIRUSTOTAL_API_KEY": "fake_key"}):
            res = _check_virustotal("https://sbi.co.in")
            self.assertTrue(res["checked"])
            self.assertEqual(res["status"], "SAFE")
            self.assertFalse(res["is_dangerous"])


class TestFailureHandling(unittest.TestCase):
    """Verify that external API errors return UNKNOWN/unavailable and never safe."""

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._check_google_safe_browsing")
    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._check_virustotal")
    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._check_phishtank")
    def test_api_failure_not_treated_as_safe(self, mock_pt, mock_vt, mock_gsb):
        mock_gsb.return_value = {"checked": False, "status": "RATE_LIMITED", "source": "Google Safe Browsing"}
        mock_vt.return_value = {"checked": False, "status": "ERROR", "source": "VirusTotal"}
        mock_pt.return_value = {"checked": False, "status": "TIMEOUT", "source": "PhishTank"}

        results = check_urls_external(["http://unverified-site.com"])
        self.assertEqual(len(results), 1)
        r = results[0]
        # Must not be flagged, but critically must NOT be safe!
        self.assertFalse(r["is_flagged"])
        self.assertFalse(r["is_safe"])
        self.assertTrue(r["is_unavailable"])
        self.assertEqual(len(r["safe_by"]), 0)
        self.assertEqual(len(r["unavailable_by"]), 3)


class TestVerdictConsistency(unittest.TestCase):
    """Verify strict consistency between score and verdict."""

    def test_verdict_consistency_rules(self):
        # Score >= 70 must be HIGH
        self.assertEqual(_normalize_verdict("SAFE", 85), "HIGH")
        self.assertEqual(_normalize_verdict("MEDIUM", 70), "HIGH")
        self.assertEqual(_normalize_verdict("", 90), "HIGH")

        # Score 40-69 must be MEDIUM (or HIGH if explicitly flagged)
        self.assertEqual(_normalize_verdict("SAFE", 55), "MEDIUM")
        self.assertEqual(_normalize_verdict("MEDIUM", 45), "MEDIUM")
        self.assertEqual(_normalize_verdict("HIGH", 60), "HIGH")

        # Score < 40 cannot be HIGH
        self.assertEqual(_normalize_verdict("HIGH", 20), "SAFE")
        self.assertEqual(_normalize_verdict("SAFE", 10), "SAFE")
        self.assertEqual(_normalize_verdict("MEDIUM", 35), "MEDIUM")


class TestFullScannerSyntheticMessages(unittest.IsolatedAsyncioTestCase):
    """Test full scanner on the 5 mandatory synthetic messages."""

    async def asyncSetUp(self):
        self.state = ScanState(_reflex_internal_init=True)
        self.patcher = patch("fraudradar_ai_scam_detection_v2.states.scan_state.check_urls_external", return_value=[])
        self.mock_urls = self.patcher.start()
        self.patcher_llm = patch.object(
            ScanState,
            "_analyze_sync",
            side_effect=lambda text, itype="text": self.state._heuristic_fallback(text),
        )
        self.mock_llm = self.patcher_llm.start()

    async def asyncTearDown(self):
        self.patcher_llm.stop()
        self.patcher.stop()

    async def test_synthetic_1_legitimate_bank_otp(self):
        # 1. Legitimate bank OTP notification
        msg = "Your OTP is 384827 for online purchase of Rs 1,499 at Amazon. Valid for 10 minutes. Do not share this code with anyone, including bank officials."
        await self.state.analyze(text=msg, input_type="text")
        self.assertTrue(self.state.has_result)
        self.assertEqual(self.state.verdict, "SAFE")
        self.assertLess(self.state.risk_score, 40)
        self.assertIn("Safe Notification", self.state.categories)

    async def test_synthetic_2_request_to_share_otp(self):
        # 2. Request to share an OTP
        msg = "Dear customer, your SBI NetBanking account is suspended due to invalid KYC. Please reply with OTP or send your OTP to 9876543210 to reactivate."
        await self.state.analyze(text=msg, input_type="text")
        self.assertTrue(self.state.has_result)
        self.assertEqual(self.state.verdict, "HIGH")
        self.assertGreaterEqual(self.state.risk_score, 70)

    async def test_synthetic_3_suspicious_payment_refund_link(self):
        # 3. Suspicious payment/refund link
        msg = "Electricity Department alert: Your bill of Rs 4,500 was charged twice. Click here to claim your refund: http://quick-refund-claim.xyz/sbi immediately."
        await self.state.analyze(text=msg, input_type="text")
        self.assertTrue(self.state.has_result)
        self.assertEqual(self.state.verdict, "HIGH")
        self.assertGreaterEqual(self.state.risk_score, 70)
        # Verify it was NOT overridden by safe notification
        self.assertNotEqual(self.state.verdict, "SAFE")

    async def test_synthetic_4_legitimate_with_trusted_url(self):
        # 4. Legitimate message containing a trusted URL
        msg = "Your Amazon order #402-9871234 has been shipped and will arrive tomorrow. Track your package: https://amazon.in/orders. Thank you for shopping with us."
        await self.state.analyze(text=msg, input_type="text")
        self.assertTrue(self.state.has_result)
        self.assertEqual(self.state.verdict, "SAFE")
        self.assertLess(self.state.risk_score, 40)

    async def test_synthetic_5_scam_with_no_url(self):
        # 5. Scam message with no URL
        msg = "URGENT NOTICE: CBI Officer calling from Cyber Crime Headquarters. Your bank account is linked to an illegal money laundering syndicate. Transfer Rs 50,000 immediately to the government clearance account or you will be arrested in 2 hours."
        await self.state.analyze(text=msg, input_type="text")
        self.assertTrue(self.state.has_result)
        # Should be classified as high or medium risk scam, definitely NOT safe
        self.assertIn(self.state.verdict, ("HIGH", "MEDIUM"))
        self.assertGreaterEqual(self.state.risk_score, 40)

    async def test_synthetic_6_job_task_scam(self):
        # 6. Part-time YouTube task / work from home scam
        msg = "Part-Time Work from Home Opportunity! Earn Rs 2,500 - Rs 8,000 daily by simply liking YouTube videos and rating hotels on Google Maps. No experience needed. Daily payout via UPI. Contact HR Priya on WhatsApp: +91-9123456789 to claim your Rs 500 bonus."
        await self.state.analyze(text=msg, input_type="text")
        self.assertTrue(self.state.has_result)
        self.assertEqual(self.state.verdict, "HIGH")
        self.assertGreaterEqual(self.state.risk_score, 80)
        self.assertIn("Job Scam", self.state.categories)

    async def test_synthetic_7_electricity_disconnection_threat(self):
        # 7. Electricity bill disconnection panic lure
        msg = "Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM from the electricity office because your previous month's bill was not updated. Please immediately contact our officer at +91-9876543210."
        await self.state.analyze(text=msg, input_type="text")
        self.assertTrue(self.state.has_result)
        self.assertEqual(self.state.verdict, "HIGH")
        self.assertGreaterEqual(self.state.risk_score, 80)
        self.assertIn("Utility Scam", self.state.categories)

    async def test_clear_result_resets_input_and_results(self):
        # Verify that clear_result empties input_text, has_result, and error
        self.state.input_text = "Suspicious phishing text to clear"
        self.state.has_result = True
        self.state.error = "Some previous scan error"

        await self.state.clear_result()

        self.assertEqual(self.state.input_text, "")
        self.assertFalse(self.state.has_result)
        self.assertEqual(self.state.error, "")


class TestSafeOverridePrevention(unittest.TestCase):
    """Regression test ensuring suspicious evidence cannot be overridden by safe rules."""

    def test_fake_debit_alert_with_untrusted_link(self):
        msg = "Rs 45,000 debited from SBI A/c 5432 on 20-Oct. If this transaction was not done by you, cancel transaction immediately at http://sbi-card-support.xyz/block"
        self.assertTrue(_has_suspicious_url_or_threat(msg))
        # Must NOT be identified as safe notification because of the unverified link
        self.assertFalse(_is_safe_notification(msg))


if __name__ == "__main__":
    unittest.main()
