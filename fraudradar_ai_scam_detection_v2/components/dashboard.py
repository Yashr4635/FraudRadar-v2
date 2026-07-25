import reflex as rx
from fraudradar_ai_scam_detection_v2.components.sidebar import app_layout
from fraudradar_ai_scam_detection_v2.states.auth_state import AuthState
from fraudradar_ai_scam_detection_v2.states.scan_state import ScanState
from fraudradar_ai_scam_detection_v2.states.dashboard_state import DashboardState


def lift_card(*children, class_name: str = "") -> rx.Component:
    return rx.el.div(
        *children,
        class_name=(
            "bg-white border border-gray-200 rounded-2xl p-5 "
            "shadow-xs hover:shadow-md hover:-translate-y-0.5 "
            "transition-all duration-300 "
        )
        + class_name,
    )


def verdict_pill(verdict) -> rx.Component:
    return rx.el.span(
        verdict,
        class_name=rx.match(
            verdict,
            ("SAFE", "inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-semibold bg-green-50 text-green-700 border border-green-200 w-fit"),
            ("MEDIUM", "inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-semibold bg-yellow-50 text-yellow-700 border border-yellow-200 w-fit"),
            ("HIGH", "inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-semibold bg-red-50 text-red-700 border border-red-200 w-fit"),
            "inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-semibold bg-gray-100 text-gray-600 border border-gray-200 w-fit",
        ),
    )


def sparkline(heights: list[int], color: str) -> rx.Component:
    return rx.el.div(
        *[
            rx.el.div(
                class_name=f"flex-1 rounded-sm {color} opacity-80",
                custom_attrs={"style": {"height": f"{h}%"}},
            )
            for h in heights
        ],
        class_name="flex items-end gap-0.5 h-8 w-20",
    )


def overview_card(
    label: str,
    value,
    icon: str,
    trend: str,
    trend_color: str,
    spark_heights: list[int],
    spark_color: str,
    accent_bg: str,
    accent_text: str,
) -> rx.Component:
    return lift_card(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name=f"h-5 w-5 {accent_text}"),
                class_name=f"h-10 w-10 rounded-xl {accent_bg} flex items-center justify-center",
            ),
            sparkline(spark_heights, spark_color),
            class_name="flex items-start justify-between",
        ),
        rx.el.p(label, class_name="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mt-4"),
        rx.el.p(value, class_name="text-3xl font-extrabold text-gray-900 mt-1"),
        rx.el.div(
            rx.icon("trending-up", class_name=f"h-3 w-3 {trend_color}"),
            rx.el.span(trend, class_name=f"text-xs font-semibold {trend_color}"),
            rx.el.span("vs last week", class_name="text-xs text-gray-500"),
            class_name="flex items-center gap-1.5 mt-2",
        ),
    )


def overview_row() -> rx.Component:
    return rx.el.div(
        overview_card("Total Scans", ScanState.total_scans.to_string(), "scan-search", "+12.4%", "stroke-green-600", [30, 50, 40, 70, 60, 85, 95], "bg-orange-400", "bg-orange-50", "stroke-[#E8471A]"),
        overview_card("Threats Blocked", ScanState.scams_detected.to_string(), "shield-alert", "+8.2%", "stroke-red-600", [20, 35, 30, 50, 45, 65, 75], "bg-red-400", "bg-red-50", "stroke-red-500"),
        overview_card("Avg Risk Score", f"{ScanState.avg_risk:.1f}%", "trending-up", "-3.1%", "stroke-emerald-600", [60, 55, 70, 50, 65, 45, 40], "bg-yellow-400", "bg-yellow-50", "stroke-yellow-600"),
        overview_card("Latest Verdict", ScanState.latest_verdict, "activity", "Live", "stroke-blue-600", [40, 60, 50, 80, 60, 90, 70], "bg-blue-400", "bg-blue-50", "stroke-blue-500"),
        class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4",
    )


def quick_action_card(icon: str, title: str, desc: str, href: str, accent: str) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.icon(icon, class_name=f"h-5 w-5 {accent}"),
            class_name="h-11 w-11 rounded-xl bg-gradient-to-br from-orange-50 to-white border border-orange-100 flex items-center justify-center mb-3 group-hover:scale-110 group-hover:shadow-sm transition-all duration-300",
        ),
        rx.el.p(title, class_name="text-sm font-bold text-gray-900"),
        rx.el.p(desc, class_name="text-xs text-gray-500 mt-1 leading-relaxed min-h-[2.25rem]"),
        rx.el.div(
            rx.el.span("Open", class_name="text-xs font-semibold text-[#E8471A]"),
            rx.icon("arrow-right", class_name="h-3 w-3 stroke-[#E8471A] group-hover:translate-x-1 transition-transform"),
            class_name="flex items-center gap-1 mt-3",
        ),
        href=href,
        class_name="group relative bg-white border border-gray-200 rounded-2xl p-4 hover:border-orange-300 hover:shadow-lg hover:-translate-y-1 transition-all duration-300",
    )


def quick_scan_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p("Quick Scan", class_name="text-[11px] font-semibold text-gray-500 uppercase tracking-wider"),
                rx.el.h3("Start a new fraud check", class_name="text-base font-bold text-gray-900 mt-1"),
            ),
            rx.el.a("View all tools", rx.icon("arrow-right", class_name="h-3 w-3"), href="/analyze", class_name="inline-flex items-center gap-1 text-xs font-semibold text-[#E8471A] hover:underline"),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.el.div(
            quick_action_card("message-square-warning", "Analyze Message", "Paste SMS, WhatsApp, or email to scan.", "/analyze", "stroke-[#E8471A]"),
            quick_action_card("globe", "Scan Website", "Verify a URL for phishing or fraud.", "/analyze", "stroke-blue-500"),
            quick_action_card("phone", "Verify Phone", "Check a number for known scam reports.", "/analyze", "stroke-emerald-500"),
            quick_action_card("image", "Upload Screenshot", "Send a screenshot for AI analysis.", "/analyze", "stroke-purple-500"),
            quick_action_card("qr-code", "Scan QR Code", "Decode and verify any QR before paying.", "/analyze", "stroke-pink-500"),
            class_name="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3",
        ),
    )


def timeline_item(h) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                class_name=rx.match(
                    h["verdict"],
                    ("HIGH", "h-3 w-3 rounded-full bg-red-500 ring-4 ring-red-100"),
                    ("MEDIUM", "h-3 w-3 rounded-full bg-yellow-500 ring-4 ring-yellow-100"),
                    ("SAFE", "h-3 w-3 rounded-full bg-green-500 ring-4 ring-green-100"),
                    "h-3 w-3 rounded-full bg-gray-400 ring-4 ring-gray-100",
                ),
            ),
            rx.el.div(class_name="w-px flex-1 bg-gray-100 mt-1"),
            class_name="relative flex flex-col items-center pt-2",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    verdict_pill(h["verdict"]),
                    rx.el.span(h["input_type"].upper(), class_name="text-[10px] font-bold text-gray-400 uppercase tracking-wider"),
                    rx.el.span("·", class_name="text-[10px] text-gray-300"),
                    rx.el.span(h["timestamp"], class_name="text-[10px] text-gray-400"),
                    class_name="flex items-center gap-2 flex-wrap",
                ),
                rx.el.a(
                    rx.icon("eye", class_name="h-3.5 w-3.5 stroke-gray-500"),
                    href="/history",
                    class_name="h-7 w-7 rounded-md border border-gray-200 hover:border-orange-300 hover:bg-orange-50 flex items-center justify-center transition-colors shrink-0",
                ),
                class_name="flex items-center justify-between gap-2",
            ),
            rx.el.p(h["input_text"], class_name="text-sm text-gray-800 mt-2 leading-relaxed line-clamp-2"),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        class_name=rx.cond(h["risk_score"] >= 70, "h-1.5 rounded-full bg-red-500", rx.cond(h["risk_score"] >= 40, "h-1.5 rounded-full bg-yellow-500", "h-1.5 rounded-full bg-green-500")),
                        custom_attrs={"style": {"width": f"{h['risk_score']}%"}},
                    ),
                    class_name="flex-1 h-1.5 rounded-full bg-gray-100",
                ),
                rx.el.span(f"{h['risk_score']}% risk", class_name="text-[11px] font-bold text-gray-700 ml-3 tabular-nums"),
                rx.el.span("·", class_name="text-[11px] text-gray-300 mx-2"),
                rx.el.span("AI 94%", class_name="text-[11px] font-medium text-gray-500"),
                class_name="flex items-center mt-3",
            ),
            class_name="flex-1 pb-5 ml-3 pt-0.5",
        ),
        class_name="flex items-start gap-1",
    )


def recent_timeline() -> rx.Component:
    return lift_card(
        rx.el.div(
            rx.el.div(
                rx.el.p("Recent Activity", class_name="text-[11px] font-semibold text-gray-500 uppercase tracking-wider"),
                rx.el.h3("Live scan timeline", class_name="text-base font-bold text-gray-900 mt-1"),
            ),
            rx.el.a("View all", rx.icon("arrow-right", class_name="h-3 w-3"), href="/history", class_name="inline-flex items-center gap-1 text-xs font-semibold text-[#E8471A] hover:underline"),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.cond(
            ScanState.history.length() > 0,
            rx.el.div(rx.foreach(ScanState.history[:6], timeline_item)),
            rx.el.div(
                rx.el.div(rx.icon("inbox", class_name="h-8 w-8 stroke-gray-300"), class_name="h-16 w-16 rounded-2xl bg-gray-50 flex items-center justify-center mx-auto"),
                rx.el.p("No scans yet", class_name="text-sm font-semibold text-gray-900 mt-3 text-center"),
                rx.el.p("Run your first AI fraud check to populate this timeline.", class_name="text-xs text-gray-500 text-center mt-1"),
                rx.el.a(rx.icon("scan-search", class_name="h-3.5 w-3.5"), rx.el.span("Start First Scan"), href="/analyze", class_name="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#E8471A] text-white text-xs font-semibold hover:bg-[#c43a13] mt-4"),
                class_name="py-10 flex flex-col items-center",
            ),
        ),
    )


def assistant_widget() -> rx.Component:
    return rx.el.div(
        rx.el.div(class_name="absolute inset-0 bg-gradient-to-br from-[#E8471A] to-[#c43a13] rounded-2xl"),
        rx.el.div(class_name="absolute top-0 right-0 w-40 h-40 bg-white/10 rounded-full blur-3xl"),
        rx.el.div(class_name="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full blur-2xl"),
        rx.el.div(
            rx.el.div(
                rx.el.div(rx.icon("sparkles", class_name="h-5 w-5 text-white"), class_name="h-11 w-11 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center"),
                rx.el.div(
                    rx.el.p("AI Safety Assistant", class_name="text-sm font-bold text-white"),
                    rx.el.p("Powered by Groq · Llama 3.3", class_name="text-[11px] text-white/75"),
                ),
                class_name="flex items-center gap-3",
            ),
            rx.el.p("Ask anything about scams, suspicious messages, or how to stay safe online.", class_name="text-sm text-white/90 mt-4 leading-relaxed"),
            rx.el.a(
                rx.icon("message-circle", class_name="h-3.5 w-3.5"),
                rx.el.span("Open Assistant"),
                rx.icon("arrow-right", class_name="h-3 w-3 group-hover:translate-x-1 transition-transform"),
                href="/assistant",
                class_name="group inline-flex items-center gap-1.5 px-4 py-2.5 rounded-lg bg-white text-[#E8471A] text-xs font-bold hover:bg-orange-50 transition-colors mt-5",
            ),
            class_name="relative",
        ),
        class_name="relative overflow-hidden rounded-2xl p-5 shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300",
    )


def emergency_help_card() -> rx.Component:
    return lift_card(
        rx.el.div(
            rx.el.div(rx.icon("phone-call", class_name="h-5 w-5 stroke-red-600"), class_name="h-10 w-10 rounded-xl bg-red-50 border border-red-100 flex items-center justify-center"),
            rx.el.div(
                rx.el.p("Emergency Help", class_name="text-sm font-bold text-gray-900"),
                rx.el.p("Cybercrime support 24×7", class_name="text-[11px] text-gray-500"),
            ),
            class_name="flex items-center gap-3",
        ),
        rx.el.div(
            rx.el.a(
                rx.el.div(
                    rx.el.p("Call 1930", class_name="text-sm font-bold text-white"),
                    rx.el.p("National helpline", class_name="text-[11px] text-white/80 mt-0.5"),
                ),
                rx.icon("phone", class_name="h-4 w-4 text-white shrink-0"),
                href="tel:1930",
                class_name="flex items-center justify-between p-3.5 rounded-xl bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 transition-colors",
            ),
            rx.el.a(
                rx.el.div(
                    rx.el.p("Report Online", class_name="text-sm font-bold text-gray-900"),
                    rx.el.p("cybercrime.gov.in", class_name="text-[11px] text-gray-500 mt-0.5"),
                ),
                rx.icon("external-link", class_name="h-4 w-4 stroke-gray-700 shrink-0"),
                href="https://cybercrime.gov.in",
                target="_blank",
                class_name="flex items-center justify-between p-3.5 rounded-xl border border-gray-200 hover:border-orange-300 hover:bg-orange-50 transition-colors",
            ),
            class_name="flex flex-col gap-2.5 mt-4",
        ),
    )


def risk_breakdown_row(c, i) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    (i + 1).to_string(),
                    class_name="h-6 w-6 rounded-full bg-gray-900 text-white text-[11px] font-bold flex items-center justify-center shrink-0",
                ),
                rx.el.span(c["name"].to(str), class_name="text-sm font-semibold text-gray-800"),
                class_name="flex items-center gap-2.5",
            ),
            rx.el.span(c["value"].to(str) + "%", class_name="text-sm font-extrabold text-gray-900 tabular-nums"),
            class_name="flex items-center justify-between mb-2",
        ),
        rx.el.div(
            rx.el.div(
                class_name=f"h-2.5 rounded-full {c['color']}",
                custom_attrs={"style": {"width": c["value"].to_string() + "%"}},
            ),
            class_name="w-full h-2.5 rounded-full bg-gray-100 overflow-hidden",
        ),
        class_name="p-3.5 rounded-xl border border-gray-100 hover:border-orange-200 hover:bg-orange-50/20 transition-colors",
    )


def risk_breakdown_card() -> rx.Component:
    return lift_card(
        rx.el.div(
            rx.el.div(
                rx.el.div(rx.icon("bar-chart-3", class_name="h-5 w-5 stroke-[#E8471A]"), class_name="h-10 w-10 rounded-xl bg-orange-50 border border-orange-100 flex items-center justify-center"),
                rx.el.div(
                    rx.el.p("Risk Breakdown", class_name="text-[11px] font-semibold text-gray-500 uppercase tracking-wider"),
                    rx.el.h3("Top scam categories", class_name="text-base font-bold text-gray-900 mt-1"),
                ),
                class_name="flex items-center gap-3",
            ),
            rx.el.span(
                "Live analysis",
                class_name="inline-flex items-center gap-1.5 text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full",
            ),
            class_name="flex items-center justify-between mb-5",
        ),
        rx.el.div(
            rx.foreach(DashboardState.risk_categories, risk_breakdown_row),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-3",
        ),
    )


def tips_carousel() -> rx.Component:
    return lift_card(
        rx.el.div(
            rx.el.div(
                rx.icon("lightbulb", class_name="h-4 w-4 stroke-yellow-500"),
                rx.el.p("Daily Safety Tip", class_name="text-[11px] font-semibold text-gray-500 uppercase tracking-wider"),
                class_name="flex items-center gap-1.5",
            ),
            rx.el.div(
                rx.el.button(rx.icon("chevron-left", class_name="h-3.5 w-3.5"), on_click=DashboardState.prev_tip, class_name="h-7 w-7 rounded-md border border-gray-200 hover:border-orange-300 hover:bg-orange-50 flex items-center justify-center transition-colors"),
                rx.el.button(rx.icon("chevron-right", class_name="h-3.5 w-3.5"), on_click=DashboardState.next_tip, class_name="h-7 w-7 rounded-md border border-gray-200 hover:border-orange-300 hover:bg-orange-50 flex items-center justify-center transition-colors"),
                class_name="flex items-center gap-1",
            ),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.el.div(
            rx.el.div(rx.icon(DashboardState.selected_tip["icon"], class_name="h-5 w-5 stroke-[#E8471A]"), class_name="h-11 w-11 rounded-xl bg-orange-50 border border-orange-100 flex items-center justify-center shrink-0"),
            rx.el.div(
                rx.el.p(DashboardState.selected_tip["title"], class_name="text-sm font-bold text-gray-900"),
                rx.el.p(DashboardState.selected_tip["desc"], class_name="text-xs text-gray-600 mt-1.5 leading-relaxed"),
            ),
            class_name="flex items-start gap-3",
        ),
        rx.el.div(
            rx.foreach(
                DashboardState.tips,
                lambda t, i: rx.el.button(
                    on_click=lambda: DashboardState.set_tip(i),
                    class_name=rx.cond(i == DashboardState.current_tip, "h-1.5 w-6 rounded-full bg-[#E8471A]", "h-1.5 w-1.5 rounded-full bg-gray-300 hover:bg-gray-400 transition-colors"),
                ),
            ),
            class_name="flex items-center justify-center gap-1.5 mt-4",
        ),
    )


def notification_center() -> rx.Component:
    return lift_card(
        rx.el.div(
            rx.el.p("Notifications", class_name="text-[11px] font-semibold text-gray-500 uppercase tracking-wider"),
            rx.el.h3("Recent alerts", class_name="text-base font-bold text-gray-900 mt-1"),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.foreach(
                DashboardState.notifications,
                lambda n: rx.el.div(
                    rx.el.div(
                        rx.icon(n["icon"], class_name=rx.match(n["severity"], ("high", "h-4 w-4 stroke-red-600"), ("medium", "h-4 w-4 stroke-yellow-600"), "h-4 w-4 stroke-blue-600")),
                        class_name=rx.match(n["severity"], ("high", "h-9 w-9 rounded-xl bg-red-50 border border-red-100 flex items-center justify-center shrink-0"), ("medium", "h-9 w-9 rounded-xl bg-yellow-50 border border-yellow-100 flex items-center justify-center shrink-0"), "h-9 w-9 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center shrink-0"),
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(n["title"], class_name="text-xs font-bold text-gray-900"),
                            rx.cond(n["unread"], rx.el.div(class_name="h-1.5 w-1.5 rounded-full bg-[#E8471A] shrink-0"), rx.fragment()),
                            class_name="flex items-center gap-1.5",
                        ),
                        rx.el.p(n["message"], class_name="text-[11px] text-gray-600 mt-0.5 leading-relaxed"),
                        rx.el.p(n["time"], class_name="text-[10px] text-gray-400 mt-1"),
                        class_name="flex-1 min-w-0",
                    ),
                    class_name="flex items-start gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors",
                ),
            ),
            class_name="flex flex-col gap-1",
        ),
    )


def dashboard_content() -> rx.Component:
    return rx.el.div(
        # Row 1: Overview stats
        rx.el.div(overview_row(), class_name="mt-4"),

        # Row 2: Quick scan
        rx.el.div(quick_scan_panel(), class_name="mt-4"),

        # Row 3: Recent timeline + Assistant + Emergency
        rx.el.div(
            rx.el.div(recent_timeline(), class_name="lg:col-span-2"),
            rx.el.div(
                assistant_widget(),
                rx.el.div(emergency_help_card(), class_name="mt-4"),
                class_name="lg:col-span-1",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4",
        ),

        # Row 4: Top scam categories — now full width, achievements removed
        rx.el.div(risk_breakdown_card(), class_name="mt-4"),

        # Row 5: Daily tip + Recent alerts
        rx.el.div(
            rx.el.div(tips_carousel(), class_name="md:col-span-1"),
            rx.el.div(notification_center(), class_name="md:col-span-2"),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4",
        ),

        class_name="bg-[#F8FAFC] -mx-6 -my-6 px-6 py-6 min-h-full",
    )


def dashboard_page() -> rx.Component:
    return app_layout(
        dashboard_content(),
        "Dashboard",
        f"Command center · {AuthState.user_email}",
    )