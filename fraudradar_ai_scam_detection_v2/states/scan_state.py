import os
import re
import csv
import io
import json
import logging
import datetime
from urllib.parse import urlparse, parse_qs
import reflex as rx
from typing import TypedDict

try:
    from groq import Groq
except Exception:
    logging.exception("Unexpected error")
    Groq = None


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

# Patterns that indicate REQUESTING credentials (scam)
CREDENTIAL_REQUEST_PATTERNS = [
    r"\b(?:send|share|provide|give|reply\s+with|enter|submit|tell)\s+(?:your\s+)?(?:otp|pin|cvv|password|card\s+number|account\s+number)\b",
    r"\bverify\s+(?:your\s+)?(?:otp|pin|account|card)\b",
    r"\bclick\s+(?:here|the\s+link)\s+(?:to\s+)?(?:verify|update|confirm|claim)\b",
    r"\bupdate\s+(?:your\s+)?kyc\b",
    r"\bkyc\s+(?:expired|update|verification)\b",
    r"\baccount\s+(?:will\s+be\s+)?(?:blocked|suspended|closed|terminated)\b",
    r"\bwon\b.*\b(?:prize|lottery|reward|cash|iphone|gift)\b",
    r"\bclaim\s+(?:your\s+)?(?:prize|reward|cash|refund)\b",
    r"\binstall\s+(?:the\s+)?(?:app|apk)\b",
    r"\bdownload\s+(?:this\s+)?(?:app|apk|file)\b",
    r"\bapprove\s+(?:the\s+)?(?:payment|request|transaction)\b",
]


def _is_safe_notification(text: str) -> bool:
    """Returns True if the text looks like a legitimate notification."""
    t = text.lower()
    safe_hits = sum(
        1 for p in OTP_NOTIFICATION_PATTERNS if re.search(p, t, re.IGNORECASE)
    )
    scam_hits = sum(
        1 for p in CREDENTIAL_REQUEST_PATTERNS if re.search(p, t, re.IGNORECASE)
    )
    return safe_hits > 0 and scam_hits == 0


def _is_credential_request(text: str) -> bool:
    """Returns True if the text is requesting credentials."""
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
    v = (verdict or "").strip().upper()
    if v in ("HIGH", "MEDIUM", "SAFE"):
        return v
    if v in ("CONFIRMED SCAM", "LIKELY SCAM", "SCAM"):
        return "HIGH"
    if v in ("SUSPICIOUS",):
        return "MEDIUM"
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "SAFE"


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

        try:
            result = self._analyze_sync(analysis_text, analysis_type)
        except Exception as e:
            logging.exception(f"Analyze unexpected: {e}")
            result = self._heuristic_fallback(analysis_text)

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
        extracted = self._extract_threats(analysis_text)
        for key in ("links", "urls", "phones", "emails"):
            for v in extracted[key]:
                if v not in breakdown[key]:
                    breakdown[key].append(v)
        self.threat_breakdown = breakdown
        self.contributions = self._build_contributions(
            analysis_text, breakdown, self.keywords, analysis_type
        )
        self.has_result = True
        self.is_analyzing = False

        user_id = ""
        try:
            from fraudradar_ai_scam_detection_v2.states.auth_state import AuthState
            auth = await self.get_state(AuthState)
            user_id = auth.user_id or ""
        except Exception:
            logging.exception("auth lookup")

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

        try:
            self._persist_to_supabase(record)
        except Exception as e:
            logging.exception(f"Supabase persistence skipped: {e}")

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
        url_re = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
        domain_re = re.compile(r"\b(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s]*)?", re.IGNORECASE)
        phone_re = re.compile(r"(?:\+?\d[\d\s\-]{7,}\d)")
        email_re = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
        links = url_re.findall(text)
        emails = email_re.findall(text)
        phones = [p.strip() for p in phone_re.findall(text) if len(re.sub(r"\D", "", p)) >= 8]
        bare = [d for d in domain_re.findall(text) if not d.startswith("http")]
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

        # Pre-check: if clearly a safe notification, short-circuit with low score
        if _is_safe_notification(text) and not _is_credential_request(text):
            context_hint = "\n\nNOTE: This message appears to be a legitimate system notification (OTP delivery, order update, transaction confirmation). Analyze carefully with low bias toward false positives."
        else:
            context_hint = ""

        try:
            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Input type: {input_type}\n\nAnalyze this content:\n\n{text}{context_hint}",
                    },
                ],
                temperature=0.1,
                max_tokens=900,
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content or ""
            try:
                result = json.loads(content)
                # Post-processing safety net: if our rule engine says safe but
                # LLM says HIGH, cap it at MEDIUM unless there are real indicators
                if _is_safe_notification(text) and not _is_credential_request(text):
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

        # Start with context check
        is_safe_notif = _is_safe_notification(text)
        is_cred_req = _is_credential_request(text)

        if is_safe_notif and not is_cred_req:
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
        }
        for kw, (pts, risk, reason, cat) in keyword_map.items():
            if kw in t:
                score += pts
                flags.append(f"Contains '{kw}'")
                kw_hits.append({"term": kw, "risk": risk, "reason": reason})
                categories.add(cat)

        if is_cred_req and not is_safe_notif:
            score = max(score, 75)

        if "http://" in t:
            score += 15
            flags.append("Contains insecure HTTP link")
            categories.add("Phishing")

        score = min(score, 95)
        if score >= 70:
            verdict = "HIGH"
        elif score >= 40:
            verdict = "MEDIUM"
        else:
            verdict = "SAFE"

        threats = self._extract_threats(text)
        urgency_terms = [w for w in ["urgent", "immediately", "now", "expire", "today", "final warning"] if w in t]
        money_terms = [w for w in ["upi", "pay", "rs.", "₹", "transfer", "refund"] if w in t]
        social_terms = [w for w in ["bank", "police", "rbi", "officer", "kyc"] if w in t]

        return {
            "risk_score": score,
            "confidence": 75,
            "verdict": verdict,
            "summary": f"Heuristic detection: {verdict} risk based on suspicious patterns.",
            "explanation": "Rule-based analysis detected suspicious patterns. Review the red flags and verify through official channels before taking action.",
            "categories": list(categories) or ["General"],
            "red_flags": flags or ["No obvious red flags detected"],
            "actions": [
                "Do not share OTP/PIN/CVV with anyone",
                "Verify sender via official bank channels",
                "Avoid clicking links in unverified messages",
                "Report to cybercrime.gov.in or call 1930 if suspicious",
            ],
            "checklist": [
                "Confirm sender identity via official app",
                "Never share OTP, PIN, CVV, or password",
                "Do not click on unverified short links",
                "Block and report suspicious numbers",
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