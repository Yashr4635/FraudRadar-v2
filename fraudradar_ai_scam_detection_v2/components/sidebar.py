import reflex as rx
import datetime
from fraudradar_ai_scam_detection_v2.states.auth_state import AuthState


def _is_active(href: str) -> rx.Var:
    from reflex.state import State as _RxState
    return _RxState.router.page.path == href


def nav_link(icon: str, label: str, href: str) -> rx.Component:
    active = _is_active(href)
    return rx.el.a(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 nav-icon"),
            class_name=rx.cond(
                active,
                "h-8 w-8 rounded-lg bg-white/20 flex items-center justify-center text-white",
                "h-8 w-8 rounded-lg bg-transparent flex items-center justify-center text-gray-500 group-hover:text-[#E8471A] group-hover:bg-orange-50",
            ),
        ),
        rx.el.span(label, class_name="text-sm font-medium flex-1"),
        rx.cond(
            active,
            rx.el.div(class_name="h-1.5 w-1.5 rounded-full bg-white"),
            rx.fragment(),
        ),
        href=href,
        class_name=rx.cond(
            active,
            "nav-pill group flex items-center gap-2.5 px-2.5 py-2 rounded-xl bg-gradient-to-r from-[#E8471A] to-[#c43a13] text-white shadow-md shadow-orange-200/60",
            "nav-pill group flex items-center gap-2.5 px-2.5 py-2 rounded-xl text-gray-700 hover:bg-orange-50/60 hover:text-[#E8471A]",
        ),
    )


def sidebar_section_label(label: str) -> rx.Component:
    return rx.el.p(
        label,
        class_name="px-3 pt-5 pb-2 text-[10px] font-bold text-gray-400 tracking-[0.12em] uppercase",
    )


def bottom_action(icon: str, label: str, href: str = "#") -> rx.Component:
    return rx.el.a(
        rx.icon(icon, class_name="h-3.5 w-3.5 text-gray-500"),
        rx.el.span(label, class_name="text-xs font-medium text-gray-700"),
        href=href,
        class_name="flex items-center gap-2 px-2.5 py-1.5 rounded-lg hover:bg-gray-100 hover:text-[#E8471A] transition-colors",
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("shield-check", class_name="h-5 w-5 text-white icon-spin-hover"),
                    class_name="h-10 w-10 rounded-xl bg-gradient-to-br from-[#E8471A] to-[#c43a13] flex items-center justify-center shadow-md shadow-orange-200/60",
                ),
                rx.el.div(
                    rx.el.p("FraudRadar", class_name="text-sm font-bold text-gray-900"),
                    rx.el.p("Scam Defense AI", class_name="text-[10px] text-gray-500 font-medium"),
                ),
                class_name="flex items-center gap-3 px-4 h-16 border-b border-gray-100",
            ),
            rx.el.nav(
                sidebar_section_label("Main"),
                nav_link("layout-dashboard", "Dashboard", "/dashboard"),
                nav_link("scan-search", "Analyze", "/analyze"),
                nav_link("history", "History", "/history"),
                nav_link("message-circle", "Assistant", "/assistant"),
                sidebar_section_label("Resources"),
                nav_link("phone", "Helpline", "/helpline"),
                nav_link("book-open", "Scam Guide", "/scam-guide"),
                nav_link("scale", "Legal & Trust", "/legal"),
                sidebar_section_label("Account"),
                nav_link("user", "Profile", "/profile"),
                nav_link("settings", "Settings", "/settings"),
                class_name="flex flex-col flex-1 px-2.5 py-2 gap-0.5 overflow-y-auto",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon("phone-call", class_name="h-4 w-4 text-white"),
                            class_name="h-8 w-8 rounded-lg bg-gradient-to-br from-[#E8471A] to-[#c43a13] flex items-center justify-center shadow-md shadow-orange-200/60 shrink-0",
                        ),
                        rx.el.div(
                            rx.el.p("Helpline 1930", class_name="text-xs font-bold text-gray-900"),
                            rx.el.p("24×7 Cyber Crime", class_name="text-[10px] text-gray-500"),
                        ),
                        class_name="flex items-center gap-2",
                    ),
                    rx.el.a(
                        rx.icon("phone", class_name="h-3 w-3"),
                        rx.el.span("Call Now"),
                        href="tel:1930",
                        class_name="btn-press mt-2.5 w-full inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#E8471A] text-white text-[11px] font-bold hover:bg-[#c43a13] transition-colors",
                    ),
                    class_name="rounded-2xl border border-orange-200/70 bg-gradient-to-br from-orange-50 to-white p-3 shadow-xs",
                ),
                rx.el.div(
                    bottom_action("life-buoy", "Support", "mailto:hello@fraudradar.app"),
                    bottom_action("message-square", "Feedback", "mailto:hello@fraudradar.app"),
                    bottom_action("info", "About", "/legal"),
                    class_name="flex flex-col gap-0.5 mt-3",
                ),
                rx.el.button(
                    rx.icon("log-out", class_name="h-3.5 w-3.5"),
                    rx.el.span("Sign Out", class_name="text-xs font-semibold"),
                    on_click=AuthState.logout,
                    class_name="btn-press mt-2 w-full flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl border border-gray-200 bg-white text-gray-700 hover:bg-red-50 hover:border-red-200 hover:text-red-600 transition-colors",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            AuthState.user_name.to_string()[0:1].upper(),
                            class_name="h-7 w-7 rounded-full bg-gradient-to-br from-[#E8471A] to-[#c43a13] text-white flex items-center justify-center text-[11px] font-bold shrink-0",
                        ),
                        rx.el.div(
                            rx.el.p(AuthState.user_name, class_name="text-xs font-bold text-gray-900 truncate"),
                            rx.el.p(AuthState.user_email, class_name="text-[10px] text-gray-500 truncate"),
                            class_name="min-w-0 flex-1",
                        ),
                        class_name="flex items-center gap-2 min-w-0",
                    ),
                    class_name="mt-3 px-2 py-2 rounded-xl bg-gray-50 border border-gray-100",
                ),
                class_name="border-t border-gray-100 p-3",
            ),
            class_name="flex flex-col h-full bg-white",
        ),
        class_name="fixed left-0 top-0 h-screen w-64 bg-white border-r border-gray-200 hidden lg:flex flex-col z-40 shadow-xs",
    )


def mobile_top() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("shield-check", class_name="h-4 w-4 text-white"),
                class_name="h-9 w-9 rounded-xl bg-gradient-to-br from-[#E8471A] to-[#c43a13] flex items-center justify-center",
            ),
            rx.el.div(
                rx.el.p("FraudRadar", class_name="text-sm font-bold text-gray-900"),
                rx.el.p("Scam Defense", class_name="text-[10px] text-gray-500"),
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.div(
            rx.el.a(
                rx.icon("scan-search", class_name="h-4 w-4 text-white"),
                href="/analyze",
                class_name="h-9 w-9 rounded-xl bg-[#E8471A] flex items-center justify-center",
            ),
            rx.el.button(
                rx.icon("log-out", class_name="h-4 w-4 text-gray-700"),
                on_click=AuthState.logout,
                class_name="h-9 w-9 rounded-xl border border-gray-200 bg-white flex items-center justify-center",
            ),
            class_name="flex items-center gap-2",
        ),
        class_name="lg:hidden flex items-center justify-between px-4 h-14 bg-white border-b border-gray-200 sticky top-0 z-40",
    )


def mobile_tabbar() -> rx.Component:
    items = [
        ("layout-dashboard", "Home", "/dashboard"),
        ("scan-search", "Scan", "/analyze"),
        ("history", "History", "/history"),
        ("message-circle", "AI", "/assistant"),
        ("user", "Profile", "/profile"),
    ]
    return rx.el.nav(
        *[
            rx.el.a(
                rx.icon(icon, class_name="h-4 w-4"),
                rx.el.span(label, class_name="text-[10px] font-semibold mt-0.5"),
                href=href,
                class_name="flex flex-col items-center justify-center gap-0 flex-1 py-2 text-gray-500 hover:text-[#E8471A] transition-colors",
            )
            for icon, label, href in items
        ],
        class_name="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex items-center z-40 shadow-lg",
    )


def header_bar(title: str, subtitle: str = "") -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    title,
                    class_name="text-lg sm:text-xl font-bold text-gray-900 tracking-tight",
                ),
                rx.cond(
                    subtitle != "",
                    rx.el.p(subtitle, class_name="text-xs sm:text-sm text-gray-500 mt-0.5"),
                    rx.fragment(),
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(class_name="h-2 w-2 rounded-full bg-green-500 status-dot"),
                    rx.el.span("Online", class_name="text-[11px] font-semibold text-green-700"),
                    class_name="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-green-50 border border-green-200",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex items-center justify-between h-16 px-4 sm:px-6",
        ),
        class_name="sticky top-0 bg-white/85 backdrop-blur-xl border-b border-gray-200 z-30",
    )


def footer() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("shield-check", class_name="h-3.5 w-3.5 text-white"),
                    class_name="h-6 w-6 rounded-md bg-gradient-to-br from-[#E8471A] to-[#c43a13] flex items-center justify-center",
                ),
                rx.el.span("FraudRadar", class_name="text-xs font-bold text-gray-900"),
                rx.el.span("·", class_name="text-xs text-gray-300"),
                rx.el.div(
                    rx.icon("sparkles", class_name="h-3 w-3 text-[#E8471A]"),
                    rx.el.span("AI Powered", class_name="text-[11px] font-semibold text-gray-700"),
                    class_name="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-orange-50 border border-orange-100",
                ),
                rx.el.div(
                    rx.el.span("v1.0", class_name="text-[11px] font-semibold text-gray-700"),
                    class_name="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-100 border border-gray-200",
                ),
                class_name="flex items-center gap-2 flex-wrap",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("shield-check", class_name="h-3.5 w-3.5 text-[#E8471A]"),
                    rx.el.span("Secure · Private · India-focused", class_name="text-[11px] font-medium text-gray-700"),
                    class_name="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-orange-50 border border-orange-100",
                ),
                rx.el.a("Privacy", href="/legal", class_name="text-[11px] text-gray-500 hover:text-[#E8471A] font-medium"),
                rx.el.a("Terms", href="/legal", class_name="text-[11px] text-gray-500 hover:text-[#E8471A] font-medium"),
                rx.el.a("Help", href="/helpline", class_name="text-[11px] text-gray-500 hover:text-[#E8471A] font-medium"),
                class_name="flex items-center gap-3 flex-wrap",
            ),
            class_name="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 px-4 sm:px-6 py-4 max-w-full",
        ),
        class_name="border-t border-gray-200 bg-white",
    )


def app_layout(content: rx.Component, title: str, subtitle: str = "") -> rx.Component:
    return rx.el.div(
        sidebar(),
        mobile_top(),
        rx.el.div(
            header_bar(title, subtitle),
            rx.el.main(
                rx.el.div(
                    content,
                    class_name="dash-shell max-w-[1600px] mx-auto",
                ),
                class_name="flex-1 px-4 sm:px-6 lg:px-8 py-5 sm:py-6 pb-24 lg:pb-6",
            ),
            footer(),
            class_name="flex flex-col min-h-screen lg:ml-64",
        ),
        mobile_tabbar(),
        class_name="min-h-screen bg-[#F8FAFC] font-['Inter'] antialiased",
        on_mount=AuthState.require_auth,
    )