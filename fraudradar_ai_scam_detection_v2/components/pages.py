import reflex as rx
from fraudradar_ai_scam_detection_v2.components.sidebar import app_layout
from fraudradar_ai_scam_detection_v2.components.dashboard import dashboard_page as _dashboard_page
from fraudradar_ai_scam_detection_v2.states.auth_state import AuthState
from fraudradar_ai_scam_detection_v2.states.scan_state import ScanState
from fraudradar_ai_scam_detection_v2.states.assistant_state import AssistantState
from fraudradar_ai_scam_detection_v2.states.profile_state import ProfileState
from fraudradar_ai_scam_detection_v2.states.upload_state import (
    UploadState,
    SCREENSHOT_UPLOAD_ID,
    QR_UPLOAD_ID,
    ALLOWED_IMAGE_TYPES,
)


def card(*children, class_name: str = "") -> rx.Component:
    return rx.el.div(
        *children,
        class_name=f"bg-white border border-gray-200 rounded-xl p-6 {class_name}",
    )


def stat_card(
    label: str, value, icon: str, accent: str = "text-[#E8471A]"
) -> rx.Component:
    return card(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    label,
                    class_name="text-xs font-medium text-gray-500 uppercase tracking-wider",
                ),
                rx.el.p(
                    value, class_name="text-2xl font-bold text-gray-900 mt-2"
                ),
                class_name="flex-1",
            ),
            rx.el.div(
                rx.icon(icon, class_name=f"h-5 w-5 {accent}"),
                class_name="h-10 w-10 rounded-lg bg-orange-50 flex items-center justify-center",
            ),
            class_name="flex items-start justify-between",
        ),
    )


def verdict_badge(verdict) -> rx.Component:
    return rx.el.span(
        verdict,
        class_name=rx.match(
            verdict,
            (
                "SAFE",
                "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200 w-fit",
            ),
            (
                "MEDIUM",
                "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-yellow-50 text-yellow-700 border border-yellow-200 w-fit",
            ),
            (
                "HIGH",
                "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200 w-fit",
            ),
            "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 border border-gray-200 w-fit",
        ),
    )


def dashboard_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            stat_card(
                "Total Scans", ScanState.total_scans.to_string(), "scan-search"
            ),
            stat_card(
                "Scams Detected",
                ScanState.scams_detected.to_string(),
                "shield-alert",
            ),
            stat_card(
                "Avg Risk Score", f"{ScanState.avg_risk:.1f}", "trending-up"
            ),
            stat_card("Latest Verdict", ScanState.latest_verdict, "activity"),
            class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4",
        ),
        rx.el.div(
            card(
                rx.el.div(
                    rx.el.h3(
                        "Quick Actions",
                        class_name="text-base font-semibold text-gray-900",
                    ),
                    rx.el.p(
                        "Start protecting yourself in seconds.",
                        class_name="text-sm text-gray-500 mt-1",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.a(
                        rx.icon("scan-search", class_name="h-4 w-4"),
                        rx.el.span(
                            "Analyze Message", class_name="text-sm font-medium"
                        ),
                        href="/analyze",
                        class_name="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-[#E8471A] text-white hover:bg-[#c43a13] transition-colors",
                    ),
                    rx.el.a(
                        rx.icon("message-circle", class_name="h-4 w-4"),
                        rx.el.span(
                            "Ask Assistant", class_name="text-sm font-medium"
                        ),
                        href="/assistant",
                        class_name="flex items-center gap-2 px-4 py-2.5 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors",
                    ),
                    rx.el.a(
                        rx.icon("history", class_name="h-4 w-4"),
                        rx.el.span(
                            "View History", class_name="text-sm font-medium"
                        ),
                        href="/history",
                        class_name="flex items-center gap-2 px-4 py-2.5 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors",
                    ),
                    class_name="flex flex-wrap gap-3",
                ),
            ),
            card(
                rx.el.div(
                    rx.icon("phone-call", class_name="h-5 w-5 text-[#E8471A]"),
                    rx.el.h3(
                        "Emergency Helpline",
                        class_name="text-base font-semibold text-gray-900",
                    ),
                    class_name="flex items-center gap-2 mb-2",
                ),
                rx.el.p(
                    "Report cyber fraud immediately.",
                    class_name="text-sm text-gray-500",
                ),
                rx.el.div(
                    rx.el.a(
                        "Call 1930",
                        href="tel:1930",
                        class_name="inline-flex items-center justify-center px-4 py-2.5 rounded-lg bg-[#E8471A] text-white text-sm font-medium hover:bg-[#c43a13]",
                    ),
                    rx.el.a(
                        "cybercrime.gov.in",
                        href="https://cybercrime.gov.in",
                        target="_blank",
                        class_name="inline-flex items-center justify-center px-4 py-2.5 rounded-lg border border-gray-300 text-gray-700 text-sm font-medium hover:bg-gray-50",
                    ),
                    class_name="flex gap-3 mt-4",
                ),
            ),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4",
        ),
        card(
            rx.el.div(
                rx.el.h3(
                    "Recent Activity",
                    class_name="text-base font-semibold text-gray-900",
                ),
                rx.el.a(
                    "View all",
                    href="/history",
                    class_name="text-sm text-[#E8471A] hover:underline",
                ),
                class_name="flex items-center justify-between mb-4",
            ),
            rx.cond(
                ScanState.history.length() > 0,
                rx.el.div(
                    rx.foreach(
                        ScanState.history[:5],
                        lambda h: rx.el.div(
                            rx.el.div(
                                verdict_badge(h["verdict"]),
                                rx.el.p(
                                    h["timestamp"],
                                    class_name="text-xs text-gray-500",
                                ),
                                class_name="flex items-center gap-3",
                            ),
                            rx.el.p(
                                h["input_text"],
                                class_name="text-sm text-gray-700 mt-2 line-clamp-2",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        class_name=rx.cond(
                                            h["risk_score"] >= 70,
                                            "h-1.5 rounded-full bg-red-500",
                                            rx.cond(
                                                h["risk_score"] >= 40,
                                                "h-1.5 rounded-full bg-yellow-500",
                                                "h-1.5 rounded-full bg-green-500",
                                            ),
                                        ),
                                        custom_attrs={
                                            "style": {
                                                "width": f"{h['risk_score']}%"
                                            }
                                        },
                                    ),
                                    class_name="flex-1 h-1.5 rounded-full bg-gray-100",
                                ),
                                rx.el.p(
                                    f"{h['risk_score']}%",
                                    class_name="text-xs font-medium text-gray-600 ml-3",
                                ),
                                class_name="flex items-center mt-3",
                            ),
                            class_name="py-4 border-b border-gray-100 last:border-0",
                        ),
                    ),
                ),
                rx.el.div(
                    rx.icon(
                        "inbox", class_name="h-8 w-8 text-gray-300 mx-auto"
                    ),
                    rx.el.p(
                        "No scans yet",
                        class_name="text-sm text-gray-500 mt-2 text-center",
                    ),
                    rx.el.a(
                        "Run your first scan",
                        href="/analyze",
                        class_name="block text-sm text-[#E8471A] hover:underline text-center mt-1",
                    ),
                    class_name="py-8",
                ),
            ),
            class_name="mt-4",
        ),
        class_name="space-y-0",
    )


def dashboard_page() -> rx.Component:
    return _dashboard_page()


def _threat_section(label: str, icon: str, items, accent: str) -> rx.Component:
    return rx.cond(
        items.length() > 0,
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name=f"h-3.5 w-3.5 {accent}"),
                rx.el.p(
                    label,
                    class_name="text-[11px] font-bold text-gray-700 uppercase tracking-wider",
                ),
                rx.el.span(
                    items.length().to_string(),
                    class_name="ml-auto text-[10px] font-bold text-gray-500",
                ),
                class_name="flex items-center gap-1.5 mb-2",
            ),
            rx.el.div(
                rx.foreach(
                    items,
                    lambda v: rx.el.span(
                        v,
                        class_name="inline-block px-2 py-1 rounded-md text-[11px] font-mono bg-white border border-gray-200 text-gray-800 break-all",
                    ),
                ),
                class_name="flex flex-wrap gap-1.5",
            ),
            class_name="p-3 rounded-xl border border-gray-200 bg-gray-50/40",
        ),
        rx.fragment(),
    )


def threat_breakdown_card_inline() -> rx.Component:
    tb = ScanState.threat_breakdown
    return card(
        rx.el.div(
            rx.icon("radar", class_name="h-4 w-4 text-[#E8471A]"),
            rx.el.h4(
                "Threat Breakdown",
                class_name="text-sm font-semibold text-gray-900",
            ),
            class_name="flex items-center gap-2 mb-3",
        ),
        rx.el.div(
            _threat_section("Links", "link", tb["links"], "text-red-500"),
            _threat_section(
                "URLs / Domains", "globe", tb["urls"], "text-orange-500"
            ),
            _threat_section(
                "Phone Numbers", "phone", tb["phones"], "text-blue-500"
            ),
            _threat_section("Emails", "mail", tb["emails"], "text-purple-500"),
            _threat_section(
                "Suspicious Domains",
                "shield-alert",
                tb["suspicious_domains"],
                "text-red-600",
            ),
            _threat_section(
                "Money Requests",
                "indian-rupee",
                tb["money_requests"],
                "text-emerald-500",
            ),
            _threat_section(
                "Urgency", "clock", tb["urgency"], "text-yellow-500"
            ),
            _threat_section(
                "Social Engineering",
                "users",
                tb["social_engineering"],
                "text-pink-500",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-3",
        ),
        class_name="mt-4",
    )


def _input_type_tab(value: str, label: str, icon: str) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, class_name="h-3.5 w-3.5"),
        rx.el.span(label, class_name="text-xs font-semibold"),
        on_click=lambda: ScanState.set_input_type(value),
        class_name=rx.cond(
            ScanState.input_type == value,
            "inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-[#E8471A] text-white shadow-sm",
            "inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 hover:text-[#E8471A]",
        ),
    )


def _screenshot_upload_zone() -> rx.Component:
    return rx.el.div(
        rx.upload.root(
            rx.el.div(
                rx.icon("image-up", class_name="h-7 w-7 text-[#E8471A]"),
                rx.el.p(
                    "Drop a screenshot or click to browse",
                    class_name="text-sm font-bold text-gray-900 mt-2",
                ),
                rx.el.p(
                    "PNG, JPG, WEBP, BMP · max 6 MB · text will be auto-extracted via OCR",
                    class_name="text-[11px] text-gray-500 mt-1",
                ),
                class_name="flex flex-col items-center justify-center text-center py-8",
            ),
            id=SCREENSHOT_UPLOAD_ID,
            accept=ALLOWED_IMAGE_TYPES,
            multiple=False,
            max_files=1,
            max_size=6 * 1024 * 1024,
            on_drop=UploadState.handle_screenshot_upload(
                rx.upload_files(upload_id=SCREENSHOT_UPLOAD_ID)
            ),
            class_name="border-2 border-dashed border-orange-200 rounded-xl bg-orange-50/40 hover:bg-orange-50 hover:border-orange-300 transition-colors cursor-pointer",
        ),
        rx.cond(
            UploadState.is_processing,
            rx.el.div(
                rx.icon(
                    "loader-circle",
                    class_name="h-4 w-4 animate-spin text-[#E8471A]",
                ),
                rx.el.span(
                    "Extracting text from image...",
                    class_name="text-xs font-semibold text-gray-700",
                ),
                class_name="flex items-center gap-2 mt-3 p-2.5 rounded-lg bg-orange-50 border border-orange-200",
            ),
            rx.fragment(),
        ),
        rx.cond(
            UploadState.upload_error != "",
            rx.el.div(
                rx.icon("circle-alert", class_name="h-4 w-4 text-red-600"),
                rx.el.p(
                    UploadState.upload_error,
                    class_name="text-sm text-red-700",
                ),
                class_name="flex items-center gap-2 p-3 rounded-lg bg-red-50 border border-red-200 mt-3",
            ),
            rx.fragment(),
        ),
        rx.cond(
            UploadState.extracted_text != "",
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "scan-text", class_name="h-3.5 w-3.5 text-green-600"
                    ),
                    rx.el.p(
                        "Extracted text",
                        class_name="text-[11px] font-bold text-gray-700 uppercase tracking-wider",
                    ),
                    class_name="flex items-center gap-1.5 mb-1.5",
                ),
                rx.el.p(
                    UploadState.extracted_text,
                    class_name="text-xs text-gray-700 leading-relaxed font-mono whitespace-pre-wrap",
                ),
                class_name="mt-3 p-3 rounded-lg bg-green-50/40 border border-green-200",
            ),
            rx.fragment(),
        ),
    )


def _qr_upload_zone() -> rx.Component:
    return rx.el.div(
        rx.upload.root(
            rx.el.div(
                rx.icon("qr-code", class_name="h-7 w-7 text-[#E8471A]"),
                rx.el.p(
                    "Drop a QR code image or click to browse",
                    class_name="text-sm font-bold text-gray-900 mt-2",
                ),
                rx.el.p(
                    "PNG, JPG, WEBP, BMP · max 6 MB · the decoded URL will be analyzed",
                    class_name="text-[11px] text-gray-500 mt-1",
                ),
                class_name="flex flex-col items-center justify-center text-center py-8",
            ),
            id=QR_UPLOAD_ID,
            accept=ALLOWED_IMAGE_TYPES,
            multiple=False,
            max_files=1,
            max_size=6 * 1024 * 1024,
            on_drop=UploadState.handle_qr_upload(
                rx.upload_files(upload_id=QR_UPLOAD_ID)
            ),
            class_name="border-2 border-dashed border-orange-200 rounded-xl bg-orange-50/40 hover:bg-orange-50 hover:border-orange-300 transition-colors cursor-pointer",
        ),
        rx.cond(
            UploadState.is_processing,
            rx.el.div(
                rx.icon(
                    "loader-circle",
                    class_name="h-4 w-4 animate-spin text-[#E8471A]",
                ),
                rx.el.span(
                    "Decoding QR code...",
                    class_name="text-xs font-semibold text-gray-700",
                ),
                class_name="flex items-center gap-2 mt-3 p-2.5 rounded-lg bg-orange-50 border border-orange-200",
            ),
            rx.fragment(),
        ),
        rx.cond(
            UploadState.upload_error != "",
            rx.el.div(
                rx.icon("circle-alert", class_name="h-4 w-4 text-red-600"),
                rx.el.p(
                    UploadState.upload_error,
                    class_name="text-sm text-red-700",
                ),
                class_name="flex items-center gap-2 p-3 rounded-lg bg-red-50 border border-red-200 mt-3",
            ),
            rx.fragment(),
        ),
        rx.cond(
            UploadState.decoded_qr_value != "",
            rx.el.div(
                rx.el.div(
                    rx.icon("qr-code", class_name="h-3.5 w-3.5 text-green-600"),
                    rx.el.p(
                        "Decoded QR content",
                        class_name="text-[11px] font-bold text-gray-700 uppercase tracking-wider",
                    ),
                    class_name="flex items-center gap-1.5 mb-1.5",
                ),
                rx.el.p(
                    UploadState.decoded_qr_value,
                    class_name="text-xs text-gray-800 leading-relaxed font-mono break-all",
                ),
                class_name="mt-3 p-3 rounded-lg bg-green-50/40 border border-green-200",
            ),
            rx.fragment(),
        ),
    )


def _why_flagged_card() -> rx.Component:
    return rx.cond(
        ScanState.contributions.length() > 0,
        card(
            rx.el.div(
                rx.icon("microscope", class_name="h-4 w-4 text-[#E8471A]"),
                rx.el.h4(
                    "Why was this flagged?",
                    class_name="text-sm font-bold text-gray-900",
                ),
                rx.el.span(
                    ScanState.contributions.length().to_string() + " factors",
                    class_name="ml-auto text-[10px] font-bold text-[#E8471A] bg-orange-50 border border-orange-200 px-2 py-0.5 rounded-full",
                ),
                class_name="flex items-center gap-2 mb-3",
            ),
            rx.el.div(
                rx.foreach(
                    ScanState.contributions,
                    lambda c: rx.el.div(
                        rx.el.div(
                            rx.icon(
                                c["icon"],
                                class_name="h-4 w-4 text-[#E8471A]",
                            ),
                            class_name="h-9 w-9 rounded-xl bg-orange-50 border border-orange-100 flex items-center justify-center shrink-0",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.p(
                                    c["label"],
                                    class_name="text-sm font-bold text-gray-900",
                                ),
                                rx.el.span(
                                    "+" + c["points"].to_string() + " pts",
                                    class_name="ml-auto text-[10px] font-bold text-red-700 bg-red-50 border border-red-200 px-2 py-0.5 rounded-full",
                                ),
                                class_name="flex items-center gap-2",
                            ),
                            rx.el.p(
                                c["detail"],
                                class_name="text-xs text-gray-600 mt-1 leading-relaxed",
                            ),
                            class_name="flex-1 min-w-0",
                        ),
                        class_name="flex items-start gap-3 p-3 rounded-xl border border-orange-100 bg-gradient-to-br from-orange-50/30 to-white hover:from-orange-50 transition-colors",
                    ),
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-2",
            ),
            class_name="mt-4",
        ),
        rx.fragment(),
    )


def _highlighted_message_card() -> rx.Component:
    return rx.cond(
        (ScanState.keywords.length() > 0) & (ScanState.input_text != ""),
        card(
            rx.el.div(
                rx.icon("highlighter", class_name="h-4 w-4 text-[#E8471A]"),
                rx.el.h4(
                    "Original Message · Highlighted",
                    class_name="text-sm font-bold text-gray-900",
                ),
                class_name="flex items-center gap-2 mb-3",
            ),
            rx.el.div(
                rx.el.p(
                    ScanState.input_text,
                    class_name="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap font-mono break-words",
                ),
                class_name="p-4 rounded-xl bg-gray-50 border border-gray-200",
            ),
            rx.el.div(
                rx.el.p(
                    "Detected suspicious terms:",
                    class_name="text-[11px] font-bold text-gray-600 uppercase tracking-wider mb-2",
                ),
                rx.el.div(
                    rx.foreach(
                        ScanState.keywords,
                        lambda k: rx.el.span(
                            k["term"],
                            class_name=rx.match(
                                k["risk"],
                                (
                                    "high",
                                    "inline-block px-2 py-0.5 rounded-md text-[11px] font-bold font-mono bg-red-100 text-red-800 border border-red-300",
                                ),
                                (
                                    "medium",
                                    "inline-block px-2 py-0.5 rounded-md text-[11px] font-bold font-mono bg-yellow-100 text-yellow-800 border border-yellow-300",
                                ),
                                "inline-block px-2 py-0.5 rounded-md text-[11px] font-bold font-mono bg-blue-100 text-blue-800 border border-blue-300",
                            ),
                        ),
                    ),
                    class_name="flex flex-wrap gap-1.5",
                ),
                class_name="mt-3",
            ),
            class_name="mt-4",
        ),
        rx.fragment(),
    )


def analyze_content() -> rx.Component:
    return rx.el.div(
        card(
            rx.el.div(
                rx.el.h3(
                    "Analyze for Scams",
                    class_name="text-base font-semibold text-gray-900",
                ),
                rx.el.p(
                    "Choose an input type. Paste text, a URL, a phone number, or upload a screenshot or QR code.",
                    class_name="text-sm text-gray-500 mt-1",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                _input_type_tab("text", "Text", "type"),
                _input_type_tab("url", "URL", "link"),
                _input_type_tab("message", "Message", "message-square"),
                _input_type_tab("phone", "Phone", "phone"),
                _input_type_tab("image", "Screenshot", "image"),
                _input_type_tab("qr", "QR Code", "qr-code"),
                class_name="flex flex-wrap gap-2 mb-4",
            ),
            rx.match(
                ScanState.input_type,
                ("image", _screenshot_upload_zone()),
                ("qr", _qr_upload_zone()),
                (
                    "phone",
                    rx.el.div(
                        rx.icon(
                            "phone",
                            class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400",
                        ),
                        rx.el.input(
                            placeholder="+91 98765 43210",
                            default_value=ScanState.input_text,
                            on_change=ScanState.set_input_text.debounce(300),
                            class_name="w-full pl-10 pr-3 py-3 rounded-lg border border-gray-300 bg-white text-sm font-mono focus:outline-hidden focus:ring-2 focus:ring-[#E8471A]",
                        ),
                        class_name="relative",
                    ),
                ),
                (
                    "url",
                    rx.el.div(
                        rx.icon(
                            "link",
                            class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400",
                        ),
                        rx.el.input(
                            placeholder="https://example.com or bit.ly/abc",
                            default_value=ScanState.input_text,
                            on_change=ScanState.set_input_text.debounce(300),
                            class_name="w-full pl-10 pr-3 py-3 rounded-lg border border-gray-300 bg-white text-sm font-mono focus:outline-hidden focus:ring-2 focus:ring-[#E8471A]",
                        ),
                        class_name="relative",
                    ),
                ),
                rx.el.textarea(
                    placeholder="Paste suspicious SMS, WhatsApp message, email, or text here...",
                    default_value=ScanState.input_text,
                    on_change=ScanState.set_input_text.debounce(300),
                    class_name="w-full min-h-[160px] p-3 rounded-lg border border-gray-300 bg-white text-sm focus:outline-hidden focus:ring-2 focus:ring-[#E8471A] focus:border-transparent",
                ),
            ),
            rx.cond(
                ScanState.error != "",
                rx.el.div(
                    rx.icon("circle-alert", class_name="h-4 w-4 text-red-600"),
                    rx.el.p(ScanState.error, class_name="text-sm text-red-700"),
                    class_name="flex items-center gap-2 p-3 rounded-lg bg-red-50 border border-red-200 mt-3",
                ),
                rx.fragment(),
            ),
            rx.cond(
                (ScanState.input_type != "image")
                & (ScanState.input_type != "qr"),
                rx.el.div(
                    rx.el.button(
                        rx.cond(
                            ScanState.is_analyzing,
                            rx.fragment(
                                rx.icon(
                                    "loader-circle",
                                    class_name="h-4 w-4 animate-spin",
                                ),
                                rx.el.span("Analyzing..."),
                            ),
                            rx.fragment(
                                rx.icon(
                                    "scan-search",
                                    class_name="h-4 w-4",
                                ),
                                rx.el.span("Analyze Now"),
                            ),
                        ),
                        on_click=lambda: ScanState.analyze(
                            ScanState.input_text, ScanState.input_type
                        ),
                        disabled=ScanState.is_analyzing,
                        class_name="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#E8471A] text-white text-sm font-medium hover:bg-[#c43a13] disabled:opacity-50",
                    ),
                    rx.el.button(
                        "Clear",
                        on_click=ScanState.clear_result,
                        class_name="px-4 py-2.5 rounded-lg border border-gray-300 text-gray-700 text-sm font-medium hover:bg-gray-50",
                    ),
                    class_name="flex items-center gap-3 mt-4",
                ),
                rx.fragment(),
            ),
        ),
        rx.cond(
            ScanState.has_result,
            rx.el.div(
                card(
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "Risk Assessment",
                                class_name="text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    ScanState.risk_score.to_string() + "%",
                                    class_name="text-4xl font-bold text-gray-900",
                                ),
                                verdict_badge(ScanState.verdict),
                                class_name="flex items-center gap-3 mt-2",
                            ),
                            rx.el.div(
                                rx.icon(
                                    "gauge",
                                    class_name="h-3.5 w-3.5 text-gray-500",
                                ),
                                rx.el.span(
                                    "Confidence: ",
                                    class_name="text-xs text-gray-500",
                                ),
                                rx.el.span(
                                    ScanState.confidence.to_string() + "%",
                                    class_name="text-xs font-bold text-gray-900",
                                ),
                                class_name="flex items-center gap-1.5 mt-2",
                            ),
                            class_name="flex-1",
                        ),
                        rx.el.div(
                            rx.icon(
                                rx.cond(
                                    ScanState.risk_score >= 70,
                                    "shield-alert",
                                    rx.cond(
                                        ScanState.risk_score >= 40,
                                        "shield",
                                        "shield-check",
                                    ),
                                ),
                                class_name=rx.cond(
                                    ScanState.risk_score >= 70,
                                    "h-12 w-12 text-red-500",
                                    rx.cond(
                                        ScanState.risk_score >= 40,
                                        "h-12 w-12 text-yellow-500",
                                        "h-12 w-12 text-green-500",
                                    ),
                                ),
                            ),
                        ),
                        class_name="flex items-start justify-between",
                    ),
                    rx.el.div(
                        rx.el.div(
                            class_name=rx.cond(
                                ScanState.risk_score >= 70,
                                "h-2 rounded-full bg-red-500",
                                rx.cond(
                                    ScanState.risk_score >= 40,
                                    "h-2 rounded-full bg-yellow-500",
                                    "h-2 rounded-full bg-green-500",
                                ),
                            ),
                            custom_attrs={
                                "style": {
                                    "width": ScanState.risk_score.to_string()
                                    + "%"
                                }
                            },
                        ),
                        class_name="w-full h-2 rounded-full bg-gray-100 mt-4",
                    ),
                    rx.cond(
                        ScanState.categories.length() > 0,
                        rx.el.div(
                            rx.foreach(
                                ScanState.categories,
                                lambda c: rx.el.span(
                                    c,
                                    class_name="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-orange-50 text-[#E8471A] border border-orange-200",
                                ),
                            ),
                            class_name="flex flex-wrap gap-2 mt-4",
                        ),
                        rx.fragment(),
                    ),
                    class_name="mt-4",
                ),
                rx.cond(
                    ScanState.summary != "",
                    card(
                        rx.el.div(
                            rx.icon(
                                "sparkles", class_name="h-4 w-4 text-[#E8471A]"
                            ),
                            rx.el.h4(
                                "AI Summary",
                                class_name="text-sm font-semibold text-gray-900",
                            ),
                            class_name="flex items-center gap-2 mb-2",
                        ),
                        rx.el.p(
                            ScanState.summary,
                            class_name="text-sm text-gray-800 leading-relaxed font-medium",
                        ),
                        class_name="mt-4 bg-gradient-to-br from-orange-50/40 to-white",
                    ),
                    rx.fragment(),
                ),
                _why_flagged_card(),
                _highlighted_message_card(),
                card(
                    rx.el.h4(
                        "Detailed Explanation",
                        class_name="text-sm font-semibold text-gray-900 mb-2",
                    ),
                    rx.el.p(
                        ScanState.explanation,
                        class_name="text-sm text-gray-700 leading-relaxed",
                    ),
                    class_name="mt-4",
                ),
                rx.cond(
                    ScanState.keywords.length() > 0,
                    card(
                        rx.el.div(
                            rx.icon(
                                "highlighter",
                                class_name="h-4 w-4 text-[#E8471A]",
                            ),
                            rx.el.h4(
                                "Suspicious Keywords",
                                class_name="text-sm font-semibold text-gray-900",
                            ),
                            class_name="flex items-center gap-2 mb-3",
                        ),
                        rx.el.div(
                            rx.foreach(
                                ScanState.keywords,
                                lambda k: rx.el.div(
                                    rx.el.div(
                                        rx.el.span(
                                            k["term"],
                                            class_name="text-xs font-mono font-bold text-gray-900",
                                        ),
                                        rx.el.span(
                                            k["risk"].upper(),
                                            class_name=rx.match(
                                                k["risk"],
                                                (
                                                    "high",
                                                    "px-1.5 py-0.5 rounded text-[9px] font-bold bg-red-100 text-red-700",
                                                ),
                                                (
                                                    "medium",
                                                    "px-1.5 py-0.5 rounded text-[9px] font-bold bg-yellow-100 text-yellow-700",
                                                ),
                                                "px-1.5 py-0.5 rounded text-[9px] font-bold bg-blue-100 text-blue-700",
                                            ),
                                        ),
                                        class_name="flex items-center gap-2",
                                    ),
                                    rx.el.p(
                                        k["reason"],
                                        class_name="text-[11px] text-gray-600 mt-1",
                                    ),
                                    class_name=rx.match(
                                        k["risk"],
                                        (
                                            "high",
                                            "p-2.5 rounded-lg border border-red-200 bg-red-50/40",
                                        ),
                                        (
                                            "medium",
                                            "p-2.5 rounded-lg border border-yellow-200 bg-yellow-50/40",
                                        ),
                                        "p-2.5 rounded-lg border border-blue-200 bg-blue-50/40",
                                    ),
                                ),
                            ),
                            class_name="grid grid-cols-1 sm:grid-cols-2 gap-2",
                        ),
                        class_name="mt-4",
                    ),
                    rx.fragment(),
                ),
                threat_breakdown_card_inline(),
                rx.el.div(
                    card(
                        rx.el.div(
                            rx.icon("flag", class_name="h-4 w-4 text-red-500"),
                            rx.el.h4(
                                "Red Flags",
                                class_name="text-sm font-semibold text-gray-900",
                            ),
                            class_name="flex items-center gap-2 mb-3",
                        ),
                        rx.el.ul(
                            rx.foreach(
                                ScanState.red_flags,
                                lambda f: rx.el.li(
                                    rx.icon(
                                        "dot",
                                        class_name="h-4 w-4 text-red-500 shrink-0 mt-0.5",
                                    ),
                                    rx.el.span(
                                        f, class_name="text-sm text-gray-700"
                                    ),
                                    class_name="flex items-start gap-1",
                                ),
                            ),
                            class_name="space-y-2",
                        ),
                    ),
                    card(
                        rx.el.div(
                            rx.icon(
                                "circle-check",
                                class_name="h-4 w-4 text-green-500",
                            ),
                            rx.el.h4(
                                "Recommended Actions",
                                class_name="text-sm font-semibold text-gray-900",
                            ),
                            class_name="flex items-center gap-2 mb-3",
                        ),
                        rx.el.ul(
                            rx.foreach(
                                ScanState.actions,
                                lambda a: rx.el.li(
                                    rx.icon(
                                        "dot",
                                        class_name="h-4 w-4 text-green-500 shrink-0 mt-0.5",
                                    ),
                                    rx.el.span(
                                        a, class_name="text-sm text-gray-700"
                                    ),
                                    class_name="flex items-start gap-1",
                                ),
                            ),
                            class_name="space-y-2",
                        ),
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4",
                ),
                rx.cond(
                    ScanState.checklist.length() > 0,
                    card(
                        rx.el.div(
                            rx.icon(
                                "list-checks",
                                class_name="h-4 w-4 text-[#E8471A]",
                            ),
                            rx.el.h4(
                                "Safety Checklist",
                                class_name="text-sm font-semibold text-gray-900",
                            ),
                            class_name="flex items-center gap-2 mb-3",
                        ),
                        rx.el.div(
                            rx.foreach(
                                ScanState.checklist,
                                lambda c: rx.el.div(
                                    rx.el.div(
                                        rx.icon(
                                            "check",
                                            class_name="h-3 w-3 text-white",
                                        ),
                                        class_name="h-5 w-5 rounded-md bg-[#E8471A] flex items-center justify-center shrink-0",
                                    ),
                                    rx.el.p(
                                        c,
                                        class_name="text-sm text-gray-800 font-medium",
                                    ),
                                    class_name="flex items-start gap-2 p-3 rounded-xl border border-orange-100 bg-orange-50/30 hover:bg-orange-50 transition-colors",
                                ),
                            ),
                            class_name="grid grid-cols-1 sm:grid-cols-2 gap-2",
                        ),
                        class_name="mt-4",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    ScanState.entities.length() > 0,
                    card(
                        rx.el.div(
                            rx.icon("tag", class_name="h-4 w-4 text-blue-500"),
                            rx.el.h4(
                                "Detected Entities",
                                class_name="text-sm font-semibold text-gray-900",
                            ),
                            class_name="flex items-center gap-2 mb-3",
                        ),
                        rx.el.div(
                            rx.foreach(
                                ScanState.entities,
                                lambda e: rx.el.span(
                                    e,
                                    class_name="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-mono bg-gray-100 text-gray-800 border border-gray-200",
                                ),
                            ),
                            class_name="flex flex-wrap gap-2",
                        ),
                        class_name="mt-4",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    ScanState.risk_score >= 70,
                    card(
                        rx.el.div(
                            rx.icon(
                                "phone-call",
                                class_name="h-5 w-5 text-[#E8471A]",
                            ),
                            rx.el.h4(
                                "Take action now",
                                class_name="text-sm font-semibold text-gray-900",
                            ),
                            class_name="flex items-center gap-2 mb-2",
                        ),
                        rx.el.p(
                            "This appears to be a high-risk scam. Report it immediately.",
                            class_name="text-sm text-gray-600 mb-3",
                        ),
                        rx.el.div(
                            rx.el.a(
                                "Call 1930",
                                href="tel:1930",
                                class_name="px-4 py-2 rounded-lg bg-[#E8471A] text-white text-sm font-medium",
                            ),
                            rx.el.a(
                                "Report Online",
                                href="https://cybercrime.gov.in",
                                target="_blank",
                                class_name="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 text-sm font-medium hover:bg-gray-50",
                            ),
                            class_name="flex gap-2",
                        ),
                        class_name="mt-4 border-orange-200 bg-orange-50",
                    ),
                    rx.fragment(),
                ),
            ),
            rx.fragment(),
        ),
    )


def analyze_page() -> rx.Component:
    return app_layout(
        analyze_content(), "Analyze", "Run AI-powered fraud detection"
    )


def history_content() -> rx.Component:
    return rx.el.div(
        card(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400",
                    ),
                    rx.el.input(
                        placeholder="Search scans, categories, summaries...",
                        default_value=ScanState.search_query,
                        on_change=ScanState.set_search.debounce(200),
                        class_name="w-full pl-10 pr-3 py-2 rounded-lg border border-gray-300 bg-white text-sm focus:outline-hidden focus:ring-2 focus:ring-[#E8471A]",
                    ),
                    class_name="relative flex-1",
                ),
                rx.el.select(
                    rx.foreach(
                        ["All", "SAFE", "MEDIUM", "HIGH"],
                        lambda v: rx.el.option(v, value=v),
                    ),
                    value=ScanState.filter_verdict,
                    on_change=ScanState.set_filter_verdict,
                    class_name="px-3 py-2 rounded-lg border border-gray-300 bg-white text-sm focus:outline-hidden focus:ring-2 focus:ring-[#E8471A] appearance-none",
                ),
                rx.el.select(
                    rx.el.option("Newest first", value="newest"),
                    rx.el.option("Oldest first", value="oldest"),
                    rx.el.option("Highest risk", value="risk_desc"),
                    rx.el.option("Lowest risk", value="risk_asc"),
                    value=ScanState.sort_by,
                    on_change=ScanState.set_sort_by,
                    class_name="px-3 py-2 rounded-lg border border-gray-300 bg-white text-sm focus:outline-hidden focus:ring-2 focus:ring-[#E8471A] appearance-none",
                ),
                rx.el.button(
                    rx.icon("download", class_name="h-3.5 w-3.5"),
                    rx.el.span(
                        "Export CSV", class_name="text-xs font-semibold"
                    ),
                    on_click=ScanState.export_csv,
                    class_name="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-[#E8471A] text-white hover:bg-[#c43a13] transition-colors",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="h-3.5 w-3.5"),
                    rx.el.span("Clear", class_name="text-xs font-semibold"),
                    on_click=ScanState.clear_history,
                    class_name="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition-colors",
                ),
                class_name="flex flex-wrap gap-2",
            ),
        ),
        rx.cond(
            ScanState.filtered_history.length() > 0,
            rx.el.div(
                rx.foreach(
                    ScanState.filtered_history,
                    lambda h: card(
                        rx.el.div(
                            rx.el.div(
                                verdict_badge(h["verdict"]),
                                rx.el.p(
                                    h["timestamp"],
                                    class_name="text-xs text-gray-500",
                                ),
                                rx.el.span(
                                    h["input_type"].upper(),
                                    class_name="text-xs text-gray-400 uppercase",
                                ),
                                class_name="flex items-center gap-3 flex-wrap",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    "Risk " + h["risk_score"].to_string() + "%",
                                    class_name="text-sm font-semibold text-gray-900",
                                ),
                                rx.el.span(
                                    "·",
                                    class_name="text-xs text-gray-300",
                                ),
                                rx.el.p(
                                    "Conf " + h["confidence"].to_string() + "%",
                                    class_name="text-xs text-gray-500 font-medium",
                                ),
                                class_name="flex items-center gap-2",
                            ),
                            class_name="flex items-center justify-between gap-2 flex-wrap",
                        ),
                        rx.cond(
                            h["categories"].length() > 0,
                            rx.el.div(
                                rx.foreach(
                                    h["categories"],
                                    lambda c: rx.el.span(
                                        c,
                                        class_name="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-orange-50 text-[#E8471A] border border-orange-200",
                                    ),
                                ),
                                class_name="flex flex-wrap gap-1.5 mt-2",
                            ),
                            rx.fragment(),
                        ),
                        rx.el.p(
                            h["input_text"],
                            class_name="text-sm text-gray-700 mt-3 line-clamp-2",
                        ),
                        rx.cond(
                            h["summary"] != "",
                            rx.el.p(
                                h["summary"],
                                class_name="text-xs text-gray-600 mt-2 italic line-clamp-2",
                            ),
                            rx.el.p(
                                h["explanation"],
                                class_name="text-xs text-gray-500 mt-2 line-clamp-2",
                            ),
                        ),
                        rx.el.div(
                            rx.el.button(
                                rx.icon("download", class_name="h-3 w-3"),
                                rx.el.span(
                                    "Report",
                                    class_name="text-[11px] font-semibold",
                                ),
                                on_click=lambda: ScanState.export_report(
                                    h["id"]
                                ),
                                class_name="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-gray-200 text-gray-700 hover:bg-orange-50 hover:border-orange-300 transition-colors",
                            ),
                            rx.el.button(
                                rx.icon("trash-2", class_name="h-3 w-3"),
                                rx.el.span(
                                    "Delete",
                                    class_name="text-[11px] font-semibold",
                                ),
                                on_click=lambda: ScanState.delete_record(
                                    h["id"]
                                ),
                                class_name="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition-colors",
                            ),
                            class_name="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100",
                        ),
                        class_name="hover:border-orange-300 transition-colors",
                    ),
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4",
            ),
            card(
                rx.el.div(
                    rx.icon(
                        "inbox", class_name="h-10 w-10 text-gray-300 mx-auto"
                    ),
                    rx.el.p(
                        "No scans found",
                        class_name="text-sm text-gray-500 mt-2 text-center",
                    ),
                    rx.el.a(
                        "Run your first scan",
                        href="/analyze",
                        class_name="block text-sm text-[#E8471A] hover:underline text-center mt-1",
                    ),
                    class_name="py-8",
                ),
                class_name="mt-4",
            ),
        ),
    )


def history_page() -> rx.Component:
    return app_layout(history_content(), "History", "Review your past scans")


def _assistant_quick_chip(icon: str, label: str, prompt: str) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, class_name="h-3.5 w-3.5"),
        rx.el.span(label, class_name="text-xs font-semibold"),
        on_click=lambda: rx.set_value("chat-input", prompt),
        class_name="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-gray-200 bg-white text-gray-700 hover:border-orange-300 hover:bg-orange-50 hover:text-[#E8471A] transition-colors",
    )


def _assistant_escalation_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("phone-call", class_name="h-4 w-4 text-red-600"),
            rx.el.p(
                "Need urgent help?",
                class_name="text-sm font-bold text-gray-900",
            ),
            class_name="flex items-center gap-2 mb-2",
        ),
        rx.el.p(
            "If you've already shared OTP, money or sensitive info, escalate immediately.",
            class_name="text-xs text-gray-600 leading-relaxed",
        ),
        rx.el.div(
            rx.el.a(
                rx.icon("phone", class_name="h-3.5 w-3.5"),
                rx.el.span("Call 1930", class_name="text-xs font-bold"),
                href="tel:1930",
                class_name="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-500 text-white hover:bg-red-600",
            ),
            rx.el.a(
                rx.icon("external-link", class_name="h-3.5 w-3.5"),
                rx.el.span("Report Online", class_name="text-xs font-bold"),
                href="https://cybercrime.gov.in",
                target="_blank",
                class_name="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-red-200 text-red-700 hover:bg-red-50",
            ),
            class_name="flex items-center gap-2 mt-3",
        ),
        class_name="rounded-2xl border border-red-200 bg-gradient-to-br from-red-50 to-white p-4",
    )


def _assistant_context_card() -> rx.Component:
    return rx.cond(
        ScanState.has_result,
        rx.el.div(
            rx.el.div(
                rx.icon("scan-search", class_name="h-4 w-4 text-[#E8471A]"),
                rx.el.p(
                    "Last scan context",
                    class_name="text-xs font-bold text-gray-900",
                ),
                rx.el.span(
                    ScanState.verdict,
                    class_name=rx.match(
                        ScanState.verdict,
                        (
                            "HIGH",
                            "ml-auto px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-700",
                        ),
                        (
                            "MEDIUM",
                            "ml-auto px-2 py-0.5 rounded-full text-[10px] font-bold bg-yellow-100 text-yellow-700",
                        ),
                        (
                            "SAFE",
                            "ml-auto px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-green-700",
                        ),
                        "ml-auto px-2 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-700",
                    ),
                ),
                class_name="flex items-center gap-2 mb-2",
            ),
            rx.el.p(
                ScanState.summary,
                class_name="text-xs text-gray-700 leading-relaxed line-clamp-3",
            ),
            rx.el.button(
                rx.icon("sparkles", class_name="h-3 w-3"),
                rx.el.span(
                    "Ask AI about this scan", class_name="text-[11px] font-bold"
                ),
                on_click=lambda: rx.set_value(
                    "chat-input",
                    "Explain this scan result in simple terms and tell me what to do next: "
                    + ScanState.summary,
                ),
                class_name="inline-flex items-center gap-1.5 mt-3 px-3 py-1.5 rounded-lg bg-[#E8471A] text-white hover:bg-[#c43a13]",
            ),
            class_name="rounded-2xl border border-orange-200 bg-gradient-to-br from-orange-50 to-white p-4",
        ),
        rx.fragment(),
    )


def assistant_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                _assistant_context_card(),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "sparkles", class_name="h-4 w-4 text-white"
                            ),
                            class_name="h-9 w-9 rounded-xl bg-gradient-to-br from-[#E8471A] to-[#c43a13] flex items-center justify-center shadow-md",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "FraudRadar AI",
                                class_name="text-sm font-bold text-gray-900",
                            ),
                            rx.el.p(
                                "Powered by Groq · India scam expert",
                                class_name="text-[11px] text-gray-500",
                            ),
                        ),
                        class_name="flex items-center gap-2.5",
                    ),
                    rx.el.div(
                        rx.el.div(
                            class_name="h-2 w-2 rounded-full bg-green-500 animate-pulse"
                        ),
                        rx.el.span(
                            "Online",
                            class_name="text-[11px] font-bold text-green-700",
                        ),
                        class_name="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-50 border border-green-200",
                    ),
                    class_name="flex items-center justify-between mb-3",
                ),
                rx.cond(
                    AssistantState.messages.length() == 0,
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "message-circle-question",
                                class_name="h-7 w-7 text-[#E8471A]",
                            ),
                            class_name="h-14 w-14 rounded-2xl bg-orange-50 border border-orange-100 flex items-center justify-center mx-auto",
                        ),
                        rx.el.h3(
                            "How can I help you stay safe?",
                            class_name="text-lg font-bold text-gray-900 mt-4 text-center",
                        ),
                        rx.el.p(
                            "Ask about suspicious messages, scam patterns, or how to report fraud.",
                            class_name="text-sm text-gray-500 text-center mt-1 max-w-md mx-auto",
                        ),
                        rx.el.div(
                            _assistant_quick_chip(
                                "indian-rupee",
                                "UPI fraud",
                                "Explain common UPI fraud tactics in India and how to spot them.",
                            ),
                            _assistant_quick_chip(
                                "key",
                                "OTP scam",
                                "Someone is asking for my OTP claiming to be from my bank — what should I do?",
                            ),
                            _assistant_quick_chip(
                                "link",
                                "Phishing link",
                                "How can I tell if a link is a phishing attempt?",
                            ),
                            _assistant_quick_chip(
                                "shield-alert",
                                "Report scam",
                                "How do I report a scam to cybercrime.gov.in step by step?",
                            ),
                            _assistant_quick_chip(
                                "briefcase",
                                "Job scam",
                                "Is this job offer a scam? It asks for a registration fee.",
                            ),
                            _assistant_quick_chip(
                                "phone-call",
                                "Caller verify",
                                "How do I verify if a caller is really from my bank?",
                            ),
                            class_name="flex flex-wrap items-center justify-center gap-2 mt-5",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Or pick a guided prompt:",
                                class_name="text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-2 text-center",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    AssistantState.suggested_prompts,
                                    lambda p: rx.el.button(
                                        rx.icon(
                                            "sparkles",
                                            class_name="h-3.5 w-3.5 text-[#E8471A] shrink-0",
                                        ),
                                        rx.el.span(
                                            p,
                                            class_name="text-sm text-gray-700 text-left",
                                        ),
                                        on_click=lambda: rx.set_value("chat-input", p),
                                        class_name="flex items-start gap-2 p-3 rounded-xl border border-gray-200 bg-white hover:border-[#E8471A] hover:bg-orange-50 transition-colors text-left w-full",
                                    ),
                                ),
                                class_name="grid grid-cols-1 md:grid-cols-2 gap-2",
                            ),
                            class_name="mt-6",
                        ),
                        class_name="py-6",
                    ),
                    rx.el.div(
                        rx.foreach(
                            AssistantState.messages,
                            lambda m: rx.el.div(
                                rx.cond(
                                    m["role"] == "assistant",
                                    rx.el.div(
                                        rx.icon(
                                            "sparkles",
                                            class_name="h-3.5 w-3.5 text-white",
                                        ),
                                        class_name="h-7 w-7 rounded-lg bg-gradient-to-br from-[#E8471A] to-[#c43a13] flex items-center justify-center shrink-0",
                                    ),
                                    rx.fragment(),
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        m["content"],
                                        class_name="text-sm whitespace-pre-wrap leading-relaxed",
                                    ),
                                    class_name=rx.cond(
                                        m["role"] == "user",
                                        "max-w-[75%] px-4 py-2.5 rounded-2xl bg-gradient-to-r from-[#E8471A] to-[#c43a13] text-white shadow-md",
                                        "max-w-[75%] px-4 py-2.5 rounded-2xl bg-gray-100 text-gray-900",
                                    ),
                                ),
                                class_name=rx.cond(
                                    m["role"] == "user",
                                    "flex justify-end gap-2",
                                    "flex justify-start gap-2 items-start",
                                ),
                            ),
                        ),
                        rx.cond(
                            AssistantState.is_thinking,
                            rx.el.div(
                                rx.el.div(
                                    rx.icon(
                                        "sparkles",
                                        class_name="h-3.5 w-3.5 text-white",
                                    ),
                                    class_name="h-7 w-7 rounded-lg bg-gradient-to-br from-[#E8471A] to-[#c43a13] flex items-center justify-center shrink-0",
                                ),
                                rx.el.div(
                                    rx.icon(
                                        "loader-circle",
                                        class_name="h-4 w-4 animate-spin text-gray-500",
                                    ),
                                    rx.el.span(
                                        "Analyzing...",
                                        class_name="text-sm text-gray-500",
                                    ),
                                    class_name="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-gray-100",
                                ),
                                class_name="flex justify-start gap-2 items-start",
                            ),
                            rx.fragment(),
                        ),
                        id="chat-messages",
                        class_name="space-y-3 max-h-[55vh] overflow-y-auto pr-1",
                    ),
                ),
                class_name="bg-white border border-gray-200 rounded-2xl p-5",
            ),
            rx.el.form(
                rx.el.div(
                    rx.icon(
                        "message-circle",
                        class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400",
                    ),
                    rx.el.input(
                        id="chat-input",
                        name="message",
                        placeholder="Ask about a suspicious message, link, or scam...",
                        auto_complete="off",
                        class_name="w-full pl-10 pr-3 py-3 rounded-xl border border-gray-300 bg-white text-sm focus:outline-hidden focus:ring-2 focus:ring-[#E8471A] focus:border-transparent",
                    ),
                    class_name="relative flex-1",
                ),
                rx.el.button(
                    rx.icon("send", class_name="h-4 w-4"),
                    type="submit",
                    disabled=AssistantState.is_thinking,
                    class_name="px-4 py-3 rounded-xl bg-[#E8471A] text-white hover:bg-[#c43a13] disabled:opacity-50 transition-colors",
                ),
                rx.el.button(
                    rx.icon("refresh-cw", class_name="h-4 w-4"),
                    type="button",
                    on_click=AssistantState.clear_chat,
                    title="Clear chat",
                    class_name="px-3 py-3 rounded-xl border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors",
                ),
                on_submit=AssistantState.send_message,
                class_name="flex items-center gap-2 mt-3",
            ),
            rx.el.div(
                rx.icon("shield-check", class_name="h-3 w-3 text-green-600"),
                rx.el.span(
                    "Conversations are private. AI may make mistakes—verify critical actions through official channels.",
                    class_name="text-[11px] text-gray-500 font-medium",
                ),
                class_name="flex items-start gap-1.5 mt-2",
            ),
            class_name="lg:col-span-2",
        ),
        rx.el.div(
            _assistant_escalation_card(),
            rx.el.div(
                rx.el.div(
                    rx.icon("lightbulb", class_name="h-4 w-4 text-yellow-500"),
                    rx.el.p(
                        "Quick safety reminders",
                        class_name="text-sm font-bold text-gray-900",
                    ),
                    class_name="flex items-center gap-2 mb-3",
                ),
                rx.el.div(
                    *[
                        rx.el.div(
                            rx.icon(
                                "check",
                                class_name="h-3 w-3 text-green-600 shrink-0 mt-0.5",
                            ),
                            rx.el.p(
                                t,
                                class_name="text-xs text-gray-700 leading-relaxed",
                            ),
                            class_name="flex items-start gap-2",
                        )
                        for t in [
                            "Never share OTP, PIN, or CVV — even with bank officials.",
                            "Verify caller identity by calling back the official number.",
                            "Don't click unknown links from SMS or WhatsApp.",
                            "Report suspicious activity to 1930 within 24 hours.",
                            "Save evidence (screenshots) before deleting fraud messages.",
                        ]
                    ],
                    class_name="flex flex-col gap-2",
                ),
                class_name="rounded-2xl border border-yellow-200 bg-gradient-to-br from-yellow-50 to-white p-4 mt-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("phone", class_name="h-4 w-4 text-blue-600"),
                    rx.el.p(
                        "Official channels",
                        class_name="text-sm font-bold text-gray-900",
                    ),
                    class_name="flex items-center gap-2 mb-3",
                ),
                rx.el.div(
                    rx.el.a(
                        rx.el.span(
                            "Helpline 1930",
                            class_name="text-xs font-semibold text-gray-900",
                        ),
                        rx.icon("phone", class_name="h-3 w-3 text-gray-500"),
                        href="tel:1930",
                        class_name="flex items-center justify-between p-2.5 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50/40",
                    ),
                    rx.el.a(
                        rx.el.span(
                            "cybercrime.gov.in",
                            class_name="text-xs font-semibold text-gray-900",
                        ),
                        rx.icon(
                            "external-link", class_name="h-3 w-3 text-gray-500"
                        ),
                        href="https://cybercrime.gov.in",
                        target="_blank",
                        class_name="flex items-center justify-between p-2.5 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50/40",
                    ),
                    rx.el.a(
                        rx.el.span(
                            "Sancharsaathi",
                            class_name="text-xs font-semibold text-gray-900",
                        ),
                        rx.icon(
                            "external-link", class_name="h-3 w-3 text-gray-500"
                        ),
                        href="https://sancharsaathi.gov.in",
                        target="_blank",
                        class_name="flex items-center justify-between p-2.5 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50/40",
                    ),
                    class_name="flex flex-col gap-2",
                ),
                class_name="rounded-2xl border border-gray-200 bg-white p-4 mt-4",
            ),
            class_name="lg:col-span-1",
        ),
        class_name="grid grid-cols-1 lg:grid-cols-3 gap-4",
    )


def assistant_page() -> rx.Component:
    return app_layout(
        assistant_content(), "Assistant", "AI-guided scam safety help"
    )


def _profile_stat(label: str, value, icon: str, accent: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"h-4 w-4 {accent}"),
            class_name="h-9 w-9 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-center",
        ),
        rx.el.div(
            rx.el.p(
                value,
                class_name="text-xl font-extrabold text-gray-900",
            ),
            rx.el.p(
                label,
                class_name="text-[11px] font-semibold text-gray-500 uppercase tracking-wider",
            ),
        ),
        class_name="flex items-center gap-3 p-3 rounded-xl border border-gray-100 bg-white",
    )


def profile_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.img(
                            src=f"https://api.dicebear.com/9.x/notionists/svg?seed={ProfileState.avatar_seed}",
                            class_name="h-20 w-20 rounded-2xl bg-orange-50 border-2 border-white shadow-md",
                        ),
                        rx.el.div(
                            rx.icon(
                                "shield-check", class_name="h-3 w-3 text-white"
                            ),
                            class_name="absolute -bottom-1 -right-1 h-6 w-6 rounded-full bg-green-500 border-2 border-white flex items-center justify-center",
                        ),
                        class_name="relative",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.h2(
                                AuthState.user_name,
                                class_name="text-xl font-bold text-gray-900",
                            ),
                            rx.el.span(
                                "Verified",
                                class_name="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-50 text-green-700 border border-green-200",
                            ),
                            class_name="flex items-center gap-2 flex-wrap",
                        ),
                        rx.el.div(
                            rx.icon(
                                "mail", class_name="h-3.5 w-3.5 text-gray-400"
                            ),
                            rx.el.p(
                                AuthState.user_email,
                                class_name="text-sm text-gray-600",
                            ),
                            class_name="flex items-center gap-1.5 mt-1",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.icon(
                                    "calendar",
                                    class_name="h-3 w-3 text-gray-400",
                                ),
                                rx.el.span(
                                    "Joined ",
                                    class_name="text-[11px] text-gray-500",
                                ),
                                rx.el.span(
                                    ProfileState.joined_date,
                                    class_name="text-[11px] font-semibold text-gray-700",
                                ),
                                class_name="inline-flex items-center gap-1",
                            ),
                            rx.el.span(class_name="h-3 w-px bg-gray-300"),
                            rx.el.div(
                                rx.icon(
                                    "map-pin",
                                    class_name="h-3 w-3 text-gray-400",
                                ),
                                rx.el.span(
                                    ProfileState.location,
                                    class_name="text-[11px] font-semibold text-gray-700",
                                ),
                                class_name="inline-flex items-center gap-1",
                            ),
                            class_name="flex items-center gap-2 mt-2 flex-wrap",
                        ),
                    ),
                    class_name="flex items-start gap-4",
                ),
                rx.el.div(
                    rx.el.a(
                        rx.icon("settings", class_name="h-3.5 w-3.5"),
                        rx.el.span(
                            "Settings", class_name="text-xs font-semibold"
                        ),
                        href="/settings",
                        class_name="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-gray-200 bg-white hover:bg-gray-50",
                    ),
                    rx.el.button(
                        rx.icon("log-out", class_name="h-3.5 w-3.5"),
                        rx.el.span(
                            "Sign Out", class_name="text-xs font-semibold"
                        ),
                        on_click=AuthState.logout,
                        class_name="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-red-200 text-red-600 hover:bg-red-50",
                    ),
                    class_name="flex items-center gap-2",
                ),
                class_name="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4",
            ),
            class_name="bg-gradient-to-br from-orange-50/40 via-white to-white border border-gray-200 rounded-2xl p-5",
        ),
        rx.el.div(
            _profile_stat(
                "Total Scans",
                ScanState.total_scans.to_string(),
                "scan-search",
                "text-[#E8471A]",
            ),
            _profile_stat(
                "Scams Detected",
                ScanState.scams_detected.to_string(),
                "shield-alert",
                "text-red-500",
            ),
            _profile_stat(
                "Avg Risk",
                f"{ScanState.avg_risk:.1f}%",
                "trending-up",
                "text-yellow-600",
            ),
            _profile_stat(
                "Security Score",
                "85",
                "shield-check",
                "text-green-600",
            ),
            class_name="grid grid-cols-2 lg:grid-cols-4 gap-3 mt-4",
        ),
        rx.el.div(
            rx.el.div(
                card(
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "user-cog", class_name="h-4 w-4 text-[#E8471A]"
                            ),
                            rx.el.h3(
                                "Personal Information",
                                class_name="text-base font-bold text-gray-900",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        rx.el.span(
                            "Editable",
                            class_name="text-[10px] font-bold text-gray-500 uppercase tracking-wider",
                        ),
                        class_name="flex items-center justify-between mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Full Name",
                                class_name="block text-xs font-bold text-gray-700 mb-1.5 uppercase tracking-wider",
                            ),
                            rx.el.div(
                                rx.icon(
                                    "user",
                                    class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400",
                                ),
                                rx.el.input(
                                    default_value=ProfileState.full_name,
                                    on_change=ProfileState.set_full_name.debounce(
                                        200
                                    ),
                                    class_name="w-full pl-9 pr-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm focus:outline-hidden focus:ring-2 focus:ring-[#E8471A]",
                                ),
                                class_name="relative",
                            ),
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Phone",
                                class_name="block text-xs font-bold text-gray-700 mb-1.5 uppercase tracking-wider",
                            ),
                            rx.el.div(
                                rx.icon(
                                    "phone",
                                    class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400",
                                ),
                                rx.el.input(
                                    placeholder="+91 98765 43210",
                                    default_value=ProfileState.phone,
                                    on_change=ProfileState.set_phone.debounce(
                                        200
                                    ),
                                    class_name="w-full pl-9 pr-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm focus:outline-hidden focus:ring-2 focus:ring-[#E8471A]",
                                ),
                                class_name="relative",
                            ),
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Location",
                                class_name="block text-xs font-bold text-gray-700 mb-1.5 uppercase tracking-wider",
                            ),
                            rx.el.div(
                                rx.icon(
                                    "map-pin",
                                    class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400",
                                ),
                                rx.el.input(
                                    default_value=ProfileState.location,
                                    on_change=ProfileState.set_location.debounce(
                                        200
                                    ),
                                    class_name="w-full pl-9 pr-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm focus:outline-hidden focus:ring-2 focus:ring-[#E8471A]",
                                ),
                                class_name="relative",
                            ),
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Email",
                                class_name="block text-xs font-bold text-gray-700 mb-1.5 uppercase tracking-wider",
                            ),
                            rx.el.div(
                                rx.icon(
                                    "mail",
                                    class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400",
                                ),
                                rx.el.input(
                                    default_value=AuthState.user_email,
                                    disabled=True,
                                    class_name="w-full pl-9 pr-3 py-2.5 rounded-lg border border-gray-200 bg-gray-50 text-sm text-gray-600 cursor-not-allowed",
                                ),
                                class_name="relative",
                            ),
                            rx.el.p(
                                "Email cannot be changed.",
                                class_name="text-[10px] text-gray-500 mt-1",
                            ),
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Bio",
                                class_name="block text-xs font-bold text-gray-700 mb-1.5 uppercase tracking-wider",
                            ),
                            rx.el.textarea(
                                placeholder="A short note about you...",
                                default_value=ProfileState.bio,
                                on_change=ProfileState.set_bio.debounce(200),
                                class_name="w-full px-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm min-h-[90px] focus:outline-hidden focus:ring-2 focus:ring-[#E8471A]",
                            ),
                            class_name="md:col-span-2",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.icon("save", class_name="h-3.5 w-3.5"),
                            rx.el.span(
                                "Save Changes", class_name="text-xs font-bold"
                            ),
                            on_click=ProfileState.save_profile,
                            class_name="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#E8471A] text-white hover:bg-[#c43a13] transition-colors",
                        ),
                        rx.el.button(
                            rx.icon("rotate-ccw", class_name="h-3.5 w-3.5"),
                            rx.el.span("Reset", class_name="text-xs font-bold"),
                            on_click=ProfileState.reset_profile,
                            class_name="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors",
                        ),
                        class_name="flex gap-2 mt-4",
                    ),
                    rx.cond(
                        ProfileState.save_message != "",
                        rx.el.div(
                            rx.icon(
                                "circle-check",
                                class_name="h-3.5 w-3.5 text-green-600",
                            ),
                            rx.el.p(
                                ProfileState.save_message,
                                class_name="text-xs font-semibold text-green-700",
                            ),
                            class_name="flex items-center gap-1.5 mt-3 p-2.5 rounded-lg bg-green-50 border border-green-200",
                        ),
                        rx.fragment(),
                    ),
                ),
                class_name="lg:col-span-2",
            ),
            rx.el.div(
                card(
                    rx.el.div(
                        rx.icon(
                            "activity", class_name="h-4 w-4 text-[#E8471A]"
                        ),
                        rx.el.h3(
                            "Recent Activity",
                            class_name="text-base font-bold text-gray-900",
                        ),
                        class_name="flex items-center gap-2 mb-3",
                    ),
                    rx.cond(
                        ScanState.history.length() > 0,
                        rx.el.div(
                            rx.foreach(
                                ScanState.history[:5],
                                lambda h: rx.el.div(
                                    rx.el.div(
                                        class_name=rx.match(
                                            h["verdict"],
                                            (
                                                "HIGH",
                                                "h-2 w-2 rounded-full bg-red-500 shrink-0",
                                            ),
                                            (
                                                "MEDIUM",
                                                "h-2 w-2 rounded-full bg-yellow-500 shrink-0",
                                            ),
                                            (
                                                "SAFE",
                                                "h-2 w-2 rounded-full bg-green-500 shrink-0",
                                            ),
                                            "h-2 w-2 rounded-full bg-gray-400 shrink-0",
                                        ),
                                    ),
                                    rx.el.div(
                                        rx.el.p(
                                            h["input_text"],
                                            class_name="text-xs font-semibold text-gray-900 line-clamp-1",
                                        ),
                                        rx.el.div(
                                            rx.el.span(
                                                h["verdict"],
                                                class_name="text-[10px] font-bold text-gray-500",
                                            ),
                                            rx.el.span(
                                                "·",
                                                class_name="text-[10px] text-gray-300",
                                            ),
                                            rx.el.span(
                                                h["timestamp"],
                                                class_name="text-[10px] text-gray-400",
                                            ),
                                            class_name="flex items-center gap-1.5 mt-0.5",
                                        ),
                                    ),
                                    class_name="flex items-start gap-2 py-2 border-b border-gray-100 last:border-0",
                                ),
                            ),
                        ),
                        rx.el.div(
                            rx.icon(
                                "inbox",
                                class_name="h-6 w-6 text-gray-300 mx-auto",
                            ),
                            rx.el.p(
                                "No recent scans",
                                class_name="text-xs text-gray-500 text-center mt-2",
                            ),
                            class_name="py-4",
                        ),
                    ),
                    rx.el.a(
                        rx.el.span("View all history"),
                        rx.icon("arrow-right", class_name="h-3 w-3"),
                        href="/history",
                        class_name="flex items-center justify-center gap-1 mt-3 px-3 py-2 rounded-lg border border-gray-200 text-xs font-semibold text-[#E8471A] hover:bg-orange-50",
                    ),
                ),
                card(
                    rx.el.div(
                        rx.icon("award", class_name="h-4 w-4 text-[#E8471A]"),
                        rx.el.h3(
                            "Account Health",
                            class_name="text-base font-bold text-gray-900",
                        ),
                        class_name="flex items-center gap-2 mb-3",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                "Email verified",
                                class_name="text-xs text-gray-700 flex-1",
                            ),
                            rx.icon(
                                "circle-check",
                                class_name="h-3.5 w-3.5 text-green-500",
                            ),
                            class_name="flex items-center gap-2 py-1.5",
                        ),
                        rx.el.div(
                            rx.el.span(
                                "Strong password",
                                class_name="text-xs text-gray-700 flex-1",
                            ),
                            rx.icon(
                                "circle-check",
                                class_name="h-3.5 w-3.5 text-green-500",
                            ),
                            class_name="flex items-center gap-2 py-1.5",
                        ),
                        class_name="divide-y divide-gray-100",
                    ),
                    class_name="mt-4",
                ),
                class_name="lg:col-span-1 flex flex-col gap-4",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4",
        ),
        on_mount=ProfileState.init_profile,
    )


def profile_page() -> rx.Component:
    return app_layout(profile_content(), "Profile", "Manage your identity")


def _settings_section_header(icon: str, title: str, desc: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 text-[#E8471A]"),
            class_name="h-9 w-9 rounded-xl bg-orange-50 border border-orange-100 flex items-center justify-center",
        ),
        rx.el.div(
            rx.el.h3(title, class_name="text-base font-bold text-gray-900"),
            rx.el.p(desc, class_name="text-xs text-gray-500 mt-0.5"),
        ),
        class_name="flex items-start gap-3 mb-4",
    )


def _action_button(
    icon: str, label: str, desc: str, on_click=None, accent: str = "default"
) -> rx.Component:
    base = "w-full flex items-center justify-between gap-3 p-3 rounded-xl border transition-colors text-left"
    if accent == "danger":
        cls = (
            base
            + " border-red-200 bg-white hover:bg-red-50 hover:border-red-300"
        )
        icon_cls = "h-4 w-4 text-red-600"
        label_cls = "text-sm font-bold text-red-700"
    elif accent == "primary":
        cls = (
            base
            + " border-orange-200 bg-orange-50/40 hover:bg-orange-50 hover:border-orange-300"
        )
        icon_cls = "h-4 w-4 text-[#E8471A]"
        label_cls = "text-sm font-bold text-gray-900"
    else:
        cls = (
            base
            + " border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300"
        )
        icon_cls = "h-4 w-4 text-gray-700"
        label_cls = "text-sm font-bold text-gray-900"

    return rx.el.button(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name=icon_cls),
                class_name="h-9 w-9 rounded-lg bg-gray-50 border border-gray-100 flex items-center justify-center shrink-0",
            ),
            rx.el.div(
                rx.el.p(label, class_name=label_cls),
                rx.el.p(desc, class_name="text-[11px] text-gray-500 mt-0.5"),
            ),
            class_name="flex items-center gap-3",
        ),
        rx.icon("chevron-right", class_name="h-4 w-4 text-gray-400"),
        on_click=on_click,
        class_name=cls,
    )


def _delete_account_modal() -> rx.Component:
    return rx.cond(
        ProfileState.show_delete_modal,
        rx.el.div(
            rx.el.div(
                on_click=ProfileState.close_delete_modal,
                class_name="absolute inset-0 bg-black/50 backdrop-blur-sm",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "triangle-alert", class_name="h-6 w-6 text-red-600"
                    ),
                    class_name="h-12 w-12 rounded-2xl bg-red-50 border border-red-100 flex items-center justify-center",
                ),
                rx.el.h3(
                    "Delete your account?",
                    class_name="text-lg font-bold text-gray-900 mt-4",
                ),
                rx.el.p(
                    "This action requests permanent deletion of your FraudRadar account and all associated scan history. Our team will process the request within 48 hours.",
                    class_name="text-sm text-gray-600 mt-2 leading-relaxed",
                ),
                rx.el.div(
                    rx.el.label(
                        "Type DELETE to confirm",
                        class_name="block text-xs font-bold text-gray-700 mb-1.5 uppercase tracking-wider",
                    ),
                    rx.el.input(
                        placeholder="DELETE",
                        default_value=ProfileState.confirm_delete_text,
                        on_change=ProfileState.set_confirm_delete.debounce(150),
                        class_name="w-full px-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm font-mono focus:outline-hidden focus:ring-2 focus:ring-red-500",
                    ),
                    class_name="mt-4",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=ProfileState.close_delete_modal,
                        class_name="flex-1 px-4 py-2.5 rounded-lg border border-gray-300 text-gray-700 text-sm font-bold hover:bg-gray-50",
                    ),
                    rx.el.button(
                        rx.icon("trash-2", class_name="h-3.5 w-3.5"),
                        rx.el.span("Request Deletion"),
                        on_click=ProfileState.request_account_deletion,
                        class_name="flex-1 inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-lg bg-red-600 text-white text-sm font-bold hover:bg-red-700",
                    ),
                    class_name="flex items-center gap-2 mt-5",
                ),
                class_name="relative bg-white rounded-2xl shadow-2xl p-6 max-w-md w-full mx-4",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center",
        ),
        rx.fragment(),
    )


def settings_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            card(
                _settings_section_header(
                    "circle_user_round",
                    "Account Details",
                    "Your basic account information.",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Name",
                            class_name="text-[11px] font-bold text-gray-500 uppercase tracking-wider",
                        ),
                        rx.el.p(
                            AuthState.user_name,
                            class_name="text-sm font-semibold text-gray-900 mt-1",
                        ),
                        class_name="p-3 rounded-xl border border-gray-100 bg-gray-50/40",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Email",
                            class_name="text-[11px] font-bold text-gray-500 uppercase tracking-wider",
                        ),
                        rx.el.p(
                            AuthState.user_email,
                            class_name="text-sm font-semibold text-gray-900 mt-1 truncate",
                        ),
                        class_name="p-3 rounded-xl border border-gray-100 bg-gray-50/40",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Joined",
                            class_name="text-[11px] font-bold text-gray-500 uppercase tracking-wider",
                        ),
                        rx.el.p(
                            ProfileState.joined_date,
                            class_name="text-sm font-semibold text-gray-900 mt-1",
                        ),
                        class_name="p-3 rounded-xl border border-gray-100 bg-gray-50/40",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Plan",
                            class_name="text-[11px] font-bold text-gray-500 uppercase tracking-wider",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Free",
                                class_name="text-sm font-semibold text-gray-900",
                            ),
                            rx.el.span(
                                "Active",
                                class_name="text-[10px] font-bold text-green-700 bg-green-50 border border-green-200 px-1.5 py-0.5 rounded-full",
                            ),
                            class_name="flex items-center gap-2 mt-1",
                        ),
                        class_name="p-3 rounded-xl border border-gray-100 bg-gray-50/40",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-3",
                ),
                rx.el.a(
                    rx.icon("pen-line", class_name="h-3.5 w-3.5"),
                    rx.el.span("Edit profile", class_name="text-xs font-bold"),
                    href="/profile",
                    class_name="inline-flex items-center gap-1.5 mt-4 px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-700",
                ),
            ),
            card(
                _settings_section_header(
                    "bell",
                    "Notifications",
                    "Pick how you want to receive alerts and updates.",
                ),
                toggle_row(
                    "Email alerts",
                    "Get scan results via email",
                    ProfileState.notifications_email,
                    ProfileState.toggle_email_notif,
                ),
                toggle_row(
                    "SMS alerts",
                    "Critical alerts via SMS",
                    ProfileState.notifications_sms,
                    ProfileState.toggle_sms_notif,
                ),
                toggle_row(
                    "Push notifications",
                    "Real-time browser/app alerts",
                    ProfileState.notifications_push,
                    ProfileState.toggle_push_notif,
                ),
                toggle_row(
                    "High-risk alerts",
                    "Notify whenever a HIGH risk scan is detected",
                    ProfileState.high_risk_alerts,
                    ProfileState.toggle_high_risk,
                ),
                toggle_row(
                    "Weekly safety report",
                    "Summary every Monday",
                    ProfileState.weekly_report,
                    ProfileState.toggle_weekly,
                ),
                toggle_row(
                    "Trending scam news",
                    "Daily update on emerging scams in India",
                    ProfileState.scam_news,
                    ProfileState.toggle_scam_news,
                ),
                class_name="mt-4",
            ),
            card(
                _settings_section_header(
                    "shield-check",
                    "Security",
                    "Strengthen access to your account.",
                ),
                toggle_row(
                    "Two-factor authentication",
                    "Add an extra security layer with OTP",
                    ProfileState.two_factor_enabled,
                    ProfileState.toggle_2fa,
                ),
                toggle_row(
                    "Biometric sign-in",
                    "Use device fingerprint or face unlock",
                    ProfileState.biometric_enabled,
                    ProfileState.toggle_biometric,
                ),
                rx.el.div(
                    _action_button(
                        "key-round",
                        "Change Password",
                        "Update your password regularly",
                    ),
                    _action_button(
                        "log-out",
                        "Sign out of all devices",
                        "Revoke all active sessions",
                        on_click=AuthState.logout,
                    ),
                    _action_button(
                        "history",
                        "Login activity",
                        "Recent sign-in history and locations",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4",
                ),
                class_name="mt-4",
            ),
            card(
                _settings_section_header(
                    "lock",
                    "Privacy Controls",
                    "Decide how your data is used.",
                ),
                toggle_row(
                    "Anonymous analytics",
                    "Help us improve detection accuracy",
                    ProfileState.analytics_opt_in,
                    ProfileState.toggle_analytics,
                ),
                toggle_row(
                    "Share scam patterns",
                    "Contribute anonymized signals to community defense",
                    ProfileState.data_sharing,
                    ProfileState.toggle_data_sharing,
                ),
                toggle_row(
                    "Public profile badge",
                    "Show your verified status publicly",
                    ProfileState.public_profile,
                    ProfileState.toggle_public_profile,
                ),
                class_name="mt-4",
            ),
            card(
                _settings_section_header(
                    "download",
                    "Your Data",
                    "Export, review, or remove your information.",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.el.div(
                            rx.el.div(
                                rx.icon(
                                    "file-spreadsheet",
                                    class_name="h-4 w-4 text-[#E8471A]",
                                ),
                                class_name="h-9 w-9 rounded-lg bg-orange-50 border border-orange-100 flex items-center justify-center shrink-0",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    "Export Scan History (CSV)",
                                    class_name="text-sm font-bold text-gray-900 text-left",
                                ),
                                rx.el.p(
                                    "Download all scans as a spreadsheet.",
                                    class_name="text-[11px] text-gray-500 mt-0.5 text-left",
                                ),
                            ),
                            class_name="flex items-center gap-3",
                        ),
                        rx.icon("download", class_name="h-4 w-4 text-gray-400"),
                        on_click=ScanState.export_csv,
                        class_name="w-full flex items-center justify-between gap-3 p-3 rounded-xl border border-orange-200 bg-orange-50/30 hover:bg-orange-50 hover:border-orange-300 transition-colors",
                    ),
                    _action_button(
                        "file-text",
                        "Privacy Policy",
                        "Review how we handle your data",
                    ),
                    _action_button(
                        "scroll-text",
                        "Terms of Service",
                        "Read our usage agreement",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-3 gap-3",
                ),
                class_name="mt-4",
            ),
            card(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "triangle-alert", class_name="h-4 w-4 text-red-600"
                        ),
                        class_name="h-9 w-9 rounded-xl bg-red-50 border border-red-100 flex items-center justify-center",
                    ),
                    rx.el.div(
                        rx.el.h3(
                            "Danger Zone",
                            class_name="text-base font-bold text-red-900",
                        ),
                        rx.el.p(
                            "These actions are irreversible. Proceed with caution.",
                            class_name="text-xs text-red-700/80 mt-0.5",
                        ),
                    ),
                    class_name="flex items-start gap-3 mb-4",
                ),
                rx.el.div(
                    _action_button(
                        "log-out",
                        "Sign out everywhere",
                        "Force sign-out across all sessions",
                        on_click=AuthState.logout,
                        accent="danger",
                    ),
                    _action_button(
                        "trash-2",
                        "Delete account",
                        "Request permanent account removal",
                        on_click=ProfileState.open_delete_modal,
                        accent="danger",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-3",
                ),
                rx.cond(
                    ProfileState.save_message != "",
                    rx.el.div(
                        rx.icon("info", class_name="h-3.5 w-3.5 text-blue-600"),
                        rx.el.p(
                            ProfileState.save_message,
                            class_name="text-xs font-semibold text-blue-700",
                        ),
                        class_name="flex items-center gap-1.5 mt-3 p-2.5 rounded-lg bg-blue-50 border border-blue-200",
                    ),
                    rx.fragment(),
                ),
                class_name="mt-4 border-red-200/60 bg-red-50/20",
            ),
            on_mount=ProfileState.init_profile,
        ),
        _delete_account_modal(),
    )


def toggle_row(title: str, desc: str, value, on_toggle) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(title, class_name="text-sm font-medium text-gray-900"),
            rx.el.p(desc, class_name="text-xs text-gray-500"),
        ),
        rx.el.button(
            rx.el.div(
                class_name=rx.cond(
                    value,
                    "h-4 w-4 rounded-full bg-white translate-x-4 transition-transform",
                    "h-4 w-4 rounded-full bg-white translate-x-0.5 transition-transform",
                ),
            ),
            on_click=on_toggle,
            class_name=rx.cond(
                value,
                "h-5 w-9 rounded-full bg-[#E8471A] flex items-center transition-colors",
                "h-5 w-9 rounded-full bg-gray-300 flex items-center transition-colors",
            ),
        ),
        class_name="flex items-center justify-between py-3 border-b border-gray-100 last:border-0",
    )


def settings_page() -> rx.Component:
    return app_layout(
        settings_content(), "Settings", "Preferences and security"
    )


def helpline_content() -> rx.Component:
    helplines = [
        (
            "National Cyber Crime",
            "1930",
            "24x7 dedicated cybercrime helpline",
            "phone-call",
        ),
        ("Police Emergency", "112", "All India emergency", "siren"),
        ("Women Helpline", "1091", "For women in distress", "shield"),
        ("Banking Ombudsman", "14448", "RBI banking complaints", "landmark"),
    ]
    return rx.el.div(
        card(
            rx.el.div(
                rx.icon("phone-call", class_name="h-6 w-6 text-[#E8471A]"),
                rx.el.div(
                    rx.el.h3(
                        "Need help right now?",
                        class_name="text-base font-semibold text-gray-900",
                    ),
                    rx.el.p(
                        "Call these official helplines—free and confidential.",
                        class_name="text-sm text-gray-500",
                    ),
                ),
                class_name="flex items-start gap-3",
            ),
        ),
        rx.el.div(
            *[
                card(
                    rx.el.div(
                        rx.el.div(
                            rx.icon(icon, class_name="h-5 w-5 text-[#E8471A]"),
                            class_name="h-10 w-10 rounded-lg bg-orange-50 flex items-center justify-center",
                        ),
                        rx.el.div(
                            rx.el.p(
                                name,
                                class_name="text-sm font-semibold text-gray-900",
                            ),
                            rx.el.p(desc, class_name="text-xs text-gray-500"),
                        ),
                        class_name="flex items-start gap-3 mb-4",
                    ),
                    rx.el.a(
                        f"Call {num}",
                        href=f"tel:{num}",
                        class_name="block text-center px-4 py-2 rounded-lg bg-[#E8471A] text-white text-sm font-medium hover:bg-[#c43a13]",
                    ),
                )
                for name, num, desc, icon in helplines
            ],
            class_name="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4",
        ),
        card(
            rx.el.h3(
                "Online Reporting",
                class_name="text-base font-semibold text-gray-900 mb-3",
            ),
            rx.el.div(
                rx.el.a(
                    "cybercrime.gov.in",
                    href="https://cybercrime.gov.in",
                    target="_blank",
                    class_name="text-sm text-[#E8471A] hover:underline",
                ),
                rx.el.a(
                    "RBI Complaint Portal",
                    href="https://cms.rbi.org.in",
                    target="_blank",
                    class_name="text-sm text-[#E8471A] hover:underline",
                ),
                rx.el.a(
                    "Sancharsaathi.gov.in",
                    href="https://sancharsaathi.gov.in",
                    target="_blank",
                    class_name="text-sm text-[#E8471A] hover:underline",
                ),
                class_name="flex flex-col gap-2",
            ),
            class_name="mt-4",
        ),
    )


def helpline_page() -> rx.Component:
    return app_layout(
        helpline_content(), "Helpline", "Official emergency contacts"
    )


def scam_guide_content() -> rx.Component:
    guides = [
        (
            "UPI Fraud",
            "Fake payment requests, QR scams, collect requests posing as refunds.",
            "indian-rupee",
        ),
        (
            "OTP Scams",
            "Callers impersonating bank/telecom asking for OTP to 'verify'.",
            "key",
        ),
        (
            "KYC Scams",
            "SMS claiming KYC expired, link redirects to phishing site.",
            "id-card",
        ),
        (
            "Job Offers",
            "Too-good-to-be-true offers asking registration fees.",
            "briefcase",
        ),
        (
            "Courier Scams",
            "Calls about fake parcel containing illegal items.",
            "package",
        ),
        (
            "Loan Apps",
            "Unregulated apps demanding contacts/photos access.",
            "wallet",
        ),
        (
            "Investment Scams",
            "Crypto/forex 'guaranteed returns' via Telegram groups.",
            "trending-up",
        ),
        (
            "Romance Scams",
            "Long-term emotional manipulation for money.",
            "heart",
        ),
    ]
    return rx.el.div(
        card(
            rx.el.h3(
                "Learn to spot scams",
                class_name="text-base font-semibold text-gray-900",
            ),
            rx.el.p(
                "Common fraud patterns targeting Indian users.",
                class_name="text-sm text-gray-500 mt-1",
            ),
        ),
        rx.el.div(
            *[
                card(
                    rx.el.div(
                        rx.icon(icon, class_name="h-5 w-5 text-[#E8471A]"),
                        class_name="h-10 w-10 rounded-lg bg-orange-50 flex items-center justify-center mb-3",
                    ),
                    rx.el.h4(
                        title, class_name="text-sm font-semibold text-gray-900"
                    ),
                    rx.el.p(
                        desc,
                        class_name="text-xs text-gray-600 mt-1 leading-relaxed",
                    ),
                    class_name="hover:border-orange-300 transition-colors",
                )
                for title, desc, icon in guides
            ],
            class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-4",
        ),
        card(
            rx.el.h3(
                "Golden Rules",
                class_name="text-base font-semibold text-gray-900 mb-3",
            ),
            rx.el.ul(
                rx.el.li(
                    "Never share OTP, PIN, CVV, or password—even with 'bank officials'.",
                    class_name="text-sm text-gray-700",
                ),
                rx.el.li(
                    "Verify caller identity by calling back on the bank's official number.",
                    class_name="text-sm text-gray-700",
                ),
                rx.el.li(
                    "Don't click unknown links in SMS, WhatsApp, or email.",
                    class_name="text-sm text-gray-700",
                ),
                rx.el.li(
                    "Report suspicious activity to 1930 within 24 hours.",
                    class_name="text-sm text-gray-700",
                ),
                rx.el.li(
                    "Use FraudRadar's Analyze tool when in doubt.",
                    class_name="text-sm text-gray-700",
                ),
                class_name="space-y-2 list-disc pl-5",
            ),
            class_name="mt-4",
        ),
    )


def scam_guide_page() -> rx.Component:
    return app_layout(
        scam_guide_content(), "Scam Guide", "Recognize and avoid common scams"
    )


def legal_content() -> rx.Component:
    return rx.el.div(
        card(
            rx.el.h3(
                "Privacy & Trust",
                class_name="text-base font-semibold text-gray-900 mb-2",
            ),
            rx.el.p(
                "FraudRadar processes your scan input only to provide AI analysis. We do not sell, share, or rent your data. Scans are stored securely and accessible only to you.",
                class_name="text-sm text-gray-700 leading-relaxed",
            ),
        ),
        card(
            rx.el.h3(
                "Terms of Service",
                class_name="text-base font-semibold text-gray-900 mb-2",
            ),
            rx.el.p(
                "FraudRadar provides AI-assisted analysis for educational and safety purposes. Results are best-effort indicators, not legal or financial advice. Always verify through official channels.",
                class_name="text-sm text-gray-700 leading-relaxed",
            ),
            class_name="mt-4",
        ),
        card(
            rx.el.h3(
                "Compliance",
                class_name="text-base font-semibold text-gray-900 mb-2",
            ),
            rx.el.ul(
                rx.el.li(
                    "Aligned with Indian IT Act 2000 & DPDP Act 2023.",
                    class_name="text-sm text-gray-700",
                ),
                rx.el.li(
                    "Encryption in transit (TLS 1.2+).",
                    class_name="text-sm text-gray-700",
                ),
                rx.el.li(
                    "Authentication via secure password hashing.",
                    class_name="text-sm text-gray-700",
                ),
                rx.el.li(
                    "No third-party ad tracking.",
                    class_name="text-sm text-gray-700",
                ),
                class_name="space-y-1 list-disc pl-5",
            ),
            class_name="mt-4",
        ),
        card(
            rx.el.h3(
                "Disclaimer",
                class_name="text-base font-semibold text-gray-900 mb-2",
            ),
            rx.el.p(
                "Use FraudRadar as a supportive tool. For confirmed fraud, immediately call 1930 or report at cybercrime.gov.in. FraudRadar is not affiliated with any government agency.",
                class_name="text-sm text-gray-700 leading-relaxed",
            ),
            class_name="mt-4",
        ),
    )


def legal_page() -> rx.Component:
    return app_layout(
        legal_content(), "Legal & Trust", "Privacy, terms, and compliance"
    )