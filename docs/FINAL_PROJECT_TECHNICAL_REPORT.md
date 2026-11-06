# FRAUDRADAR-V2: COMPREHENSIVE PROJECT TECHNICAL AUDIT & EVALUATION REPORT

**Project Name**: FraudRadar-v2 (Scam Defense AI)  
**Repository Working Directory**: `/Users/apple/Desktop/FraudRadar-v2`  
**Live Production URL**: [https://fraudradar-gray-wood.reflex.run](https://fraudradar-gray-wood.reflex.run)  
**Reflex Cloud Deployment ID**: `aed221fd-9887-44e0-9a10-a4a3477a1d16` (Current active build)  
**Git Remote**: `https://github.com/Yashr4635/FraudRadar-v2.git` (`branch: main`, Commit: `1cf6f5a`)  
**Evaluation Date**: November 7, 2026  
**Target Audience**: External Academic Examiners, Project Evaluation Board, Technical Reviewers  

---

## EXECUTIVE SUMMARY & TRUTHFUL ENGINEERING DISCLOSURE

FraudRadar-v2 is an India-focused cyber threat detection and scam defense platform designed to protect citizens, students, and digital consumers against financial cyber fraud. The application analyzes text messages, URLs, phone numbers, screenshots, and QR codes to detect phishing, UPI fraud, electricity bill disconnection threats, job/task fraud, digital arrest extortion, and KYC harvesting.

### Truthful Implementation Status Matrix

| Engineering Area | Status | Implementation Truth & Verifiable Codebase Reality |
| :--- | :--- | :--- |
| **Scam Detection Engine** | **Implemented & Verified** | Hybrid multi-tier detection architecture combining sub-millisecond curated intelligence, a deterministic rule-based heuristic classifier, and an external cloud LLM API (**Groq API** running `qwen/qwen3.8-27b`). **No custom deep neural network or proprietary model was trained from scratch.** |
| **URL Threat Scanning** | **Implemented & Verified** | URL parsing, TLD risk heuristics, lookalike detection, and multi-engine threat queries (**Google Safe Browsing API**, **VirusTotal v3 API**, and **PhishTank**). When external API keys are active, queries execute in parallel worker pools with memory caching. |
| **Authentication Flow** | **Implemented & Verified** | Cryptographically salted 8-digit email OTP authentication with single-use verification, 10-minute TTL, PBKDF2-HMAC-SHA256 password hashing, dynamic HS256 JWT sessions, and Google SMTP (`smtp.gmail.com:587`) STARTTLS outbound delivery. |
| **Database Persistence** | **Implemented & Verified** | Dual-tier persistence engine: Local ACID SQLite WAL-mode (`data/auth.db`) and Supabase PostgreSQL (`DATABASE_URL` / `SUPABASE_DB_URL`) with automatic schema verification and table migration. |
| **Dedicated Legal Pages** | **Implemented & Verified** | Dedicated unauthenticated public routes (`/terms`, `/terms-of-service`, `/privacy`, `/privacy-policy`) compliant with the Indian Information Technology Act 2000 and Digital Personal Data Protection (DPDP) Act 2023. |
| **OCR & QR Code Scanning** | **Partially Implemented** | Native file upload and state management exist in `upload_state.py`. OCR leverages Tesseract (`pytesseract`) and QR decode leverages `pyzbar`. In cloud Linux containers lacking underlying system shared libraries (`libzbar0`, `tesseract-ocr`), it safely degrades without crashing the core app. |
| **Automated ML Training Pipeline** | **Not Implemented** | The project does **not** maintain an offline dataset training harness (e.g., PyTorch, TensorFlow, Scikit-learn model artifacts). It operates as an **API-driven and heuristic hybrid decision engine**. |

---

## 1. PROJECT OBJECTIVES & PROBLEM STATEMENT

### 1.1 Problem Statement
According to the Indian Cyber Crime Coordination Centre (I4C) under the Ministry of Home Affairs, over ₹1,750 crore was lost by Indian citizens to cyber fraud in the first quarter of 2024 alone. The threat landscape in India features unique sociotechnical attack vectors:
1. **Utility Cutoff Threats**: Impersonating electricity distribution companies (Discoms) threatening immediate disconnection at night to force calls to personal mobile numbers.
2. **Prepaid Task / Job Fraud**: Promising daily earnings of ₹2,500–₹8,000 for liking YouTube videos or writing Google Maps reviews, redirecting victims to Telegram deposit traps.
3. **Digital Arrest & Extortion**: Posing as CBI, Mumbai Police, or Customs officers alleging narcotics in courier parcels to extort money into fake "clearance accounts".
4. **Bank KYC / YONO Suspension**: Phishing links sent via SMS falsely claiming PAN or KYC expiration to harvest Internet banking credentials.
5. **UPI QR & Collect Fraud**: Tricking victims into entering their UPI PIN under the false premise of receiving cashbacks or refunds.

### 1.2 Project Objective
FraudRadar-v2 provides an accessible, private, zero-ad-tracking digital defense dashboard that empowers users to evaluate suspicious communications in under 2 seconds. The platform delivers actionable, India-specific guidance, step-by-step checklists, and direct emergency routing to the National Cybercrime Reporting Portal (**1930** / [cybercrime.gov.in](https://cybercrime.gov.in)).

---

## 2. HIGH-LEVEL SYSTEM ARCHITECTURE

```
                                  [ USER CLIENT BROWSER ]
                                             │
                                             ▼
                      [ Reflex Pure-Python Fullstack Framework ]
                                (Frontend React / Next.js)
                                             │
                            ┌────────────────┴────────────────┐
                            │ WebSocket / REST Event Pipeline │
                            ▼                                 ▼
                   [ AuthState Controller ]         [ ScanState Controller ]
                            │                                 │
              ┌─────────────┴─────────────┐         ┌─────────┴─────────┐
              ▼                           ▼         ▼                   ▼
      [ Local SQLite WAL ]       [ Google SMTP ]  [ Fast LRU Cache ]  [ Groq Cloud LLM ]
       (data/auth.db) &         (smtp.gmail.com)  (<1ms Curated +       (qwen3.8-27b
      [ Supabase Postgres ]                        512-slot Cache)       via 3.5s pool)
                                                            │
                                                            ▼
                                                [ External Threat APIs ]
                                                 ├─ Google Safe Browsing
                                                 ├─ VirusTotal API v3
                                                 └─ PhishTank Engine
```

### Core Architecture Components

1. **Frontend Layer**:
   - Compiled by Reflex 0.9.6 into a high-performance React / Next.js single-page application styled with Tailwind CSS v4 and Radix UI primitives.
   - Communicates bi-directionally with the backend via WebSocket channels for instantaneous DOM state synchronization.
2. **Backend Application Layer**:
   - Asynchronous Python 3.13 engine powered by Starlette and Granian ASGI web servers.
   - Event-driven state machines (`ScanState`, `AuthState`, `UploadState`, `AssistantState`) running in isolated user sessions.
3. **Database Layer**:
   - Primary: Acid-compliant SQLite with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) stored in `fraudradar_ai_scam_detection_v2/data/auth.db`.
   - Secondary / Cloud: Supabase PostgreSQL relational database configured via `DATABASE_URL` with automated schema verification and migration.
4. **Authentication & Messaging Engine**:
   - Password Hashing: PBKDF2-HMAC-SHA256 with cryptographically generated 16-byte random salts and 100,000 iterations.
   - OTP Generation: 8-digit cryptographically secure pseudorandom numbers (`secrets.randbelow(100_000_000)`).
   - OTP Hash Storage: Single-use HMAC-SHA256 hashed records with 10-minute expiry and a 5-attempt brute-force threshold.
   - Outbound Delivery: STARTTLS direct connection to Google SMTP (`smtp.gmail.com:587`).
5. **Detection & AI Core**:
   - Tier 1: In-memory pre-warmed sub-millisecond evaluation cache for high-confidence threats and curated samples (<2ms).
   - Tier 2: Deterministic heuristic classifier evaluating 50+ contextual regex patterns, urgent phrase clusters, and credential theft markers.
   - Tier 3: Asynchronous parallel worker pool querying external threat APIs (Google Safe Browsing, VirusTotal, PhishTank).
   - Tier 4: Cloud LLM Inference using Groq API (`qwen/qwen3.8-27b`) with connection pooling, structured JSON mode, and a strict 3.5s timeout.

---

## 3. ACTUAL IMPLEMENTATION VS. COMMON MISCONCEPTIONS

| Common Reviewer Misconception | Codebase Reality & True Implementation |
| :--- | :--- |
| *"You trained your own custom machine learning model on an Indian scam dataset."* | **False.** No machine learning model was trained or fine-tuned. The platform utilizes Groq's API hosting the open-weights model `qwen/qwen3.8-27b`, paired with a custom deterministic heuristic rule engine. |
| *"Confidence scores represent statistical probability distributions."* | **False.** Confidence scores are computed heuristically based on the density and agreement of matched indicators (e.g., presence of unverified phone + urgency + cutoff threat = 95% confidence). |
| *"HTTPS guarantees that a URL is safe."* | **False.** The application explicitly informs users that HTTPS only encrypts the transport connection; over 80% of modern phishing websites use free Let's Encrypt SSL certificates. |
| *"OTPs are sent using third-party SMS gateways."* | **False.** Authentication OTPs are delivered directly to the user's verified email inbox via authenticated SMTP (`smtp.gmail.com:587`). |

---

## 4. DETAILED SUMMARY OF PROJECT FILES

- `fraudradar_ai_scam_detection_v2/fraudradar_ai_scam_detection_v2.py`: Root application definition, route bindings, sitemap, and head stylesheets.
- `fraudradar_ai_scam_detection_v2/states/scan_state.py`: Primary fraud evaluation engine, Groq client connection pool, external API checkers, threat extraction, and scoring algorithms.
- `fraudradar_ai_scam_detection_v2/states/auth_state.py`: User lifecycle controller, 8-digit OTP submission/verification, session persistence, and authorization guards.
- `fraudradar_ai_scam_detection_v2/states/assistant_state.py`: 24/7 AI Scam Defense Assistant with contextual Indian fraud knowledge and offline heuristic fallback.
- `fraudradar_ai_scam_detection_v2/states/upload_state.py`: Image and QR code upload processing, optical character extraction, and scan routing.
- `fraudradar_ai_scam_detection_v2/services/auth_db.py`: Database connection factory, migration logic, schema definitions, and secure credential storage.
- `fraudradar_ai_scam_detection_v2/services/otp_service.py`: 8-digit OTP generation, rate limiting, and HS256 JWT session issuance.
- `fraudradar_ai_scam_detection_v2/services/email_service.py`: Unified email delivery provider with priority failover (SMTP -> Resend -> SendGrid -> Dev Outbox).
- `fraudradar_ai_scam_detection_v2/components/legal_pages.py`: Dedicated Terms of Service and Privacy Policy public routes.
- `fraudradar_ai_scam_detection_v2/components/pages.py`: Dashboard, Analyze UI, History view, Scam Guide, and Helpline directory.
- `tests/test_scan_engine.py`: 29 automated tests verifying URL analysis, API error handling, verdict consistency, and synthetic scam benchmarks.
- `tests/test_otp_auth.py`: 13 automated tests verifying OTP hashing, rate limiting, expiry, and single-use enforcement.
- `tests/test_live_app.py`: 16 live integration tests verifying route health and HTTP response codes on production.

---

## 5. DOCUMENTATION DIRECTORY INDEX

The detailed analysis for all technical review aspects is organized into the following specialized documents in the `docs/` folder:

1. [docs/TECH_STACK_AND_ARCHITECTURE.md](file:///Users/apple/Desktop/FraudRadar-v2/docs/TECH_STACK_AND_ARCHITECTURE.md): Exhaustive breakdown of frameworks, versions, database schemas, and data flow.
2. [docs/AI_SCAM_DETECTION_LOGIC.md](file:///Users/apple/Desktop/FraudRadar-v2/docs/AI_SCAM_DETECTION_LOGIC.md): In-depth trace of the scam detection pipeline, prompt design, score contribution, and 5 realistic case studies.
3. [docs/URL_ANALYSIS_AND_SECURITY.md](file:///Users/apple/Desktop/FraudRadar-v2/docs/URL_ANALYSIS_AND_SECURITY.md): Technical details on URL normalization, lookalike domain detection, and multi-engine threat intelligence.
4. [docs/TESTING_AND_EVALUATION_REPORT.md](file:///Users/apple/Desktop/FraudRadar-v2/docs/TESTING_AND_EVALUATION_REPORT.md): Evaluation methodology, synthetic test benchmark results, edge-case testing, and live verification metrics.
5. [docs/PROJECT_CHANGELOG.md](file:///Users/apple/Desktop/FraudRadar-v2/docs/PROJECT_CHANGELOG.md): Historical record of commits, architectural refactors, bug fixes, and resolved regressions.
6. [docs/EXTERNAL_REVIEW_QUESTIONS_AND_ANSWERS.md](file:///Users/apple/Desktop/FraudRadar-v2/docs/EXTERNAL_REVIEW_QUESTIONS_AND_ANSWERS.md): 45 technically rigorous questions and answers prepared for academic and industry examiners.
7. [docs/PROJECT_DEMO_SCRIPT.md](file:///Users/apple/Desktop/FraudRadar-v2/docs/PROJECT_DEMO_SCRIPT.md): Step-by-step 2-minute pitch, 5-minute technical walkthrough, and interactive demo sequence.
