import time
import unittest
from unittest.mock import patch, MagicMock

from fraudradar_ai_scam_detection_v2.states.scan_state import (
    check_urls_external,
    _get_cached_url,
    _set_cached_url,
    _url_cache,
    ScanState,
)


class TestPerformanceOptimizations(unittest.TestCase):
    """Benchmark tests validating the speed optimizations."""

    def setUp(self):
        _url_cache.clear()

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._check_google_safe_browsing")
    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._check_virustotal")
    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._check_phishtank")
    def test_parallel_external_checks_speedup(self, mock_pt, mock_vt, mock_gsb):
        def simulated_delay(url):
            time.sleep(0.05)
            return {"checked": True, "status": "SAFE", "source": "mock"}

        mock_gsb.side_effect = simulated_delay
        mock_vt.side_effect = simulated_delay
        mock_pt.side_effect = simulated_delay

        start = time.perf_counter()
        # 3 URLs x 3 engines = 9 checks.
        # In serial: 9 * 0.05s = 0.45s.
        # In parallel (3 workers for URLs, 3 for engines): ~0.05s - 0.12s.
        results = check_urls_external([
            "https://url1.com",
            "https://url2.com",
            "https://url3.com",
        ])
        elapsed = time.perf_counter() - start

        self.assertEqual(len(results), 3)
        # Verify elapsed time is much faster than serial execution (0.45s)
        self.assertLess(elapsed, 0.30, f"Expected parallel execution < 0.30s, got {elapsed:.3f}s")

    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._check_phishtank")
    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._check_virustotal")
    @patch("fraudradar_ai_scam_detection_v2.states.scan_state._check_google_safe_browsing")
    def test_lru_cache_hit_instant(self, mock_gsb, mock_vt, mock_pt):
        mock_gsb.return_value = {"checked": True, "status": "SAFE", "source": "Google Safe Browsing"}
        mock_vt.return_value = {"checked": True, "status": "SAFE", "source": "VirusTotal"}
        mock_pt.return_value = {"checked": False, "status": "NOT_CONFIGURED", "source": "PhishTank"}

        # First check populates cache
        check_urls_external(["https://repeated-domain.com"])

        # Second check should hit cache instantly (< 0.005s)
        start = time.perf_counter()
        results2 = check_urls_external(["https://repeated-domain.com"])
        elapsed = time.perf_counter() - start

        self.assertEqual(len(results2), 1)
        self.assertLess(elapsed, 0.005, f"Cache hit should be instantaneous, got {elapsed:.4f}s")


if __name__ == "__main__":
    unittest.main()
