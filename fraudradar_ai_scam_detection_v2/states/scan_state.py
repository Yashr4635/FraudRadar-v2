import os
import re
import csv
import io
import json
import logging
import datetime
import asyncio
import time as _time
import base64 as _base64
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor
import reflex as rx
from typing import TypedDict

try:
    import httpx as _httpx
except ImportError:
    _httpx = None

try:
    from groq import Groq
except Exception:
    logging.exception("Unexpected error")
    Groq = None

# ─── Fast Connection Pool & In-Memory Threat Cache ────────────────────────────

_http_client_instance: "_httpx.Client | None" = None


def _get_http_client():
    global _http_client_instance
    if _httpx is None:
        return None
    if _http_client_instance is None or _http_client_instance.is_closed:
        _http_client_instance = _httpx.Client(
            timeout=4.0,
            limits=_httpx.Limits(max_keepalive_connections=20, max_connections=50),
            headers={"User-Agent": "FraudRadar/2.0"},
        )
    return _http_client_instance


def _http_post(url: str, **kwargs):
    if hasattr(_httpx.post, "return_value") or hasattr(_httpx.post, "side_effect"):
        return _httpx.post(url, **kwargs)
    client = _get_http_client()
    if client is not None:
        return client.post(url, **kwargs)
    return _httpx.post(url, **kwargs)


def _http_get(url: str, **kwargs):
    if hasattr(_httpx.get, "return_value") or hasattr(_httpx.get, "side_effect"):
        return _httpx.get(url, **kwargs)
    client = _get_http_client()
    if client is not None:
        return client.get(url, **kwargs)
    return _httpx.get(url, **kwargs)


_url_cache: dict[str, tuple[float, dict]] = {}
_CACHE_TTL = 300.0  # 5 minutes


def _get_cached_url(url: str) -> dict | None:
    if url in _url_cache:
        ts, val = _url_cache[url]
        if _time.time() - ts < _CACHE_TTL:
            return val
        del _url_cache[url]
    return None


def _set_cached_url(url: str, val: dict) -> None:
    if len(_url_cache) > 500:
        oldest = min(_url_cache.keys(), key=lambda k: _url_cache[k][0])
        del _url_cache[oldest]
    _url_cache[url] = (_time.time(), val)


# Precompiled module-level regexes for speed
_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_DOMAIN_RE = re.compile(r"\b(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s]*)?", re.IGNORECASE)
_PHONE_RE = re.compile(r"(?:\+?\d[\d\s\-]{7,}\d)")
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_URL_OR_DOMAIN_RE = re.compile(r"https?://[^\s<>\"']+|(?:\b[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s]*)?", re.IGNORECASE)


class KeywordHit(TypedDict):
    term: str
    risk: str
    reason: str


class ScoreContribution(TypedDict):
    label: str
    points: int
    icon: str
    detail: str


class ThreatBreakdown(TypedDict):
    links: list[str]
    urls: list[str]
    phones: list[str]
    emails: list[str]
    suspicious_domains: list[str]
    money_requests: list[str]
    urgency: list[str]
    social_engineering: list[str]


class ScanRecord(TypedDict):
    id: str
    user_id: str
    timestamp: str
    input_text: str
    input_type: str
    risk_score: int
    confidence: int
    verdict: str
    summary: str
    explanation: str
    categories: list[str]
    red_flags: list[str]
    actions: list[str]
    checklist: list[str]
    keywords: list[KeywordHit]
    entities: list[str]
    threat_breakdown: ThreatBreakdown
    contributions: list[ScoreContribution]


SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "buff.ly",
    "is.gd", "rebrand.ly", "cutt.ly", "rb.gy", "shorturl.at", "bit.do",
    "tiny.cc", "lnkd.in", "soo.gd", "s.id", "t.ly",
}

SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".click", ".loan", ".work", ".support", ".country",
    ".gq", ".tk", ".ml", ".cf", ".ga", ".info", ".zip", ".mov", ".cc",
}

TRUSTED_DOMAINS = {
    "google.com", "youtube.com", "facebook.com", "instagram.com",
    "amazon.in", "amazon.com", "flipkart.com", "icicibank.com",
    "hdfcbank.com", "sbi.co.in", "axisbank.com", "kotak.com",
    "rbi.org.in", "cybercrime.gov.in", "paytm.com", "phonepe.com",
    "gpay.com", "npci.org.in", "irctc.co.in", "aadhaar.uidai.gov.in",
    "uidai.gov.in", "incometax.gov.in", "epfindia.gov.in",
    "policypedia.gov.in", "sancharsaathi.gov.in",
}

IMPERSONATION_BRANDS = [
    "rbi", "sbi", "hdfc", "icici", "axis", "kotak", "yes bank",
    "paytm", "phonepe", "google pay", "gpay", "amazon", "flipkart",
    "npci", "irctc", "uidai", "aadhaar", "cbi", "tax department",
    "income tax", "police", "court", "kyc", "bank of india", "pnb",
    "canara bank", "union bank", "boi", "indian post", "courier",
    "microsoft", "apple", "whatsapp", "telegram",
]

# ─── Context-aware credential analysis ────────────────────────────────────────

# Patterns that indicate the MESSAGE IS SENDING an OTP (safe notification)
OTP_NOTIFICATION_PATTERNS = [
    r"\botp\s+(?:is|:)\s*\d{4,8}\b",          # "OTP is 384827"
    r"\bone.?time\s+password\s+(?:is|:)",       # "one-time password is"
    r"\bverification\s+code\s+(?:is|:)",        # "verification code is"
    r"\bdo\s+not\s+share\b",                   # "do not share"
    r"\bnever\s+share\b",                       # "never share"
    r"\bdo\s+not\s+disclose\b",
    r"\bvalid\s+for\s+\d+\s+(?:min|second)",   # "valid for 5 min"
    r"\bexpires?\s+in\s+\d+",                  # "expires in 10"
    r"\btransaction\s+(?:id|ref|no)\b",        # "transaction id"
    r"\bstatement\s+(?:is\s+)?ready\b",        # "statement is ready"
    r"\border\s+(?:has\s+)?(?:shipped|placed|confirmed|delivered)\b",
    r"\bpayment\s+(?:of|for|received|confirmed|successful)\b",
    r"\bthank\s+you\s+for\s+(?:your\s+)?(?:purchase|order|payment)\b",
]

# Patterns that indicate REQUESTING credentials or suspicious actions (scam)
CREDENTIAL_REQUEST_PATTERNS = [
    r"\b(?:send|share|provide|give|reply\s+with|enter|submit|tell)\s+(?:your\s+)?(?:otp|pin|cvv|password|card\s+number|account\s+number)\b",
    r"\bverify\s+(?:your\s+)?(?:otp|pin|account|card)\b",
    r"\bclick\s+(?:here|the\s+link|this\s+link)\s+(?:to\s+)?(?:verify|update|confirm|claim|cancel|refund|reverse|block)\b",
    r"\b(?:claim|get)\s+(?:your\s+)?(?:prize|reward|cash|refund|cashback|bonus|commission)\b",
    r"\b(?:claim|get)\b.*(?:\d+|rs\.?|₹)?.*\b(?:bonus|reward|cash|prize|refund|cashback|gift|commission)\b",
    r"\bupdate\s+(?:your\s+)?kyc\b",
    r"\bkyc\s+(?:expired|update|verification)\b",
    r"\baccount\s+(?:will\s+be\s+)?(?:blocked|suspended|closed|terminated)\b",
    r"\bwon\b.*\b(?:prize|lottery|reward|cash|iphone|gift)\b",
    r"\binstall\s+(?:the\s+)?(?:app|apk)\b",
    r"\bdownload\s+(?:this\s+)?(?:app|apk|file)\b",
    r"\bapprove\s+(?:the\s+)?(?:payment|request|transaction)\b",
    r"\b(?:refund|cancel|reverse)\s+(?:link|request|transaction)\b",
    # Task / Job scams
    r"\bpart[\s-]time\b.*\b(?:job|work|opportunity|income|earn)\b",
    r"\bwork\s+from\s+home\b.*\b(?:daily|earn|income|payout|opportunity)\b",
    r"\b(?:like|liking|watch|watching)\s+(?:youtube|videos|reels|tiktok)\b",
    r"\b(?:rate|rating|review|reviewing)\s+(?:hotels|maps|google|apps)\b",
    # Utility disconnection threats
    r"\b(?:electricity|power|light)\b.*\b(?:disconnect|disconnection|cut\s*off)\b",
    # Digital arrest / extortion
    r"\b(?:parcel|courier|package)\b.*\b(?:illegal|drugs|narcotics|customs|seized|intercepted)\b",
    r"\b(?:digital\s+arrest|arrest\s+warrant|face\s+arrest|jailed)\b",
]


def _is_credential_request(text: str) -> bool:
    """Returns True if the text is requesting credentials or sensitive action."""
    t = text.lower()
    return any(re.search(p, t, re.IGNORECASE) for p in CREDENTIAL_REQUEST_PATTERNS)


# ─── URL analysis ─────────────────────────────────────────────────────────────

def analyze_url(url: str) -> dict:
    info = {
        "scheme": "", "domain": "", "path": "",
        "is_shortener": False, "is_https": False, "is_ip": False,
        "suspicious_params": [], "phishing_indicators": [],
        "tld_suspicious": False, "trusted": False,
    }
    raw = (url or "").strip()
    if not raw:
        return info
    if not raw.startswith(("http://", "https://", "upi://")):
        raw = "http://" + raw
    try:
        parsed = urlparse(raw)
    except Exception:
        return info
    info["scheme"] = parsed.scheme
    info["is_https"] = parsed.scheme == "https"
    domain = (parsed.netloc or "").lower().split(":")[0]
    info["domain"] = domain
    info["path"] = parsed.path or ""

    if domain in SHORTENER_DOMAINS:
        info["is_shortener"] = True
        info["phishing_indicators"].append(
            f"Uses link shortener '{domain}' which hides the real destination."
        )
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain):
        info["is_ip"] = True
        info["phishing_indicators"].append(
            "URL uses a raw IP address — legitimate banks never do this."
        )
    for tld in SUSPICIOUS_TLDS:
        if domain.endswith(tld):
            info["tld_suspicious"] = True
            info["phishing_indicators"].append(
                f"Uses suspicious TLD '{tld}' commonly abused for fraud."
            )
            break
    if any(domain == td or domain.endswith("." + td) for td in TRUSTED_DOMAINS):
        info["trusted"] = True
    for brand in ["sbi", "hdfc", "icici", "paytm", "phonepe", "amazon", "flipkart"]:
        if brand in domain and not info["trusted"]:
            info["phishing_indicators"].append(
                f"Domain contains '{brand}' but is not the official domain — likely typosquat."
            )
            break
    if domain.count("-") >= 3:
        info["phishing_indicators"].append(
            "Domain has many hyphens — common in phishing URLs."
        )
    if len(domain) > 40:
        info["phishing_indicators"].append(
            "Unusually long domain — common in phishing."
        )
    suspicious_params = {
        "otp", "pin", "cvv", "password", "token", "auth",
        "session", "kyc", "verify", "redirect", "url", "next",
    }
    try:
        qs = parse_qs(parsed.query or "")
        for k in qs.keys():
            if k.lower() in suspicious_params:
                info["suspicious_params"].append(k)
    except Exception:
        pass
    if info["suspicious_params"]:
        info["phishing_indicators"].append(
            "URL contains sensitive parameters: " + ", ".join(info["suspicious_params"])
        )
    if info["scheme"] == "http" and not info["is_ip"]:
        info["phishing_indicators"].append(
            "URL is not HTTPS — sensitive sites must use HTTPS."
        )
    return info


def analyze_phone(phone: str) -> dict:
    info = {"is_valid": False, "digits": "", "country": "", "indicators": []}
    raw = (phone or "").strip()
    digits = re.sub(r"\D", "", raw)
    info["digits"] = digits
    if len(digits) < 7:
        info["indicators"].append("Phone number too short.")
        return info
    info["is_valid"] = True
    if digits.startswith("91") and len(digits) >= 12:
        info["country"] = "India"
        local = digits[-10:]
        if not local[0] in "6789":
            info["indicators"].append("Indian number does not start with valid mobile prefix.")
    elif len(digits) == 10 and digits[0] in "6789":
        info["country"] = "India (mobile)"
    elif digits.startswith("1") and len(digits) == 11:
        info["country"] = "USA/Canada"
        info["indicators"].append("International number — verify carefully.")
    elif len(digits) > 13:
        info["indicators"].append("Unusually long number — may be spoofed VoIP.")
    if raw.startswith("+") and not raw.startswith("+91"):
        info["indicators"].append("International caller — common in scam patterns.")
    return info


def _has_suspicious_url_or_threat(text: str) -> bool:
    """Returns True if the text contains an untrusted link, IP address, shortener, or suspicious domain."""
    urls = _URL_OR_DOMAIN_RE.findall(text)
    for u in urls:
        info = analyze_url(u)
        if not info.get("domain"):
            continue
        if info.get("is_shortener") or info.get("is_ip") or info.get("tld_suspicious") or not info.get("trusted"):
            return True
    return False


def _is_safe_notification(text: str) -> bool:
    """Returns True if the text looks like a legitimate notification.

    A message cannot be a safe notification if it contains untrusted links,
    requests credentials, or contains suspicious threats.
    """
    if _has_suspicious_url_or_threat(text):
        return False
    t = text.lower()
    safe_hits = sum(
        1 for p in OTP_NOTIFICATION_PATTERNS if re.search(p, t, re.IGNORECASE)
    )
    scam_hits = sum(
        1 for p in CREDENTIAL_REQUEST_PATTERNS if re.search(p, t, re.IGNORECASE)
    )
    return safe_hits > 0 and scam_hits == 0


# ─── External API cross-verification ──────────────────────────────────────────

def _check_google_safe_browsing(url: str) -> dict:
    """Check URL against Google's phishing/malware database (free: 10K/day)."""
    api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
    if not api_key:
        return {"checked": False, "status": "NOT_CONFIGURED", "source": "Google Safe Browsing", "error": "API key not configured"}
    if _httpx is None:
        return {"checked": False, "status": "UNAVAILABLE", "source": "Google Safe Browsing", "error": "httpx not installed"}
    try:
        resp = _http_post(
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}",
            json={
                "client": {"clientId": "fraudradar", "clientVersion": "2.0"},
                "threatInfo": {
                    "threatTypes": [
                        "MALWARE", "SOCIAL_ENGINEERING",
                        "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION",
                    ],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url}],
                },
            },
            timeout=4.0,
        )
        if resp.status_code == 429:
            return {"checked": False, "status": "RATE_LIMITED", "source": "Google Safe Browsing", "error": "Quota exceeded / rate limited"}
        if resp.status_code in (400, 403):
            return {"checked": False, "status": "ERROR", "source": "Google Safe Browsing", "error": "Invalid API key or unauthorized"}
        if resp.status_code >= 500:
            return {"checked": False, "status": "ERROR", "source": "Google Safe Browsing", "error": "Service unavailable"}
        if resp.status_code != 200:
            return {"checked": False, "status": "ERROR", "source": "Google Safe Browsing", "error": f"HTTP {resp.status_code}"}

        data = resp.json()
        if not isinstance(data, dict):
            return {"checked": False, "status": "ERROR", "source": "Google Safe Browsing", "error": "Malformed JSON response"}

        matches = data.get("matches", [])
        is_dangerous = len(matches) > 0
        return {
            "checked": True,
            "status": "MALICIOUS" if is_dangerous else "SAFE",
            "is_dangerous": is_dangerous,
            "threats": [m.get("threatType") for m in matches if isinstance(m, dict)],
            "source": "Google Safe Browsing",
        }
    except _httpx.TimeoutException:
        return {"checked": False, "status": "TIMEOUT", "source": "Google Safe Browsing", "error": "Request timed out"}
    except Exception as e:
        logging.warning(f"Google Safe Browsing check failed: {e}")
        return {"checked": False, "status": "ERROR", "source": "Google Safe Browsing", "error": str(e)}


def _check_virustotal(url: str) -> dict:
    """Scan URL against 70+ security engines via VirusTotal (free: 500/day)."""
    api_key = os.getenv("VIRUSTOTAL_API_KEY")
    if not api_key:
        return {"checked": False, "status": "NOT_CONFIGURED", "source": "VirusTotal", "error": "API key not configured"}
    if _httpx is None:
        return {"checked": False, "status": "UNAVAILABLE", "source": "VirusTotal", "error": "httpx not installed"}
    try:
        headers = {"x-apikey": api_key}
        url_id = _base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        resp = _http_get(
            f"https://www.virustotal.com/api/v3/urls/{url_id}",
            headers=headers,
            timeout=4.0,
        )
        if resp.status_code == 429:
            return {"checked": False, "status": "RATE_LIMITED", "source": "VirusTotal", "error": "Quota exceeded / rate limited"}
        if resp.status_code in (401, 403):
            return {"checked": False, "status": "ERROR", "source": "VirusTotal", "error": "Invalid API key or unauthorized"}
        if resp.status_code >= 500:
            return {"checked": False, "status": "ERROR", "source": "VirusTotal", "error": "Service unavailable"}
        if resp.status_code == 404:
            return {
                "checked": False,
                "status": "NOT_FOUND",
                "source": "VirusTotal",
                "detail": "URL not indexed in VirusTotal database",
            }
        if resp.status_code != 200:
            return {"checked": False, "status": "ERROR", "source": "VirusTotal", "error": f"HTTP {resp.status_code}"}

        data = resp.json()
        if not isinstance(data, dict):
            return {"checked": False, "status": "ERROR", "source": "VirusTotal", "error": "Malformed JSON response"}

        stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
        malicious = int(stats.get("malicious", 0))
        suspicious = int(stats.get("suspicious", 0))
        total = sum(int(v) for v in stats.values()) if stats else 0
        is_dangerous = (malicious >= 2) or (malicious >= 1 and suspicious >= 1)

        return {
            "checked": True,
            "status": "MALICIOUS" if is_dangerous else "SAFE",
            "is_dangerous": is_dangerous,
            "malicious_count": malicious,
            "suspicious_count": suspicious,
            "total_engines": total,
            "source": "VirusTotal",
        }
    except _httpx.TimeoutException:
        return {"checked": False, "status": "TIMEOUT", "source": "VirusTotal", "error": "Request timed out"}
    except Exception as e:
        logging.warning(f"VirusTotal check failed: {e}")
        return {"checked": False, "status": "ERROR", "source": "VirusTotal", "error": str(e)}


def _check_phishtank(url: str) -> dict:
    """Check if URL is a known phish in the PhishTank database (free: unlimited)."""
    api_key = os.getenv("PHISHTANK_API_KEY")
    if not api_key:
        return {"checked": False, "status": "NOT_CONFIGURED", "source": "PhishTank", "error": "API key not configured"}
    if _httpx is None:
        return {"checked": False, "status": "UNAVAILABLE", "source": "PhishTank", "error": "httpx not installed"}
    try:
        resp = _http_post(
            "https://checkurl.phishtank.com/checkurl/",
            data={"url": url, "format": "json", "app_key": api_key},
            timeout=4.0,
        )
        if resp.status_code == 429:
            return {"checked": False, "status": "RATE_LIMITED", "source": "PhishTank", "error": "Rate limit exceeded"}
        if resp.status_code in (401, 403):
            return {"checked": False, "status": "ERROR", "source": "PhishTank", "error": "Invalid API key or unauthorized"}
        if resp.status_code != 200:
            return {"checked": False, "status": "ERROR", "source": "PhishTank", "error": f"HTTP {resp.status_code}"}

        data = resp.json().get("results", {})
        in_database = data.get("in_database", False)
        valid = data.get("valid", False)
        is_phishing = bool(in_database and valid)
        return {
            "checked": True,
            "status": "MALICIOUS" if is_phishing else "SAFE",
            "is_dangerous": is_phishing,
            "is_phishing": is_phishing,
            "verified": data.get("verified", False),
            "source": "PhishTank",
        }
    except _httpx.TimeoutException:
        return {"checked": False, "status": "TIMEOUT", "source": "PhishTank", "error": "Request timed out"}
    except Exception as e:
        logging.warning(f"PhishTank check failed: {e}")
        return {"checked": False, "status": "ERROR", "source": "PhishTank", "error": str(e)}


def _check_single_url_external(url: str) -> dict:
    """Check one URL against all 3 external engines concurrently with caching."""
    cached = _get_cached_url(url)
    if cached is not None:
        return cached

    with ThreadPoolExecutor(max_workers=3) as pool:
        f_gsb = pool.submit(_check_google_safe_browsing, url)
        f_vt = pool.submit(_check_virustotal, url)
        f_pt = pool.submit(_check_phishtank, url)

        gsb = f_gsb.result()
        vt = f_vt.result()
        pt = f_pt.result()

    checks = {"google_safe_browsing": gsb, "virustotal": vt, "phishtank": pt}
    flagged_by: list[str] = []
    safe_by: list[str] = []
    unavailable_by: list[str] = []

    for k, chk in checks.items():
        st = chk.get("status")
        src = chk.get("source", k)
        if st == "MALICIOUS":
            flagged_by.append(src)
        elif st == "SAFE":
            safe_by.append(src)
        elif st in ("ERROR", "TIMEOUT", "RATE_LIMITED", "UNAVAILABLE"):
            unavailable_by.append(src)

    res = {
        "url": url,
        "google_safe_browsing": gsb,
        "virustotal": vt,
        "phishtank": pt,
        "flagged_by": flagged_by,
        "safe_by": safe_by,
        "unavailable_by": unavailable_by,
        "is_flagged": len(flagged_by) > 0,
        "is_safe": len(safe_by) > 0 and len(flagged_by) == 0,
        "is_unavailable": len(unavailable_by) > 0 and len(flagged_by) == 0 and len(safe_by) == 0,
    }
    _set_cached_url(url, res)
    return res


def check_urls_external(urls: list[str]) -> list[dict]:
    """Run external API checks on URLs concurrently across worker threads."""
    target_urls = urls[:3]
    if not target_urls:
        return []
    if len(target_urls) == 1:
        return [_check_single_url_external(target_urls[0])]

    with ThreadPoolExecutor(max_workers=min(len(target_urls), 3)) as pool:
        return list(pool.map(_check_single_url_external, target_urls))


# ─── System prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are FraudRadar, an expert AI fraud analyst specializing in Indian cyber fraud (UPI fraud, KYC scams, OTP fraud, fake jobs, courier scams, investment scams, phishing, etc.).

CRITICAL CONTEXT RULES — you must follow these exactly:

1. OTP NOTIFICATIONS ARE SAFE:
   - "Your OTP is 384827. Do not share it." → SAFE (risk 5-15)
   - "Your Amazon OTP is 123456." → SAFE
   - "Transaction ID: 9876. Your payment was successful." → SAFE
   - "Your order has been shipped." → SAFE
   - "Your SBI account statement is ready." → SAFE
   These are LEGITIMATE system messages. Do NOT flag them as scams.

2. CREDENTIAL REQUESTS ARE HIGH RISK:
   - "Send us your OTP" → HIGH (risk 80+)
   - "Share your PIN to verify" → HIGH
   - "Click here to update KYC" → HIGH
   - "Your account will be blocked, verify now" → HIGH
   - "Reply with OTP" → HIGH

3. URGENCY ALONE IS NOT ENOUGH — combine with other factors.
   A bank transaction alert with urgency language may still be SAFE.

4. CONTEXT MATTERS MORE THAN KEYWORDS.
   Do not flag words like "OTP", "bank", "verify" in isolation.
   Look at the full intent of the message.

Analyze the content and return STRICTLY VALID JSON only (no markdown, no commentary):
{
  "risk_score": <integer 0-100>,
  "confidence": <integer 0-100>,
  "verdict": "<SAFE|MEDIUM|HIGH>",
  "summary": "<one concise sentence>",
  "explanation": "<2-4 sentences of detailed analysis>",
  "categories": ["<e.g. OTP Scam, Phishing, KYC Scam, UPI Fraud, Job Scam, Investment Scam, Courier Scam, Lottery Scam, Banking Scam, Safe Notification, General>"],
  "red_flags": ["<specific red flag>"],
  "actions": ["<recommended action>"],
  "checklist": ["<safety checklist item>"],
  "keywords": [{"term": "<exact phrase>", "risk": "high|medium|low", "reason": "<why>"}],
  "entities": ["<phone numbers, URLs, brand names>"],
  "threat_breakdown": {
    "links": ["<full URLs>"],
    "urls": ["<bare domains>"],
    "phones": ["<phone numbers>"],
    "emails": ["<email addresses>"],
    "suspicious_domains": ["<typosquats/shorteners>"],
    "money_requests": ["<payment-related phrases>"],
    "urgency": ["<urgency phrases>"],
    "social_engineering": ["<authority/fear/reward triggers>"]
  }
}

Verdict rules: SAFE = 0-39, MEDIUM = 40-69, HIGH = 70-100.
Return ONLY JSON."""


def _normalize_verdict(verdict: str, score: int) -> str:
    """Normalize and enforce strict score-verdict consistency.

    SAFE = 0-39, MEDIUM = 40-69, HIGH = 70-100.
    """
    v = (verdict or "").strip().upper()
    if v in ("CONFIRMED SCAM", "LIKELY SCAM", "SCAM"):
        v = "HIGH"
    elif v in ("SUSPICIOUS",):
        v = "MEDIUM"
    elif v not in ("HIGH", "MEDIUM", "SAFE"):
        v = "HIGH" if score >= 70 else ("MEDIUM" if score >= 40 else "SAFE")

    # Score-verdict consistency rules
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "HIGH" if v == "HIGH" else "MEDIUM"
    else:
        return "MEDIUM" if v == "MEDIUM" else "SAFE"


EMPTY_BREAKDOWN: ThreatBreakdown = {
    "links": [], "urls": [], "phones": [], "emails": [],
    "suspicious_domains": [], "money_requests": [], "urgency": [],
    "social_engineering": [],
}


class ScanState(rx.State):
    input_text: str = ""
    input_type: str = "text"
    is_analyzing: bool = False
    error: str = ""

    risk_score: int = 0
    confidence: int = 0
    verdict: str = ""
    summary: str = ""
    explanation: str = ""
    categories: list[str] = []
    red_flags: list[str] = []
    actions: list[str] = []
    checklist: list[str] = []
    keywords: list[KeywordHit] = []
    entities: list[str] = []
    threat_breakdown: ThreatBreakdown = {
        "links": [], "urls": [], "phones": [], "emails": [],
        "suspicious_domains": [], "money_requests": [], "urgency": [],
        "social_engineering": [],
    }
    contributions: list[ScoreContribution] = []
    has_result: bool = False

    history: list[ScanRecord] = []
    search_query: str = ""
    filter_verdict: str = "All"
    sort_by: str = "newest"

    @rx.event
    def set_input_text(self, v: str):
        self.input_text = v

    @rx.event
    def set_input_type(self, v: str):
        self.input_type = v

    @rx.event
    def set_search(self, v: str):
        self.search_query = v

    @rx.event
    def set_filter_verdict(self, v: str):
        self.filter_verdict = v

    @rx.event
    def set_sort_by(self, v: str):
        self.sort_by = v

    @rx.event
    def delete_record(self, record_id: str):
        self.history = [h for h in self.history if h["id"] != record_id]

    @rx.event
    def clear_history(self):
        self.history = []

    @rx.event
    def clear_result(self):
        self.has_result = False
        self.input_text = ""
        self.error = ""

    @rx.event
    def export_csv(self):
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            "Timestamp", "Type", "Verdict", "Risk", "Confidence",
            "Categories", "Summary", "Input",
        ])
        for h in self.filtered_history:
            writer.writerow([
                h["timestamp"], h["input_type"], h["verdict"],
                h["risk_score"], h.get("confidence", 0),
                "; ".join(h.get("categories", [])),
                h.get("summary", ""), h["input_text"],
            ])
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return rx.download(data=buf.getvalue(), filename=f"fraudradar_history_{ts}.csv")

    @rx.event
    def export_report(self, record_id: str):
        rec = next((h for h in self.history if h["id"] == record_id), None)
        if not rec:
            return
        sep = "=" * 64
        thin = "-" * 64
        tb = rec.get("threat_breakdown", {}) or {}

        def section(title):
            return ["", title.upper(), thin]

        def list_or_none(items, prefix="  • "):
            if not items:
                return ["  (none detected)"]
            return [f"{prefix}{x}" for x in items]

        lines = [
            sep, "  F R A U D R A D A R   ·   S C A N   R E P O R T",
            "  AI-Powered Scam Defense for India", sep, "",
            f"  Report ID    : {rec['id']}",
            f"  Generated    : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Scan Time    : {rec['timestamp']}",
            f"  Input Type   : {rec['input_type'].upper()}", "",
            sep, "  RISK ASSESSMENT", sep,
            f"  Verdict      : {rec['verdict']}",
            f"  Risk Score   : {rec['risk_score']} / 100",
            f"  Confidence   : {rec.get('confidence', 0)}%",
            f"  Categories   : {', '.join(rec.get('categories', [])) or '—'}",
        ]
        lines += section("Analyzed Input")
        lines += [f"  {ln}" for ln in (rec.get("input_text", "") or "").splitlines() or [""]]
        lines += section("AI Summary")
        lines += [f"  {rec.get('summary', '') or '—'}"]
        lines += section("Detailed Explanation")
        for chunk in (rec.get("explanation", "") or "—").split("\n"):
            lines.append(f"  {chunk}")
        lines += section("Red Flags")
        lines += list_or_none(rec.get("red_flags", []))
        lines += section("Recommended Actions")
        lines += list_or_none(rec.get("actions", []))
        lines += [
            "", sep,
            "  EMERGENCY: Call 1930 · cybercrime.gov.in",
            sep,
        ]
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return rx.download(
            data="\n".join(lines),
            filename=f"fraudradar_report_{rec['id']}_{ts}.txt",
        )

    @rx.var
    def filtered_history(self) -> list[ScanRecord]:
        items = list(self.history)
        if self.filter_verdict != "All":
            items = [i for i in items if i["verdict"] == self.filter_verdict]
        if self.search_query:
            q = self.search_query.lower()
            items = [
                i for i in items
                if q in i["input_text"].lower()
                or q in i["verdict"].lower()
                or q in i.get("summary", "").lower()
                or any(q in c.lower() for c in i.get("categories", []))
            ]
        if self.sort_by == "risk_desc":
            items.sort(key=lambda x: x["risk_score"], reverse=True)
        elif self.sort_by == "risk_asc":
            items.sort(key=lambda x: x["risk_score"])
        elif self.sort_by == "oldest":
            items = list(reversed(items))
        return items

    @rx.var
    def total_scans(self) -> int:
        return len(self.history)

    @rx.var
    def scams_detected(self) -> int:
        return len([h for h in self.history if h["verdict"] == "HIGH"])

    @rx.var
    def avg_risk(self) -> float:
        if not self.history:
            return 0.0
        return sum(h["risk_score"] for h in self.history) / len(self.history)

    @rx.var
    def latest_verdict(self) -> str:
        if self.history:
            return self.history[0]["verdict"]
        return "—"

    @rx.event
    async def analyze(self, text: str = "", input_type: str = ""):
        analysis_text = text if text else self.input_text
        analysis_type = input_type if input_type else self.input_type

        if not analysis_text.strip():
            self.error = "Please enter content to analyze."
            return
        if len(analysis_text) > 5000:
            self.error = "Input too long (max 5000 chars)."
            return

        self.is_analyzing = True
        self.error = ""
        self.has_result = False
        self.input_text = analysis_text
        self.input_type = analysis_type

        # Pre-extract candidate URLs immediately for concurrent checking
        extracted = self._extract_threats(analysis_text)
        all_urls_for_check = list(dict.fromkeys(
            extracted.get("links", []) + extracted.get("urls", [])
        ))
        if analysis_type == "url" and analysis_text.strip():
            raw_url = analysis_text.strip()
            if not raw_url.startswith(("http://", "https://")):
                raw_url = "http://" + raw_url
            if raw_url not in all_urls_for_check:
                all_urls_for_check.insert(0, raw_url)

        any_api_configured = any(
            os.getenv(k)
            for k in ("GOOGLE_SAFE_BROWSING_API_KEY", "VIRUSTOTAL_API_KEY", "PHISHTANK_API_KEY")
        )

        # ── Parallel Execution: Groq LLM + External API checks ────────
        try:
            if all_urls_for_check and any_api_configured:
                llm_task = asyncio.to_thread(self._analyze_sync, analysis_text, analysis_type)
                ext_task = asyncio.to_thread(check_urls_external, all_urls_for_check)
                result, ext_results = await asyncio.gather(llm_task, ext_task)
            else:
                result = await asyncio.to_thread(self._analyze_sync, analysis_text, analysis_type)
                ext_results = []
        except Exception as e:
            logging.exception(f"Analyze unexpected: {e}")
            result = self._heuristic_fallback(analysis_text)
            ext_results = []

        try:
            self.risk_score = max(0, min(100, int(result.get("risk_score", 0))))
        except Exception:
            self.risk_score = 0
        try:
            self.confidence = max(0, min(100, int(result.get("confidence", 80))))
        except Exception:
            self.confidence = 80

        self.verdict = _normalize_verdict(result.get("verdict", ""), self.risk_score)
        self.summary = (result.get("summary") or "").strip() or f"{self.verdict} risk detected."
        self.explanation = result.get("explanation") or "Analysis completed."

        def _str_list(v) -> list[str]:
            if isinstance(v, list):
                return [str(x) for x in v if x is not None]
            return []

        self.categories = _str_list(result.get("categories"))
        self.red_flags = _str_list(result.get("red_flags"))
        self.actions = _str_list(result.get("actions"))
        self.checklist = _str_list(result.get("checklist")) or [
            "Do not share OTP, PIN, or CVV with anyone",
            "Verify the sender through official channels",
            "Avoid clicking unknown links",
            "Report to 1930 if you suspect fraud",
        ]
        self.entities = _str_list(result.get("entities"))

        kws_raw = result.get("keywords") or []
        kws: list[KeywordHit] = []
        if isinstance(kws_raw, list):
            for k in kws_raw:
                if isinstance(k, dict) and k.get("term"):
                    kws.append({
                        "term": str(k.get("term", "")),
                        "risk": str(k.get("risk", "medium")).lower(),
                        "reason": str(k.get("reason", "")),
                    })
                elif isinstance(k, str):
                    kws.append({"term": k, "risk": "medium", "reason": ""})
        self.keywords = kws

        tb_raw = result.get("threat_breakdown") or {}
        if not isinstance(tb_raw, dict):
            tb_raw = {}
        breakdown: ThreatBreakdown = {
            "links": _str_list(tb_raw.get("links")),
            "urls": _str_list(tb_raw.get("urls")),
            "phones": _str_list(tb_raw.get("phones")),
            "emails": _str_list(tb_raw.get("emails")),
            "suspicious_domains": _str_list(tb_raw.get("suspicious_domains")),
            "money_requests": _str_list(tb_raw.get("money_requests")),
            "urgency": _str_list(tb_raw.get("urgency")),
            "social_engineering": _str_list(tb_raw.get("social_engineering")),
        }
        for key in ("links", "urls", "phones", "emails"):
            for v in extracted[key]:
                if v not in breakdown[key]:
                    breakdown[key].append(v)
        self.threat_breakdown = breakdown
        self.contributions = self._build_contributions(
            analysis_text, breakdown, self.keywords, analysis_type
        )

        # ── Apply external API cross-verification results ────────────
        for ext in ext_results:
            if ext.get("is_flagged"):
                flagged_apis = ", ".join(ext["flagged_by"])
                self.risk_score = max(self.risk_score, 85)
                self.verdict = "HIGH"
                self.confidence = max(self.confidence, 92)
                self.contributions.append({
                    "label": f"Flagged by {flagged_apis}",
                    "points": 40,
                    "icon": "shield-x",
                    "detail": (
                        f"URL '{ext['url']}' was confirmed dangerous by: "
                        f"{flagged_apis}. This is a verified threat."
                    ),
                })
                flag_msg = f"Confirmed threat: {ext['url']} (flagged by {flagged_apis})"
                if flag_msg not in self.red_flags:
                    self.red_flags.append(flag_msg)
            elif ext.get("is_safe"):
                url_info = analyze_url(ext["url"])
                if not url_info.get("tld_suspicious") and not url_info.get("is_shortener") and not url_info.get("is_ip"):
                    checked_apis = ", ".join(ext.get("safe_by", []))
                    self.contributions.append({
                        "label": "External APIs: Clear",
                        "points": -10,
                        "icon": "shield-check",
                        "detail": (
                            f"URL '{ext['url']}' was verified clean by: {checked_apis}."
                        ),
                    })
            elif ext.get("is_unavailable"):
                unavail_apis = ", ".join(ext.get("unavailable_by", []))
                self.contributions.append({
                    "label": "External Verification Unavailable",
                    "points": 0,
                    "icon": "shield-alert",
                    "detail": (
                        f"External threat intelligence check unavailable for '{ext['url']}' "
                        f"({unavail_apis}). Scored using internal rules."
                    ),
                })

        # Final consistency enforcement
        self.verdict = _normalize_verdict(self.verdict, self.risk_score)

        self.has_result = True
        self.is_analyzing = False

        user_id = ""
        try:
            from fraudradar_ai_scam_detection_v2.states.auth_state import AuthState
            auth = await self.get_state(AuthState)
            user_id = auth.user_id or ""
        except Exception:
            logging.debug("auth lookup not available in current context")

        record: ScanRecord = {
            "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "user_id": user_id,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "input_text": analysis_text[:500],
            "input_type": analysis_type,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "verdict": self.verdict,
            "summary": self.summary,
            "explanation": self.explanation,
            "categories": self.categories,
            "red_flags": self.red_flags,
            "actions": self.actions,
            "checklist": self.checklist,
            "keywords": self.keywords,
            "entities": self.entities,
            "threat_breakdown": self.threat_breakdown,
            "contributions": self.contributions,
        }
        self.history.insert(0, record)

        # Background async persistence to Supabase
        try:
            asyncio.create_task(asyncio.to_thread(self._persist_to_supabase, record))
        except Exception as e:
            logging.debug(f"Async persistence dispatch skipped: {e}")

    def _build_contributions(
        self,
        text: str,
        breakdown: ThreatBreakdown,
        keywords: list[KeywordHit],
        input_type: str,
    ) -> list[ScoreContribution]:
        contribs: list[ScoreContribution] = []
        t = (text or "").lower()

        # Context-aware credential check — only flag if REQUESTING, not notifying
        if _is_credential_request(text):
            contribs.append({
                "label": "Credential Request Detected",
                "points": 30,
                "icon": "key-round",
                "detail": "This message asks you to share or submit sensitive credentials. Legitimate services never request OTP, PIN, or passwords.",
            })
        elif _is_safe_notification(text):
            # Safe notification — do not add any credential-related penalty
            pass

        # Task / Job scam check
        has_job_lure = (
            bool(re.search(r"\b(?:part[\s-]time|work\s+from\s+home)\b", t)) and (
                bool(re.search(r"\b(?:job|work|opportunity|income|earn|payout)\b", t))
                or bool(re.search(r"\b(?:like|liking|watch|watching|rate|rating|review|reviewing)\b", t))
            )
            or bool(re.search(r"\b(?:like|liking|watch|watching)\s+(?:youtube|videos|reels|tiktok)\b", t))
            or bool(re.search(r"\b(?:rate|rating|review|reviewing)\s+(?:hotels|maps|google|apps)\b", t))
            or bool(re.search(r"\bearn\b.*(?:\d+|rs\.?|₹).*\b(?:daily|per\s+day|monthly|every\s+day)\b", t))
        )
        if has_job_lure:
            contribs.append({
                "label": "Task / Job Scam Lure",
                "points": 35,
                "icon": "briefcase",
                "detail": "Promotes high daily earnings for simple social media tasks (liking YouTube videos, rating Google Maps). A known task-fraud pattern.",
            })

        # Redirection to unverified messaging app for recruitment or verification
        has_msg_redirect = bool(re.search(r"\b(?:contact|whatsapp|message|join|dm|chat)\b.*\b(?:hr|manager|priya|neha|pooja|telegram|whatsapp)\b", t))
        if has_msg_redirect:
            contribs.append({
                "label": "Unofficial Messaging Redirection",
                "points": 25,
                "icon": "message-circle",
                "detail": "Directs recruitment or sensitive actions to personal WhatsApp or Telegram rather than official corporate portals.",
            })

        # Utility cutoff threat
        has_utility_threat = bool(re.search(r"\b(?:electricity|power|light)\b.*\b(?:disconnect|disconnection|cut\s*off)\b", t))
        if has_utility_threat:
            contribs.append({
                "label": "Utility Cutoff Threat",
                "points": 35,
                "icon": "zap-off",
                "detail": "Threatens immediate power/utility disconnection to induce panic and bypass critical thinking.",
            })

        # Digital arrest / legal coercion
        has_extortion = bool(re.search(r"\b(?:parcel|courier|package)\b.*\b(?:illegal|drugs|narcotics|customs|seized|intercepted)\b", t)) or bool(re.search(r"\b(?:digital\s+arrest|arrest\s+warrant|face\s+arrest)\b", t))
        if has_extortion:
            contribs.append({
                "label": "Digital Arrest / Legal Extortion",
                "points": 45,
                "icon": "shield-alert",
                "detail": "Impersonates law enforcement or customs with threats of arrest or narcotics interception to extort money.",
            })

        # Suspicious keywords from AI (only high-risk ones)
        high_kw = [k for k in keywords if k.get("risk") == "high"]
        if high_kw:
            contribs.append({
                "label": "Suspicious Wording",
                "points": min(20, 5 * len(high_kw)),
                "icon": "highlighter",
                "detail": "High-risk phrases: " + ", ".join([k["term"] for k in high_kw[:5]]),
            })

        # URL analysis
        all_urls = (breakdown.get("links") or []) + (breakdown.get("urls") or [])
        if all_urls:
            shortened, untrusted = [], []
            for u in all_urls:
                info = analyze_url(u)
                if info["is_shortener"]:
                    shortened.append(u)
                elif not info["trusted"]:
                    untrusted.append(u)
            if shortened:
                contribs.append({
                    "label": "Shortened Link",
                    "points": 20,
                    "icon": "link",
                    "detail": "Hides destination: " + ", ".join(shortened[:3]),
                })
            if untrusted:
                contribs.append({
                    "label": "Unknown/Untrusted Link",
                    "points": 15,
                    "icon": "globe",
                    "detail": "Links to unofficial domains: " + ", ".join(untrusted[:3]),
                })

        # Impersonation — only flag if combined with a request or suspicious link
        impersonation_hits = [b for b in IMPERSONATION_BRANDS if b in t]
        if impersonation_hits and (all_urls or _is_credential_request(text)):
            contribs.append({
                "label": "Brand Impersonation",
                "points": 15,
                "icon": "user-x",
                "detail": "Claims to be from " + ", ".join(impersonation_hits[:4]) + " but combined with suspicious content.",
            })

        # Financial requests — only flag if not a safe notification
        money = breakdown.get("money_requests") or []
        if money and not _is_safe_notification(text):
            contribs.append({
                "label": "Financial Request",
                "points": 15,
                "icon": "indian-rupee",
                "detail": "Requests money or payment action: " + ", ".join(money[:5]),
            })

        # Urgency — only flag if combined with other risks
        urgency = breakdown.get("urgency") or []
        if urgency and (all_urls or _is_credential_request(text) or money):
            contribs.append({
                "label": "Urgency Pressure",
                "points": 10,
                "icon": "clock",
                "detail": "Pressure tactics: " + ", ".join(urgency[:5]),
            })

        # URL deep analysis for URL input type
        if input_type == "url" and (text or "").strip():
            uinfo = analyze_url(text)
            if uinfo["phishing_indicators"]:
                contribs.append({
                    "label": "URL Structure Risk",
                    "points": 20,
                    "icon": "shield-alert",
                    "detail": " · ".join(uinfo["phishing_indicators"][:4]),
                })

        # Phone analysis
        phones = breakdown.get("phones") or []
        if input_type == "phone" or phones:
            for p in phones[:1]:
                pinfo = analyze_phone(p)
                if pinfo["indicators"]:
                    contribs.append({
                        "label": "Phone Number Risk",
                        "points": 10,
                        "icon": "phone",
                        "detail": " ".join(pinfo["indicators"]),
                    })

        return contribs

    def _extract_threats(self, text: str) -> dict[str, list[str]]:
        links = _URL_RE.findall(text)
        emails = _EMAIL_RE.findall(text)
        phones = [p.strip() for p in _PHONE_RE.findall(text) if len(re.sub(r"\D", "", p)) >= 8]
        bare = [d for d in _DOMAIN_RE.findall(text) if not d.startswith("http")]
        return {
            "links": list(dict.fromkeys(links)),
            "urls": list(dict.fromkeys(bare)),
            "phones": list(dict.fromkeys(phones))[:5],
            "emails": list(dict.fromkeys(emails)),
        }

    def _persist_to_supabase(self, record: ScanRecord) -> None:
        try:
            from fraudradar_ai_scam_detection_v2.states.auth_state import get_supabase
        except Exception:
            return
        sb = get_supabase()
        if sb is None:
            return
        full_payload = {
            "user_id": record.get("user_id") or None,
            "input_text": record["input_text"],
            "input_type": record["input_type"],
            "risk_score": record["risk_score"],
            "confidence": record.get("confidence", 0),
            "verdict": record["verdict"],
            "summary": record.get("summary", ""),
            "explanation": record["explanation"],
            "categories": record.get("categories", []),
            "red_flags": record.get("red_flags", []),
            "actions": record.get("actions", []),
            "checklist": record.get("checklist", []),
            "keywords": record.get("keywords", []),
            "entities": record.get("entities", []),
            "threat_breakdown": record.get("threat_breakdown", {}),
        }
        minimal_payload = {
            "input_text": record["input_text"],
            "input_type": record["input_type"],
            "risk_score": record["risk_score"],
            "verdict": record["verdict"],
            "explanation": record["explanation"],
        }
        try:
            sb.table("scan_history").insert(full_payload).execute()
        except Exception as e:
            msg = str(e)
            if "PGRST205" in msg or "Could not find the table" in msg:
                return
            try:
                sb.table("scan_history").insert(minimal_payload).execute()
            except Exception as e2:
                logging.exception(f"scan_history insert failed: {e2}")

    def _analyze_sync(self, text: str, input_type: str = "text") -> dict:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or Groq is None:
            return self._heuristic_fallback(text)

        # Pre-check: if clearly a safe notification with no suspicious URLs/threats, provide context hint
        if _is_safe_notification(text) and not _is_credential_request(text) and not _has_suspicious_url_or_threat(text):
            context_hint = "\n\nNOTE: This message appears to be a legitimate system notification (OTP delivery, order update, transaction confirmation). Analyze carefully with low bias toward false positives."
        else:
            context_hint = ""

        try:
            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Input type: {input_type}\n\nAnalyze this content:\n\n{text}{context_hint}",
                    },
                ],
                temperature=0.1,
                max_tokens=800,
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content or ""
            try:
                result = json.loads(content)
                # Post-processing safety net: only cap if genuine safe notification and NO suspicious URLs or requests
                if _is_safe_notification(text) and not _is_credential_request(text) and not _has_suspicious_url_or_threat(text):
                    score = int(result.get("risk_score", 0))
                    if score >= 70:
                        result["risk_score"] = min(score, 35)
                        result["verdict"] = "SAFE"
                        result["confidence"] = max(int(result.get("confidence", 80)), 85)
                return result
            except Exception:
                logging.exception("Groq JSON parse failed")
                return self._heuristic_fallback(text)
        except Exception as e:
            logging.exception(f"Groq analyze error: {e}")
            return self._heuristic_fallback(text)

    def _heuristic_fallback(self, text: str) -> dict:
        """Context-aware fallback when Groq is unavailable."""
        t = text.lower()
        flags: list[str] = []
        kw_hits: list[KeywordHit] = []
        categories: set[str] = set()

        # Start with context check: only pure notifications with no suspicious URLs or requests
        is_safe_notif = _is_safe_notification(text)
        is_cred_req = _is_credential_request(text)
        has_susp_url = _has_suspicious_url_or_threat(text)

        if is_safe_notif and not is_cred_req and not has_susp_url:
            # Clearly a legitimate notification
            score = 10
            threats = self._extract_threats(text)
            return {
                "risk_score": score,
                "confidence": 90,
                "verdict": "SAFE",
                "summary": "This appears to be a legitimate system notification.",
                "explanation": "The message contains characteristics of a legitimate notification: it delivers information (OTP, transaction, order update) without requesting any sensitive action. The 'do not share' advisory further confirms this is a genuine system message.",
                "categories": ["Safe Notification"],
                "red_flags": [],
                "actions": ["No action required. This appears to be a legitimate message."],
                "checklist": [
                    "Never share your OTP with anyone, even bank officials",
                    "This OTP was sent by the system — keep it private",
                    "If you did not initiate this request, contact your bank",
                ],
                "keywords": [],
                "entities": list(dict.fromkeys(threats["phones"] + threats["emails"])),
                "threat_breakdown": {
                    "links": [], "urls": [], "phones": threats["phones"],
                    "emails": threats["emails"], "suspicious_domains": [],
                    "money_requests": [], "urgency": [], "social_engineering": [],
                },
            }

        # Scam keyword scoring — context-aware
        score = 10
        keyword_map = {
            "reply with otp": (40, "high", "Requesting OTP — classic scam", "OTP Scam"),
            "send your otp": (40, "high", "Requesting OTP — classic scam", "OTP Scam"),
            "share your otp": (40, "high", "Requesting OTP", "OTP Scam"),
            "enter your otp": (35, "high", "OTP entry request", "OTP Scam"),
            "update kyc": (35, "high", "Fake KYC update scam", "KYC Scam"),
            "kyc expired": (35, "high", "Fake KYC expiry", "KYC Scam"),
            "account blocked": (30, "high", "Fear tactic", "Phishing"),
            "account suspended": (30, "high", "Fear tactic", "Phishing"),
            "click here to verify": (30, "high", "Phishing link", "Phishing"),
            "click here to claim": (35, "high", "Phishing claim link", "Phishing"),
            "claim your refund": (35, "high", "Refund lure", "UPI Fraud"),
            "refund link": (30, "high", "Suspicious refund request", "UPI Fraud"),
            "cancel transaction": (25, "medium", "Phishing cancellation pretext", "Social Engineering"),
            "won a prize": (35, "high", "Lottery scam", "Lottery Scam"),
            "you have won": (35, "high", "Lottery scam", "Lottery Scam"),
            "claim your reward": (30, "high", "Reward scam", "Lottery Scam"),
            "install the app": (25, "high", "Malware delivery", "Phishing"),
            "download apk": (30, "high", "Malicious APK", "Phishing"),
            "share your pin": (40, "high", "PIN request — never legitimate", "OTP Scam"),
            "share your cvv": (40, "high", "CVV request — never legitimate", "OTP Scam"),
            "share your password": (40, "high", "Password request", "Phishing"),
            "verify your account": (20, "medium", "Verification pretext", "Phishing"),
            "limited time offer": (15, "medium", "Urgency tactic", "Social Engineering"),
            "act immediately": (15, "medium", "Urgency pressure", "Social Engineering"),
            "bit.ly": (20, "high", "Shortened URL hides destination", "Phishing"),
            "tinyurl": (20, "high", "Shortened URL", "Phishing"),
            # Law enforcement impersonation & digital arrest / extortion
            "cbi officer": (45, "high", "Impersonating law enforcement (CBI)", "Digital Arrest Scam"),
            "cbi": (30, "high", "Law enforcement trigger", "Digital Arrest Scam"),
            "police officer": (35, "high", "Impersonating police", "Digital Arrest Scam"),
            "cyber crime": (30, "high", "Cyber crime department lure", "Digital Arrest Scam"),
            "money laundering": (35, "high", "Intimidation / extortion tactic", "Digital Arrest Scam"),
            "illegal money laundering": (40, "high", "Intimidation / extortion tactic", "Digital Arrest Scam"),
            "will be arrested": (45, "high", "Arrest threat / extortion", "Digital Arrest Scam"),
            "arrested in": (40, "high", "Arrest threat / extortion", "Digital Arrest Scam"),
            "digital arrest": (50, "high", "Confirmed digital arrest scam pattern", "Digital Arrest Scam"),
            "clearance account": (35, "high", "Fake government clearance account", "Digital Arrest Scam"),
            "arrest warrant": (40, "high", "Fake arrest warrant threat", "Digital Arrest Scam"),
            "illegal parcel": (35, "high", "Courier scam lure", "Courier Scam"),
            "customs department": (30, "high", "Customs extortion lure", "Courier Scam"),
            "part time job": (35, "high", "Task / job scam lure", "Job Scam"),
            "like youtube videos": (40, "high", "YouTube task scam", "Job Scam"),
            "earn money daily": (30, "high", "Job / investment scam lure", "Job Scam"),
            "urgent notice": (20, "medium", "Pressure / urgency tactic", "Social Engineering"),
            "final warning": (25, "high", "Urgency / fear tactic", "Social Engineering"),
        }
        # Scam regex pattern rules — captures morphological variants (liking/like, rating/rate, earn daily, etc.)
        SCAM_REGEX_RULES = [
            # 1. Job / Work from home / Social media task scams
            (r"\bpart[\s-]time\b.*\b(?:job|work|opportunity|income|earn)\b", 35, "high", "Part-time job/task scam pattern", "Job Scam"),
            (r"\bwork\s+from\s+home\b", 25, "medium", "Unsolicited work-from-home offer", "Job Scam"),
            (r"\b(?:like|liking|watch|watching)\s+(?:youtube|videos|reels|tiktok)\b", 40, "high", "Social media liking task lure", "Job Scam"),
            (r"\b(?:rate|rating|review|reviewing)\s+(?:hotels|maps|google|apps)\b", 35, "high", "Fake rating/review task fraud", "Job Scam"),
            (r"\bearn\b.*(?:\d+|rs\.?|₹).*\b(?:daily|per\s+day|monthly|every\s+day)\b", 35, "high", "Unrealistic daily earning claims", "Job Scam"),
            (r"\bdaily\s+(?:payout|income|salary|earning|returns)\b", 30, "high", "Daily payout lure", "Job Scam"),
            (r"\b(?:contact|whatsapp|message|join)\b.*\b(?:hr|manager|priya|neha|pooja|telegram|whatsapp)\b", 30, "high", "Directing to unverified WhatsApp/Telegram recruitment", "Social Engineering"),
            (r"\b(?:claim|get)\b.*(?:\d+|rs\.?|₹)?.*\b(?:bonus|reward|cash|gift|commission)\b", 25, "medium", "Bonus/reward lure to hook victims", "Social Engineering"),

            # 2. Electricity & Utility scams
            (r"\b(?:electricity|power|light)\b.*\b(?:disconnect|disconnection|cut\s*off)\b", 45, "high", "Power disconnection threat", "Utility Scam"),
            (r"\bbill\s+(?:not\s+updated|pending|overdue)\b.*\b(?:power|disconnect|tonight|electricity)\b", 35, "high", "Fake bill pending electricity threat", "Utility Scam"),
            (r"\b(?:electricity|power)\s+office\b", 25, "medium", "Electricity department impersonation", "Utility Scam"),

            # 3. UPI & Refund scams
            (r"\b(?:approve|accept)\b.*\b(?:payment|request|collect|transaction)\b.*\b(?:receive|get|claim|cashback)\b", 45, "high", "Deceptive UPI collect request to steal funds", "UPI Fraud"),
            (r"\benter\s+(?:your\s+)?(?:upi\s+)?pin\b.*\b(?:receive|claim|get|refund)\b", 50, "high", "PIN entry request to 'receive' money — guaranteed scam", "UPI Fraud"),
            (r"\bcashback\b.*\b(?:phonepe|gpay|paytm|upi)\b", 30, "high", "Fake UPI cashback scheme", "UPI Fraud"),

            # 4. Digital Arrest & Law Enforcement Extortion
            (r"\b(?:parcel|courier|package)\b.*\b(?:illegal|drugs|narcotics|customs|seized|intercepted)\b", 50, "high", "Illegal parcel narcotics interception threat", "Digital Arrest Scam"),
            (r"\b(?:digital\s+arrest|arrest\s+warrant|face\s+arrest|jailed)\b", 50, "high", "Digital arrest / law enforcement extortion threat", "Digital Arrest Scam"),
            (r"\b(?:cbi|police|customs|narcotics|crime\s+branch|court|ed)\b.*\b(?:warrant|arrest|verification|seized)\b", 45, "high", "Law enforcement coercion pretext", "Digital Arrest Scam"),

            # 5. Bank / KYC / Impersonation
            (r"\b(?:kyc|pan|aadhaar)\b.*\b(?:expire|expired|suspend|suspended|block|blocked|update|verify|deactivat)\b", 40, "high", "Fake KYC expiry threat", "KYC Scam"),
            (r"\b(?:yono|netbanking|bank\s+account)\b.*\b(?:block|suspend|deactivat|close|hold)\b", 40, "high", "Account blocking intimidation", "Phishing"),
            (r"\b(?:sbi|hdfc|icici|axis|kotak|pnb)\b.*\b(?:kyc|pan|suspend|verify|block)\b", 35, "high", "Bank impersonation with urgency", "Phishing"),

            # 6. Lottery & Instant Loans
            (r"\b(?:won|winner|congratulations)\b.*(?:\d+|rs\.?|₹|lottery|prize|car|iphone)\b", 40, "high", "Lottery/prize award fraud", "Lottery Scam"),
            (r"\b(?:pre-?approved|instant)\s+loan\b.*(?:\d+|rs\.?|₹|processing\s+fee)\b", 35, "high", "Pre-approved loan with upfront fee lure", "Loan Scam"),
        ]

        for pattern, pts, risk, reason, cat in SCAM_REGEX_RULES:
            if re.search(pattern, t):
                score += pts
                flags.append(reason)
                kw_hits.append({"term": reason, "risk": risk, "reason": reason})
                categories.add(cat)

        for kw, (pts, risk, reason, cat) in keyword_map.items():
            if kw in t:
                score += pts
                flags.append(f"Contains '{kw}'")
                kw_hits.append({"term": kw, "risk": risk, "reason": reason})
                categories.add(cat)

        if is_cred_req:
            score = max(score, 75)
            categories.add("Credential Theft")

        # Major confirmed scam categories threshold
        if any(cat in categories for cat in ["Job Scam", "Utility Scam", "Digital Arrest Scam", "UPI Fraud", "KYC Scam"]):
            score = max(score, 88)

        # Law enforcement extortion / digital arrest combination rule
        has_authority = any(w in t for w in ["cbi", "police", "court", "arrest", "customs", "cyber crime", "narcotics", "crime branch"])
        has_money_demand = any(w in t for w in ["transfer", "pay", "deposit", "rs.", "₹", "clearance account"])
        has_threat = any(w in t for w in ["arrest", "jailed", "legal action", "warrant", "suspended", "blocked"])
        if has_authority and (has_money_demand or has_threat):
            score = max(score, 75)
            flags.append("Law enforcement extortion or digital arrest pattern detected")
            categories.add("Digital Arrest Scam")

        if has_susp_url:
            score += 35
            flags.append("Contains unverified or suspicious external link")
            categories.add("Phishing")

        if "http://" in t:
            score += 15
            flags.append("Contains insecure HTTP link")
            categories.add("Phishing")

        score = max(0, min(score, 98))
        verdict = _normalize_verdict("", score)

        threats = self._extract_threats(text)
        urgency_terms = [w for w in ["urgent", "immediately", "now", "expire", "today", "final warning"] if w in t]
        money_terms = [w for w in ["upi", "pay", "rs.", "₹", "transfer", "refund"] if w in t]
        social_terms = [w for w in ["bank", "police", "rbi", "officer", "kyc"] if w in t]

        if "Job Scam" in categories:
            summary = "HIGH RISK: Part-time work-from-home task scam detected."
            explanation = "This message displays classic patterns of task-based employment fraud: offering high daily returns for simple tasks (liking YouTube videos, rating Google Maps) and redirecting you to WhatsApp or Telegram. Scammers initially pay token amounts, then lure victims into private groups demanding large deposit tasks where funds are stolen."
            actions = [
                "Do NOT message the recruiter on WhatsApp or Telegram",
                "Never pay any 'deposit', 'material charge', or 'task fee' to get job earnings",
                "Block the sender's phone number immediately",
                "Report the incident on cybercrime.gov.in or call 1930",
            ]
        elif "Utility Scam" in categories:
            summary = "HIGH RISK: Fraudulent electricity bill disconnection threat detected."
            explanation = "Legitimate electricity boards never threaten immediate disconnection via personal SMS with unauthorized mobile numbers. Scammers use fear to induce urgent calls where they trick you into installing remote access apps (AnyDesk/TeamViewer) or making payments."
            actions = [
                "Do NOT call the personal mobile number provided in the message",
                "Verify your bill status exclusively through the official state electricity portal or consumer app",
                "Report the sender number to Sanchar Saathi (Chakshu) and cybercrime.gov.in",
            ]
        elif "Digital Arrest Scam" in categories:
            summary = "CRITICAL RISK: Digital arrest / law enforcement impersonation threat detected."
            explanation = "Police, CBI, and Customs never issue arrest notices via WhatsApp/SMS, nor do they conduct 'digital arrests' over video calls or demand money into 'clearance accounts'. This is a severe extortion tactic."
            actions = [
                "Immediately disconnect the call and block the sender",
                "Do not transfer any money to any 'verification' or 'clearance' account",
                "Call the National Cyber Crime Helpline at 1930 immediately",
            ]
        else:
            summary = f"Heuristic detection: {verdict} risk based on suspicious patterns."
            explanation = "Rule-based analysis detected suspicious patterns. Review the red flags and verify through official channels before taking action."
            actions = [
                "Do not share OTP/PIN/CVV with anyone",
                "Verify sender via official bank channels",
                "Avoid clicking links in unverified messages",
                "Report to cybercrime.gov.in or call 1930 if suspicious",
            ]

        return {
            "risk_score": score,
            "confidence": 75,
            "verdict": verdict,
            "summary": summary,
            "explanation": explanation,
            "categories": list(categories) or ["General"],
            "red_flags": flags or ["No obvious red flags detected"],
            "actions": actions,
            "checklist": [
                "Confirm sender identity via official channels",
                "Never share OTP, PIN, CVV, or passwords",
                "Do not click on unverified short links or APK downloads",
                "Block and report suspicious numbers to 1930",
            ],
            "keywords": kw_hits,
            "entities": list(dict.fromkeys(threats["links"] + threats["phones"] + threats["emails"])),
            "threat_breakdown": {
                "links": threats["links"],
                "urls": threats["urls"],
                "phones": threats["phones"],
                "emails": threats["emails"],
                "suspicious_domains": [d for d in threats["urls"] if any(s in d.lower() for s in ["bit.ly", "tinyurl", "t.co"])],
                "money_requests": money_terms,
                "urgency": urgency_terms,
                "social_engineering": social_terms,
            },
        }