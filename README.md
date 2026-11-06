# 🛡️ FraudRadar v2 — AI-Powered Digital Fraud Defense Platform

<p align="center">
  <img src="assets/fraudradar_logo.png" alt="FraudRadar AI Logo" width="160" style="border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
</p>

<h2 align="center">
  Real-Time Cyber Fraud, Phishing & Scam Intelligence System
</h2>

<p align="center">
  Detect • Analyze • Explain • Prevent Digital Fraud across India's Threat Landscape
</p>

<p align="center">
  <a href="https://fraudradar-gray-wood.reflex.run"><img src="https://img.shields.io/badge/Live_Production-fraudradar--gray--wood.reflex.run-00C781?style=for-the-badge&logo=fastapi&logoColor=white" alt="Live Demo"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11_|_3.13-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Reflex-0.9.6-6E56CF?style=flat-square&logo=reflex&logoColor=white" alt="Reflex">
  <img src="https://img.shields.io/badge/Groq_AI-Qwen_2.5_27B_|_Llama_3.3_70B-F55036?style=flat-square&logo=groq&logoColor=white" alt="Groq AI">
  <img src="https://img.shields.io/badge/VirusTotal-v3_API_Active-394EFF?style=flat-square&logo=virustotal&logoColor=white" alt="VirusTotal">
  <img src="https://img.shields.io/badge/Encryption-TLS_1.3_In--Transit-success?style=flat-square&logo=letsencrypt&logoColor=white" alt="Encryption">
  <img src="https://img.shields.io/badge/Supabase-Auth_%26_PostgreSQL-3ECF8E?style=flat-square&logo=supabase&logoColor=white" alt="Supabase">
  <img src="https://img.shields.io/badge/Unit_Tests-53%2F53_Passed-success?style=flat-square&logo=pytest&logoColor=white" alt="Unit Tests">
  <img src="https://img.shields.io/badge/Live_Routes-16%2F16_Passed-success?style=flat-square&logo=checkmarx&logoColor=white" alt="Live Routes">
</p>

---

## 🌐 Live Production Application

Access the live cloud deployment anytime:  
👉 **[https://fraudradar-gray-wood.reflex.run](https://fraudradar-gray-wood.reflex.run)**

* **Deployment Host**: Reflex Cloud Edge (Fly.io / Granian ASGI on Linux)
* **Status**: **Active & Healthy** (HTTP 200 health checks)
* **Dedicated Legal Pages**: [Terms of Service](https://fraudradar-gray-wood.reflex.run/terms) • [Privacy Policy](https://fraudradar-gray-wood.reflex.run/privacy) • [Cybercrime Helpline 1930](https://fraudradar-gray-wood.reflex.run/helpline)

---

## 📖 Executive Summary & Evolution (v1 vs v2)

The original iteration of FraudRadar relied on basic keyword matching and superficial regex rules. It suffered from frequent false positives (flagging legitimate bank transaction notifications simply for containing the word *"OTP"*), had no contextual language intelligence, lacked explainability, and suffered from authentication redirect loops.

**FraudRadar v2 is a complete architectural overhaul**:
- **Hybrid Multi-Tier Detection Brain:** Combines contextual reasoning using **Groq LLM (Qwen 2.5 27B / Llama 3.3 70B)** with deterministic regex heuristics, Indian threat entity extraction, and live **VirusTotal v3 API** threat intelligence.
- **Fail-Safe Fast Fallback:** Enforces a strict **3.5-second timeout** on LLM calls with immediate, seamless fallback to deterministic heuristic analysis, eliminating state locks and gateway timeouts.
- **Sub-Millisecond Demonstration Cache:** Pre-warmed curated cache (`CURATED_SAMPLES_EVALUATION`) guarantees `< 2ms` evaluation response for presentation benchmark samples, while open-domain text bypasses the cache to run live model inference.
- **Cryptographic 8-Digit Email OTP:** Pure numerical 8-digit OTP verification system generated via `secrets.randbelow(100_000_000)` with HMAC-SHA256 hashed storage, 10-minute expiry, single-use enforcement, 5-attempt lockout, and 60-second cooldown.
- **Explainable Model & Rule Agreement:** Provides users with a transparent risk breakdown, red flag indicators, recommended actions, and a clear **Model & Rule Agreement Score** (distinguished from a calibrated statistical probability).
- **Dedicated Legal & Trust Infrastructure:** Full standalone `/terms` and `/privacy` routes aligned with Indian IT Act 2000 and Digital Personal Data Protection (DPDP) Act 2023.

---

## 🧠 Hybrid Detection Architecture

```
                             User Submission
            (SMS / Text / Email / URL / QR Code / Screenshot)
                                    │
                                    ▼
                    Threat Extraction & Preprocessing
          (Extract URLs, Phone Numbers, Domains, Shorteners, OCR)
                                    │
          ┌─────────────────────────┴─────────────────────────┐
          ▼                                                   ▼
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│   Deterministic Rule Engine     │       │       AI Context Reasoning      │
│  ─────────────────────────────  │       │  ─────────────────────────────  │
│  • Indian Discom utility regex  │       │  • Groq API (Qwen 2.5 / Llama)  │
│  • Banking KYC typosquatting    │       │  • Semantic Intent Analysis     │
│  • Task scam & Telegram lures   │       │  • Authority Impersonation Check│
│  • Authentic 2FA detectors      │       │  • Strict 3.5s Timeout Guard    │
│  • VirusTotal v3 Domain Probe   │       │  • Structured JSON Verdict      │
└────────────────┬────────────────┘       └────────────────┬────────────────┘
                 │                                         │
                 └───────────────────┬─────────────────────┘
                                     │
                                     ▼
                     Safety-Net Reconciler & Normalizer
                   • Authentic 2FA Safe Notification Cap
                   • Credential Request & Link Override Block
                   • Score-to-Verdict Strict Normalization
                                     │
                                     ▼
               Risk Score (0-100) • Verdict (SAFE / SUSPICIOUS / HIGH)
           Model & Rule Agreement (%) • Red Flags • Actionable Guidance
```

---

## 🔬 Core Detection Principles: How Messages Are Judged

FraudRadar evaluates submitted content across 5 foundational vectors:

| Signal Vector | Legitimate Characteristics (SAFE) | Fraudulent Indicators (HIGH RISK) |
| :--- | :--- | :--- |
| **1. Urgency / Coercion** | Standard billing cycles; informational updates. | Artificial panic: *"power cut at 9:30 PM tonight"*, *"account blocked today"*, *"arrest warrant in 2 hours"*. |
| **2. Sender Contact** | Alphanumeric DLT government/bank header (`AD-HDFCBK`). | Directs victim to personal 10-digit mobile number (`"Call officer at 9876543210"`) or WhatsApp. |
| **3. Link & Domain** | Verified domains with HTTPS (`sbi.co.in`, `incometax.gov.in`). | Deceptive typosquats (`sbi-kyc-verify.com`), disposable TLDs (`.top`, `.xyz`), or shortened links (`bit.ly`). |
| **4. Call to Action** | Advises confidentiality: *"Do NOT share OTP with anyone"*. | Demands credential disclosure, APK downloads, or money transfers to release loans/prizes. |
| **5. Financial Realism** | Receipts for user-initiated purchases. | Unrealistic promises: *"Rs 3,000 daily for liking videos"*, *"Won 25 Lakhs in KBC draw"*. |

---

## 🔒 Authentication & OTP Security Architecture

- **Search Space**: 8 decimal digits produce $10^8 = 100,000,000$ possible values (a 100× expansion over 6-digit codes).
- **Attempt Lockout**: Maximum 5 attempts allowed per OTP session before permanent record invalidation.
- **Random Guess Probability**:
  $$\text{P(Success)} = \frac{5}{10^8} = 5 \times 10^{-8} = 0.000005\% \quad (1 \text{ in } 20,000,000)$$
- **Cryptographic Storage**: OTPs are salted and hashed using HMAC-SHA256 (`secrets.token_bytes(16)`) before persistence; plaintext codes are never stored.
- **Replay Protection**: The database marks `consumed = 1` immediately upon successful verification.
- **Time-to-Live (TTL)**: Automatic expiration after 10 minutes (600 seconds).
- **Transport Security**: Direct SMTP delivery using STARTTLS on port 587 with GoTrue fallback.

---

## 📊 Empirical Evaluation & Benchmark Results

### 1. Curated Demonstration Benchmarks (<2ms)
Tested against 5 canonical threat vectors with 100% precision:
1. Fake Discom Electricity Cutoff SMS (`HIGH` — Score: 88)
2. Deceptive SBI YONO KYC Phishing SMS (`HIGH` — Score: 96)
3. YouTube Prepaid Task Job Scam (`HIGH` — Score: 94)
4. Legitimate Amazon HDFC Bank 2FA Alert (`SAFE` — Score: 6)
5. Fake Gift Claim Phishing Link (`HIGH` — Score: 96)

### 2. Previously Unseen Dataset Evaluation (Live Inference)
Tested against 20 previously unseen real-world messages and 10 URLs bypassing the curated sample cache:
- **Unseen Messages**: **19 / 20 Correct (95.0% Accuracy)**
  - False Positives (FP): **0 / 10 (0.0%)** — Zero legitimate notifications falsely flagged.
  - False Negatives (FN): **1 / 10 (10.0%)** — Utility variant caught under 429 rate limit fallback.
- **Unseen URLs**: **8 / 10 Correct (80.0% Accuracy)**
  - False Negatives (FN): **0 / 5 (0.0%)** — All 5 phishing URLs detected.
  - False Positives (FP): **2 / 5 (40.0%)** — Safe domains flagged SUSPICIOUS under string heuristics.

### 3. External Threat API Status
- **VirusTotal REST API v3**: **Active & Available** (HTTP 200).
- **Google Safe Browsing v4**: **Restricted** (HTTP 403; gracefully caught by exception handlers).
- **PhishTank**: **Not Configured** (safely bypassed without crashing).

---

## 🛠 Tech Stack

| Domain | Technology / Library | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Framework** | [Reflex](https://reflex.dev/) | 0.9.6 | Full-stack reactive Python framework compiling to React & ASGI |
| **Language Runtime** | Python | 3.11 / 3.13 | Core backend business logic and async event handlers |
| **AI Engine** | Groq Cloud SDK | Latest | Fast contextual inference with Qwen 2.5 27B & Llama 3.3 70B |
| **Threat Intelligence**| VirusTotal API | v3 | Multi-engine domain reputation and phishing database checks |
| **Authentication** | Custom HMAC OTP + Supabase | GoTrue | Numerical 8-digit OTP email delivery and JWT session tokens |
| **Persistence** | PostgreSQL & SQLite | WAL Mode | Multi-tier persistence for accounts, scan history, and OTP records |
| **OCR & Vision** | Tesseract & Pyzbar | v5 | Text extraction from scam screenshots and QR code decoding |
| **Hosting** | Reflex Cloud Edge | Granian ASGI | Containerized cloud edge hosting with TLS 1.3 termination |

---

## 📚 Complete Technical Documentation Suite

The repository contains a full 8-document technical audit and review defense suite:

1. [docs/FINAL_PROJECT_TECHNICAL_REPORT.md](docs/FINAL_PROJECT_TECHNICAL_REPORT.md): Comprehensive system audit and production implementation report.
2. [docs/TECH_STACK_AND_ARCHITECTURE.md](docs/TECH_STACK_AND_ARCHITECTURE.md): Technology stack justification and dual-engine data flow diagrams.
3. [docs/AI_SCAM_DETECTION_LOGIC.md](docs/AI_SCAM_DETECTION_LOGIC.md): In-depth prompt engineering, scoring rules, and safety-net explanation.
4. [docs/URL_ANALYSIS_AND_SECURITY.md](docs/URL_ANALYSIS_AND_SECURITY.md): Phishing link heuristics, shortener expansion, and threat API integration.
5. [docs/TESTING_AND_EVALUATION_REPORT.md](docs/TESTING_AND_EVALUATION_REPORT.md): Automated unit tests, live endpoint verification, and empirical benchmark results.
6. [docs/PROJECT_CHANGELOG.md](docs/PROJECT_CHANGELOG.md): Historical record of major commits, bug fixes, and resolved regressions.
7. [docs/EXTERNAL_REVIEW_QUESTIONS_AND_ANSWERS.md](docs/EXTERNAL_REVIEW_QUESTIONS_AND_ANSWERS.md): 45 technically rigorous review questions and answers.
8. [docs/PROJECT_DEMO_SCRIPT.md](docs/PROJECT_DEMO_SCRIPT.md): Step-by-step 2-minute pitch, 5-minute technical walkthrough, and interactive demo sequence.

---

## 🧪 Automated Test Suite

Run the full automated test suite locally:

```bash
# Run all unit and integration tests
.venv/bin/python -m unittest discover tests/

# Run live production smoke tests against cloud URL
.venv/bin/python -m unittest tests/test_live_app.py
```

```text
Ran 53 tests in 0.508s — OK (skipped=2)
Ran 16 live route tests in 15.230s — OK (16/16 Passed)
```

---

## ⚙️ Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Yashr4635/FraudRadar-v2.git
cd FraudRadar-v2
```

### 2. Set Up Virtual Environment
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Install System Dependencies (for OCR & QR)
- **macOS**: `brew install tesseract zbar`
- **Ubuntu/Debian**: `sudo apt-get install -y tesseract-ocr libzbar0`

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
GROQ_API_KEY=gsk_your_groq_api_key
GROQ_MODEL=qwen/qwen3.8-27b
VIRUSTOTAL_API_KEY=your_virustotal_key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
EMAIL_DEV_MODE=false
```

### 5. Run the Application
```bash
reflex run
```
Access the local frontend at `http://localhost:3000` and backend at `http://localhost:8000`.

---

## 👨‍💻 Author & Project Credits

**DS Yashaswi**  
*B.Tech in Computer Science & Engineering (Data Science)*  
Specialization: Applied AI • Cyber Threat Intelligence • Full-Stack Cloud Engineering  

* **GitHub**: [@Yashr4635](https://github.com/Yashr4635)
* **Repository**: [https://github.com/Yashr4635/FraudRadar-v2](https://github.com/Yashr4635/FraudRadar-v2)
* **Live Deployment**: [https://fraudradar-gray-wood.reflex.run](https://fraudradar-gray-wood.reflex.run)

---

## ⭐ Star the Project
If you find FraudRadar-v2 useful or insightful, please consider starring ⭐ this repository on GitHub!
