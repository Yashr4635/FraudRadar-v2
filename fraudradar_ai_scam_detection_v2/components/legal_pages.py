import reflex as rx
from fraudradar_ai_scam_detection_v2.components.landing import landing_nav, landing_footer


def legal_header(title: str, subtitle: str, badge: str, last_updated: str = "November 2026") -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                badge,
                class_name="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-orange-50 text-[#E8471A] border border-orange-200 mb-3",
            ),
            rx.el.h1(
                title,
                class_name="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight mb-3",
            ),
            rx.el.p(
                subtitle,
                class_name="text-base sm:text-lg text-gray-600 max-w-2xl leading-relaxed mb-4",
            ),
            rx.el.div(
                rx.icon("calendar", class_name="h-4 w-4 text-gray-400 mr-2 inline"),
                rx.el.span(f"Last updated: {last_updated}", class_name="text-xs text-gray-500 font-medium"),
                rx.el.span(" · ", class_name="text-gray-300 mx-2"),
                rx.icon("shield-check", class_name="h-4 w-4 text-emerald-500 mr-1 inline"),
                rx.el.span("DPDP Act 2023 & IT Act 2000 Aligned", class_name="text-xs text-emerald-700 font-medium"),
                class_name="flex items-center flex-wrap pt-2 border-t border-gray-100",
            ),
            class_name="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center",
        ),
        class_name="bg-gradient-to-b from-orange-50/50 via-white to-white border-b border-gray-200/60",
    )


def legal_section(number: str, title: str, content: rx.Component) -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    number,
                    class_name="h-8 w-8 rounded-lg bg-orange-100 text-[#E8471A] font-bold text-sm flex items-center justify-center shrink-0 mt-0.5",
                ),
                rx.el.h2(
                    title,
                    class_name="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight",
                ),
                class_name="flex items-center gap-3 mb-4",
            ),
            rx.el.div(
                content,
                class_name="text-sm sm:text-base text-gray-700 leading-relaxed space-y-4 pl-11",
            ),
            class_name="p-6 sm:p-8 rounded-2xl bg-white border border-gray-200/80 shadow-xs mb-6",
        ),
        class_name="scroll-mt-24",
    )


def terms_content() -> rx.Component:
    return rx.el.div(
        legal_section(
            "1",
            "Acceptance of Terms & Scope",
            rx.el.div(
                rx.el.p(
                    "Welcome to FraudRadar Scam Defense AI (\"FraudRadar\", \"we\", \"us\", or \"our\"). "
                    "By accessing our platform, website, API, or services, you (\"User\", \"you\") agree to be bound "
                    "by these Terms of Service (\"Terms\"). If you do not agree to these Terms, please do not use our services."
                ),
                rx.el.p(
                    "FraudRadar is an AI-powered scam defense and threat detection engine developed for citizens, consumers, "
                    "and academic research to analyze suspicious messages, phishing URLs, malicious QR codes, and phone numbers "
                    "targeting India's digital ecosystem."
                ),
            ),
        ),
        legal_section(
            "2",
            "Educational & Safety Disclaimer (No Legal or Financial Advice)",
            rx.el.div(
                rx.el.div(
                    rx.icon("triangle-alert", class_name="h-5 w-5 text-amber-600 shrink-0 mt-0.5"),
                    rx.el.div(
                        rx.el.p(
                            "CRITICAL NOTICE: FraudRadar provides probabilistic risk assessments and heuristic indicators for "
                            "educational, awareness, and fraud mitigation purposes. Scam risk scores, threat tags, and AI recommendations "
                            "do NOT constitute formal legal testimony, financial advisory, or statutory law enforcement judgments.",
                            class_name="font-semibold text-amber-900 text-sm",
                        ),
                        class_name="text-xs text-amber-800 mt-1",
                    ),
                    class_name="flex gap-3 p-4 rounded-xl bg-amber-50 border border-amber-200 mb-4",
                ),
                rx.el.p(
                    "While our multi-tier detection brain synthesizes real-time threat intelligence from Google Safe Browsing, "
                    "VirusTotal, PhishTank, and LLM pattern recognition, attackers continuously innovate. Always verify suspicious "
                    "financial transactions through official banking channels before taking irreversible action."
                ),
            ),
        ),
        legal_section(
            "3",
            "User Accounts, OTP Security & Authentication",
            rx.el.div(
                rx.el.p(
                    "To access personalized scan history and advanced AI analysis tools, users may create an account using email "
                    "and password or cryptographic email One-Time Passwords (OTP). You agree to:"
                ),
                rx.el.ul(
                    rx.el.li("Provide accurate contact information during registration."),
                    rx.el.li("Maintain the strict confidentiality of your one-time passwords (OTPs) and account credentials."),
                    rx.el.li("Never share, disclose, or forward 8-digit OTPs to third parties or callers claiming to represent FraudRadar."),
                    rx.el.li("Notify us immediately of any unauthorized access to your account or session token."),
                    class_name="list-disc pl-5 space-y-2 mt-2",
                ),
                rx.el.p(
                    "FraudRadar staff and representatives will NEVER call, message, or email you requesting your verification OTP.",
                    class_name="font-semibold text-gray-900 mt-2",
                ),
            ),
        ),
        legal_section(
            "4",
            "Acceptable Use Policy",
            rx.el.div(
                rx.el.p("You agree NOT to use FraudRadar to:"),
                rx.el.ul(
                    rx.el.li("Analyze or reverse-engineer proprietary algorithms for unauthorized commercial exploitation."),
                    rx.el.li("Submit content that infringes upon the intellectual property or privacy rights of any third party."),
                    rx.el.li("Conduct denial-of-service attacks, automated API scraping, or deliberate load degradation against our infrastructure."),
                    rx.el.li("Circumvent authentication controls, cryptographic rate limiting, or session tokens."),
                    rx.el.li("Use our scam signatures to craft more evasive malware, phishing lures, or fraudulent campaigns."),
                    class_name="list-disc pl-5 space-y-2 mt-2",
                ),
                rx.el.p("Violations of this policy will result in immediate account termination and IP address blacklisting."),
            ),
        ),
        legal_section(
            "5",
            "Emergency Cybercrime Reporting Protocol",
            rx.el.div(
                rx.el.p(
                    "FraudRadar is a private scam detection initiative and is NOT an official government police or judicial department. "
                    "If you have already transferred money to a scammer or are under active extortion / digital arrest threats, take immediate action:"
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p("Government Cybercrime Helpline", class_name="text-xs text-gray-500 font-semibold uppercase"),
                        rx.el.p("Dial 1930 (Toll Free 24x7)", class_name="text-xl font-bold text-[#E8471A]"),
                        rx.el.p("Immediate golden-hour bank account freezing", class_name="text-xs text-gray-600"),
                        class_name="p-4 rounded-xl bg-orange-50 border border-orange-200 flex-1",
                    ),
                    rx.el.div(
                        rx.el.p("National Cybercrime Reporting Portal", class_name="text-xs text-gray-500 font-semibold uppercase"),
                        rx.el.a("https://cybercrime.gov.in", href="https://cybercrime.gov.in", target="_blank", class_name="text-base font-bold text-blue-600 hover:underline"),
                        rx.el.p("Ministry of Home Affairs (MHA), Government of India", class_name="text-xs text-gray-600"),
                        class_name="p-4 rounded-xl bg-blue-50 border border-blue-200 flex-1",
                    ),
                    class_name="grid grid-cols-1 sm:grid-cols-2 gap-4 my-4",
                ),
            ),
        ),
        legal_section(
            "6",
            "Statutory Compliance & Indian IT Act",
            rx.el.div(
                rx.el.p(
                    "These Terms are governed by and construed in accordance with the laws of the Republic of India, including the "
                    "Information Technology Act, 2000 (as amended), the Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021, "
                    "and the Digital Personal Data Protection Act, 2023 (DPDP Act)."
                ),
                rx.el.p(
                    "Any disputes arising from these Terms or the use of FraudRadar shall be subject to the exclusive jurisdiction of the competent courts in Hyderabad, Telangana, India."
                ),
            ),
        ),
        legal_section(
            "7",
            "Limitation of Liability & Indemnification",
            rx.el.div(
                rx.el.p(
                    "To the maximum extent permitted by applicable law, FraudRadar, its developers, academic supervisors, and contributors "
                    "shall not be liable for any indirect, incidental, punitive, or consequential damages resulting from your reliance on scan results, "
                    "delayed notification, or undetected zero-day fraud tactics."
                ),
            ),
        ),
        class_name="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8",
    )


def privacy_content() -> rx.Component:
    return rx.el.div(
        legal_section(
            "1",
            "Our Core Privacy Commitment",
            rx.el.div(
                rx.el.div(
                    rx.icon("shield-check", class_name="h-6 w-6 text-emerald-600 shrink-0"),
                    rx.el.div(
                        rx.el.p(
                            "ZERO AD TRACKING · NO DATA SELLING · CITIZEN-FIRST DEFENSE",
                            class_name="font-bold text-emerald-950 text-sm",
                        ),
                        rx.el.p(
                            "FraudRadar was created to protect citizens against predatory digital scams. We do not sell, rent, monetize, or broker your personal information to third parties, advertising networks, or data aggregators.",
                            class_name="text-xs sm:text-sm text-emerald-900 mt-1",
                        ),
                    ),
                    class_name="flex gap-3 p-5 rounded-xl bg-emerald-50 border border-emerald-200 mb-4",
                ),
                rx.el.p(
                    "This Privacy Policy explains how FraudRadar collects, processes, and protects your personal data in strict alignment with the "
                    "Digital Personal Data Protection Act, 2023 (DPDP Act) of India."
                ),
            ),
        ),
        legal_section(
            "2",
            "Information We Collect",
            rx.el.div(
                rx.el.p("We adhere to strict data minimization principles and collect only what is strictly required to safeguard your safety:"),
                rx.el.div(
                    rx.el.div(
                        rx.el.h4("A. Account & Authentication Data", class_name="font-semibold text-gray-900 mb-1"),
                        rx.el.p("Email address, encrypted password hash (bcrypt), or 8-digit OTP verification hashes for session authentication.", class_name="text-sm text-gray-600"),
                        class_name="p-4 rounded-xl bg-gray-50 border border-gray-200",
                    ),
                    rx.el.div(
                        rx.el.h4("B. Scan Content (Submitted by You)", class_name="font-semibold text-gray-900 mb-1"),
                        rx.el.p("Text snippets, SMS lures, WhatsApp scam messages, target URLs, or sender phone numbers you submit for risk analysis.", class_name="text-sm text-gray-600"),
                        class_name="p-4 rounded-xl bg-gray-50 border border-gray-200",
                    ),
                    rx.el.div(
                        rx.el.h4("C. Diagnostic & Security Metrics", class_name="font-semibold text-gray-900 mb-1"),
                        rx.el.p("IP addresses (anonymized in logs), browser user-agent, and rate-limiting counters to prevent brute-force abuse.", class_name="text-sm text-gray-600"),
                        class_name="p-4 rounded-xl bg-gray-50 border border-gray-200",
                    ),
                    class_name="grid grid-cols-1 sm:grid-cols-3 gap-3 my-3",
                ),
            ),
        ),
        legal_section(
            "3",
            "How We Process & Analyze Your Scans",
            rx.el.div(
                rx.el.p("When you submit content to FraudRadar:"),
                rx.el.ol(
                    rx.el.li("1. Local Threat Heuristics: Evaluates keyword urgency, impersonation flags, and deceptive payment patterns locally in memory."),
                    rx.el.li("2. Threat Intelligence Verification: Queries Google Safe Browsing, VirusTotal, and PhishTank for malicious domain reputation using secure SHA-256 hashes where supported."),
                    rx.el.li("3. Groq AI Inference: Analyzes psychological manipulation tactics via isolated, enterprise-tier LLM inference without retaining training data."),
                    rx.el.li("4. Private History Storage: Analysis results are bound strictly to your authenticated User ID in our database and are accessible only by you."),
                    class_name="list-decimal pl-5 space-y-2 mt-2",
                ),
            ),
        ),
        legal_section(
            "4",
            "Security & Cryptographic Protections",
            rx.el.div(
                rx.el.p("We employ industry-leading cybersecurity practices to protect your data at rest and in transit:"),
                rx.el.ul(
                    rx.el.li("Encryption in Transit: All web communication enforces TLS 1.3 encryption with strict HTTPS headers."),
                    rx.el.li("Salted Hashing at Rest: OTP codes and user passwords are cryptographically salted and hashed; raw credentials are never stored in plaintext."),
                    rx.el.li("Dynamic 256-Bit JWT Secrets: Session tokens are digitally signed with dynamically resolved 256-bit cryptographic keys."),
                    rx.el.li("Masked Privacy Logging: Email addresses in audit logs are masked (e.g. j*****e@domain.com) to prevent internal exposure."),
                    class_name="list-disc pl-5 space-y-2 mt-2",
                ),
            ),
        ),
        legal_section(
            "5",
            "Your Rights Under DPDP Act 2023",
            rx.el.div(
                rx.el.p("As a digital citizen under the Digital Personal Data Protection Act, 2023, you hold the following statutory rights:"),
                rx.el.ul(
                    rx.el.li("Right to Access: View all previous scans, risk scores, and saved reports directly from your dashboard."),
                    rx.el.li("Right to Erasure / Deletion: Clear your complete scan history or delete your account at any time via Settings."),
                    rx.el.li("Right to Correction: Update your registered display name and credentials."),
                    rx.el.li("Right to Grievance Redressal: Contact our designated Data Grievance Officer regarding any data inquiry."),
                    class_name="list-disc pl-5 space-y-2 mt-2",
                ),
            ),
        ),
        legal_section(
            "6",
            "Data Retention Policy",
            rx.el.div(
                rx.el.p(
                    "Scan history is retained solely for your convenience and personal defense awareness. Unauthenticated scans "
                    "are processed ephemerally in RAM and are not persisted to persistent user databases. Authenticated users can "
                    "purge their scan history with a single click from the History tab."
                ),
            ),
        ),
        legal_section(
            "7",
            "Grievance Officer & Inquiries",
            rx.el.div(
                rx.el.p("In accordance with the Information Technology Act 2000 and DPDP Act 2023 rules, contact our Grievance Desk for any privacy matter:"),
                rx.el.div(
                    rx.el.p("FraudRadar Privacy & Compliance Desk", class_name="font-semibold text-gray-900"),
                    rx.el.p("Email: support@fraudradar.app", class_name="text-sm text-gray-600"),
                    rx.el.p("Academic Project: Department of Computer Science & Engineering, HITAM", class_name="text-sm text-gray-600"),
                    rx.el.p("Hyderabad, Telangana, India", class_name="text-sm text-gray-600"),
                    class_name="p-4 rounded-xl bg-gray-50 border border-gray-200 my-2",
                ),
            ),
        ),
        class_name="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8",
    )


def public_legal_shell(header_component: rx.Component, body_component: rx.Component, active_tab: str) -> rx.Component:
    return rx.el.div(
        landing_nav(),
        header_component,
        # Tab switch bar between Terms and Privacy
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon("file-text", class_name="h-4 w-4 mr-2 inline"),
                    "Terms of Service",
                    href="/terms",
                    class_name=f"px-5 py-2.5 rounded-xl font-semibold text-sm transition-all { 'bg-white text-gray-900 shadow-sm border border-gray-200' if active_tab == 'terms' else 'text-gray-600 hover:text-gray-900' }",
                ),
                rx.el.a(
                    rx.icon("shield", class_name="h-4 w-4 mr-2 inline"),
                    "Privacy Policy",
                    href="/privacy",
                    class_name=f"px-5 py-2.5 rounded-xl font-semibold text-sm transition-all { 'bg-white text-gray-900 shadow-sm border border-gray-200' if active_tab == 'privacy' else 'text-gray-600 hover:text-gray-900' }",
                ),
                rx.el.a(
                    rx.icon("scale", class_name="h-4 w-4 mr-2 inline"),
                    "Trust & Compliance",
                    href="/legal",
                    class_name=f"px-5 py-2.5 rounded-xl font-semibold text-sm transition-all { 'bg-white text-gray-900 shadow-sm border border-gray-200' if active_tab == 'legal' else 'text-gray-600 hover:text-gray-900' }",
                ),
                class_name="inline-flex p-1.5 rounded-2xl bg-gray-100/80 border border-gray-200/60 max-w-xl mx-auto",
            ),
            class_name="text-center pt-8 pb-4 bg-white",
        ),
        body_component,
        # Bottom CTA banner
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3("Ready to Protect Yourself Against Digital Scams?", class_name="text-xl sm:text-2xl font-bold text-gray-900 mb-2"),
                    rx.el.p("Join citizens across India analyzing suspicious SMS, UPI requests, and phishing links in real-time.", class_name="text-sm text-gray-600 max-w-xl"),
                    class_name="text-center sm:text-left",
                ),
                rx.el.div(
                    rx.el.a(
                        "Create Free Account",
                        href="/signup",
                        class_name="px-6 py-3 rounded-xl bg-[#E8471A] hover:bg-[#c43a13] text-white font-semibold text-sm shadow-lg shadow-orange-300/40 transition-all",
                    ),
                    rx.el.a(
                        "Sign In",
                        href="/login",
                        class_name="px-6 py-3 rounded-xl bg-white hover:bg-gray-50 text-gray-700 font-semibold text-sm border border-gray-200 transition-all",
                    ),
                    class_name="flex items-center gap-3 justify-center sm:justify-end shrink-0 mt-4 sm:mt-0",
                ),
                class_name="max-w-4xl mx-auto p-8 rounded-3xl bg-gradient-to-br from-orange-50/80 via-white to-amber-50/50 border border-orange-200/70 flex flex-col sm:flex-row items-center justify-between shadow-xs",
            ),
            class_name="px-4 sm:px-6 lg:px-8 py-10 bg-white",
        ),
        landing_footer(),
        class_name="min-h-screen bg-slate-50 font-['Inter'] antialiased flex flex-col",
    )


def dedicated_terms_page() -> rx.Component:
    return public_legal_shell(
        legal_header(
            "Terms of Service",
            "Please review the terms, safety disclaimers, and guidelines governing the use of FraudRadar Scam Defense AI.",
            "Official Legal Terms",
        ),
        terms_content(),
        active_tab="terms",
    )


def dedicated_privacy_page() -> rx.Component:
    return public_legal_shell(
        legal_header(
            "Privacy Policy",
            "How FraudRadar protects your personal data, scan inputs, and privacy under the DPDP Act 2023.",
            "Data Protection & Privacy",
        ),
        privacy_content(),
        active_tab="privacy",
    )

