import reflex as rx


def trust_badge(icon: str, label: str) -> rx.Component:
    return rx.el.div(
        rx.icon(
            icon,
            class_name="h-4 w-4 text-orange-500 group-hover:scale-110 transition-transform",
        ),
        rx.el.span(label, class_name="text-xs font-medium text-gray-700"),
        class_name="group inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/80 backdrop-blur-xs border border-orange-100 shadow-xs hover:border-orange-300 hover:bg-white transition-all duration-300",
    )


def hero_dashboard_mockup() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "shield-check", class_name="h-4 w-4 text-white"
                        ),
                        class_name="h-7 w-7 rounded-lg bg-orange-500 flex items-center justify-center",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "FraudRadar",
                            class_name="text-xs font-semibold text-gray-900",
                        ),
                        rx.el.p(
                            "Live Analysis",
                            class_name="text-[10px] text-gray-500",
                        ),
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.div(
                    rx.el.div(
                        class_name="h-2 w-2 rounded-full bg-green-500 animate-pulse"
                    ),
                    rx.el.span(
                        "Active",
                        class_name="text-[10px] font-medium text-green-700",
                    ),
                    class_name="flex items-center gap-1.5 px-2 py-1 rounded-full bg-green-50/50 border border-green-200",
                ),
                class_name="flex items-center justify-between mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Risk Score",
                        class_name="text-[10px] font-semibold text-gray-500 uppercase tracking-wider",
                    ),
                    rx.el.div(
                        rx.el.span(
                            "87", class_name="text-4xl font-bold text-gray-900"
                        ),
                        rx.el.span(
                            "/100", class_name="text-sm text-gray-400 ml-1"
                        ),
                        class_name="flex items-baseline mt-1",
                    ),
                    rx.el.span(
                        "HIGH RISK",
                        class_name="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-red-50 text-red-700 border border-red-200 mt-2 w-fit",
                    ),
                    class_name="flex-1",
                ),
                rx.el.div(
                    rx.icon(
                        "shield-alert", class_name="h-10 w-10 text-red-500"
                    ),
                    class_name="h-16 w-16 rounded-2xl bg-red-50 flex items-center justify-center",
                ),
                class_name="flex items-start justify-between p-4 rounded-xl bg-gradient-to-br from-orange-50 to-white border border-orange-100",
            ),
            rx.el.div(
                rx.el.div(
                    class_name="h-2 rounded-full bg-red-500",
                    custom_attrs={"style": {"width": "87%"}},
                ),
                class_name="w-full h-2 rounded-full bg-gray-100 mt-3",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("flag", class_name="h-3.5 w-3.5 text-red-500"),
                    rx.el.div(
                        rx.el.p(
                            "Phishing URL detected",
                            class_name="text-xs font-semibold text-gray-900",
                        ),
                        rx.el.p(
                            "bit.ly/kyc-verify",
                            class_name="text-[10px] text-gray-500 font-mono",
                        ),
                    ),
                    class_name="flex items-start gap-2 p-2.5 rounded-lg bg-red-50/50 border border-red-100",
                ),
                rx.el.div(
                    rx.icon(
                        "triangle-alert",
                        class_name="h-3.5 w-3.5 text-orange-500",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "OTP request pattern",
                            class_name="text-xs font-semibold text-gray-900",
                        ),
                        rx.el.p(
                            "Asks for banking OTP",
                            class_name="text-[10px] text-gray-500",
                        ),
                    ),
                    class_name="flex items-start gap-2 p-2.5 rounded-lg bg-orange-50/50 border border-orange-100",
                ),
                rx.el.div(
                    rx.icon(
                        "circle-check", class_name="h-3.5 w-3.5 text-green-500"
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Reported to 1930",
                            class_name="text-xs font-semibold text-gray-900",
                        ),
                        rx.el.p(
                            "Action recommended",
                            class_name="text-[10px] text-gray-500",
                        ),
                    ),
                    class_name="flex items-start gap-2 p-2.5 rounded-lg bg-green-50/50 border border-green-100",
                ),
                class_name="flex flex-col gap-2 mt-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Threat Trend",
                        class_name="text-[10px] font-semibold text-gray-500 uppercase tracking-wider",
                    ),
                    rx.el.p(
                        "Last 7 days", class_name="text-[10px] text-gray-400"
                    ),
                    class_name="flex items-center justify-between mb-2",
                ),
                rx.el.div(
                    rx.el.div(
                        class_name="flex-1 h-8 rounded-sm bg-gradient-to-t from-orange-200 to-orange-400",
                        custom_attrs={"style": {"height": "30%"}},
                    ),
                    rx.el.div(
                        class_name="flex-1 h-12 rounded-sm bg-gradient-to-t from-orange-200 to-orange-400",
                        custom_attrs={"style": {"height": "50%"}},
                    ),
                    rx.el.div(
                        class_name="flex-1 h-10 rounded-sm bg-gradient-to-t from-orange-200 to-orange-400",
                        custom_attrs={"style": {"height": "40%"}},
                    ),
                    rx.el.div(
                        class_name="flex-1 h-16 rounded-sm bg-gradient-to-t from-orange-300 to-orange-500",
                        custom_attrs={"style": {"height": "70%"}},
                    ),
                    rx.el.div(
                        class_name="flex-1 h-14 rounded-sm bg-gradient-to-t from-orange-300 to-orange-500",
                        custom_attrs={"style": {"height": "60%"}},
                    ),
                    rx.el.div(
                        class_name="flex-1 h-20 rounded-sm bg-gradient-to-t from-red-300 to-red-500",
                        custom_attrs={"style": {"height": "85%"}},
                    ),
                    rx.el.div(
                        class_name="flex-1 h-24 rounded-sm bg-gradient-to-t from-red-400 to-red-600",
                        custom_attrs={"style": {"height": "95%"}},
                    ),
                    class_name="flex items-end gap-1.5 h-24",
                ),
                class_name="mt-4 p-3 rounded-xl bg-gray-50 border border-gray-100",
            ),
            class_name="relative bg-white/90 backdrop-blur-xl border border-white rounded-2xl p-5 shadow-2xl shadow-orange-200/40 transition-transform duration-500 hover:scale-[1.01]",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("zap", class_name="h-4 w-4 text-orange-500"),
                rx.el.div(
                    rx.el.p(
                        "AI Analysis",
                        class_name="text-[10px] font-semibold text-gray-500",
                    ),
                    rx.el.p(
                        "0.8s", class_name="text-sm font-bold text-gray-900"
                    ),
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="absolute -top-4 -left-4 bg-white border border-orange-100 rounded-xl px-3 py-2 shadow-lg hidden md:block animate-float",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("shield-check", class_name="h-4 w-4 text-green-500"),
                rx.el.div(
                    rx.el.p(
                        "Protected",
                        class_name="text-[10px] font-semibold text-gray-500",
                    ),
                    rx.el.p(
                        "24/7", class_name="text-sm font-bold text-gray-900"
                    ),
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="absolute -bottom-4 -right-4 bg-white border border-green-100 rounded-xl px-3 py-2 shadow-lg hidden md:block animate-float-delayed",
        ),
        class_name="relative animate-float",
    )


def stat_card_landing(value: str, label: str, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                icon,
                class_name="h-5 w-5 text-orange-600 group-hover:rotate-12 transition-transform duration-300",
            ),
            class_name="h-11 w-11 rounded-xl bg-orange-50/80 flex items-center justify-center mb-4 border border-orange-100/50",
        ),
        rx.el.p(
            value,
            class_name="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight",
        ),
        rx.el.p(label, class_name="text-sm text-gray-600 font-medium mt-1"),
        class_name="group bg-white border border-gray-200 rounded-2xl p-6 hover-lift hover:border-orange-300 hover:shadow-lg hover:shadow-orange-100/30 transition-all duration-300",
    )


def feature_card(icon: str, title: str, desc: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                icon,
                class_name="h-5 w-5 text-white group-hover:scale-110 transition-transform duration-300",
            ),
            class_name="h-11 w-11 rounded-xl bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center mb-4 shadow-md shadow-orange-200/50",
        ),
        rx.el.h3(
            title, class_name="text-base font-bold text-gray-900 tracking-tight"
        ),
        rx.el.p(
            desc,
            class_name="text-sm text-gray-600 mt-2 leading-relaxed font-medium",
        ),
        class_name="group bg-white border border-gray-200 rounded-2xl p-6 hover-lift hover:border-orange-300 hover:shadow-xl hover:shadow-orange-100/40 transition-all duration-300",
    )


def step_card(num: str, title: str, desc: str, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                num,
                class_name="h-10 w-10 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 text-white font-extrabold text-sm flex items-center justify-center shadow-md shadow-orange-200/50",
            ),
            rx.el.div(
                rx.icon(
                    icon,
                    class_name="h-5 w-5 text-orange-500 group-hover:scale-110 transition-transform duration-300",
                ),
                class_name="h-10 w-10 rounded-xl bg-orange-50 border border-orange-100 flex items-center justify-center",
            ),
            class_name="flex items-center gap-3 mb-4",
        ),
        rx.el.h3(title, class_name="text-base font-bold text-gray-900"),
        rx.el.p(
            desc,
            class_name="text-sm text-gray-600 mt-2 leading-relaxed font-medium",
        ),
        class_name="group relative bg-white border border-gray-200 rounded-2xl p-6 hover-lift hover:border-orange-300 hover:shadow-lg transition-all duration-300",
    )


def testimonial_card(
    name: str, role: str, quote: str, initial: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.foreach(
                ["star", "star", "star", "star", "star"],
                lambda s: rx.icon(
                    s, class_name="h-4 w-4 text-orange-500 fill-orange-500"
                ),
            ),
            class_name="flex items-center gap-0.5 mb-4",
        ),
        rx.el.p(
            f'"{quote}"',
            class_name="text-sm text-gray-700 leading-relaxed italic font-medium",
        ),
        rx.el.div(
            rx.el.div(
                initial,
                class_name="h-10 w-10 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 text-white font-semibold flex items-center justify-center shadow-xs",
            ),
            rx.el.div(
                rx.el.p(name, class_name="text-sm font-bold text-gray-900"),
                rx.el.p(role, class_name="text-xs text-gray-500 font-medium"),
            ),
            class_name="flex items-center gap-3 mt-6 pt-6 border-t border-gray-100",
        ),
        class_name="bg-white border border-gray-200 rounded-2xl p-6 hover-lift hover:border-orange-300 hover:shadow-lg transition-all duration-300",
    )


def dashboard_preview() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(class_name="h-3 w-3 rounded-full bg-red-400"),
                rx.el.div(class_name="h-3 w-3 rounded-full bg-yellow-400"),
                rx.el.div(class_name="h-3 w-3 rounded-full bg-green-400"),
                class_name="flex items-center gap-1.5",
            ),
            rx.el.p(
                "fraudradar.app/dashboard",
                class_name="text-xs text-gray-500 font-mono",
            ),
            rx.el.div(class_name="w-12"),
            class_name="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50/50",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "shield-check", class_name="h-5 w-5 text-white"
                        ),
                        class_name="h-9 w-9 rounded-lg bg-orange-500 flex items-center justify-center",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "FraudRadar",
                            class_name="text-sm font-semibold text-gray-900",
                        ),
                        rx.el.p(
                            "Dashboard", class_name="text-xs text-gray-500"
                        ),
                    ),
                    class_name="flex items-center gap-3 px-4 h-14 border-b border-gray-200",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "layout-dashboard",
                            class_name="h-4 w-4 text-orange-500",
                        ),
                        rx.el.span(
                            "Dashboard",
                            class_name="text-xs font-medium text-orange-600",
                        ),
                        class_name="flex items-center gap-2 px-3 py-2 rounded-lg bg-orange-50",
                    ),
                    rx.el.div(
                        rx.icon(
                            "scan-search", class_name="h-4 w-4 text-gray-500"
                        ),
                        rx.el.span(
                            "Analyze",
                            class_name="text-xs font-medium text-gray-600",
                        ),
                        class_name="flex items-center gap-2 px-3 py-2 rounded-lg",
                    ),
                    rx.el.div(
                        rx.icon("history", class_name="h-4 w-4 text-gray-500"),
                        rx.el.span(
                            "History",
                            class_name="text-xs font-medium text-gray-600",
                        ),
                        class_name="flex items-center gap-2 px-3 py-2 rounded-lg",
                    ),
                    rx.el.div(
                        rx.icon(
                            "message-circle", class_name="h-4 w-4 text-gray-500"
                        ),
                        rx.el.span(
                            "Assistant",
                            class_name="text-xs font-medium text-gray-600",
                        ),
                        class_name="flex items-center gap-2 px-3 py-2 rounded-lg",
                    ),
                    class_name="flex flex-col gap-1 p-3",
                ),
                class_name="w-48 border-r border-gray-200 bg-white/60 hidden md:block",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Welcome back, Priya",
                            class_name="text-lg font-bold text-gray-900",
                        ),
                        rx.el.p(
                            "Your scam defense overview",
                            class_name="text-xs text-gray-500",
                        ),
                    ),
                    rx.el.div(
                        rx.el.div(
                            "P",
                            class_name="h-8 w-8 rounded-full bg-orange-500 text-white text-xs font-semibold flex items-center justify-center",
                        ),
                        class_name="flex items-center",
                    ),
                    class_name="flex items-center justify-between mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Total Scans",
                            class_name="text-[10px] font-semibold text-gray-500 uppercase",
                        ),
                        rx.el.p(
                            "142",
                            class_name="text-2xl font-bold text-gray-900 mt-1",
                        ),
                        rx.el.p(
                            "+12 this week",
                            class_name="text-[10px] text-green-600 mt-1",
                        ),
                        class_name="bg-white/80 border border-gray-200 rounded-xl p-3",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Scams Blocked",
                            class_name="text-[10px] font-semibold text-gray-500 uppercase",
                        ),
                        rx.el.p(
                            "38",
                            class_name="text-2xl font-bold text-gray-900 mt-1",
                        ),
                        rx.el.p(
                            "+5 this week",
                            class_name="text-[10px] text-orange-600 mt-1",
                        ),
                        class_name="bg-white/80 border border-gray-200 rounded-xl p-3",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Avg Risk",
                            class_name="text-[10px] font-semibold text-gray-500 uppercase",
                        ),
                        rx.el.p(
                            "42%",
                            class_name="text-2xl font-bold text-gray-900 mt-1",
                        ),
                        rx.el.p(
                            "Medium",
                            class_name="text-[10px] text-yellow-600 mt-1",
                        ),
                        class_name="bg-white/80 border border-gray-200 rounded-xl p-3",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Latest",
                            class_name="text-[10px] font-semibold text-gray-500 uppercase",
                        ),
                        rx.el.p(
                            "HIGH",
                            class_name="text-2xl font-bold text-red-600 mt-1",
                        ),
                        rx.el.p(
                            "UPI scam",
                            class_name="text-[10px] text-gray-500 mt-1",
                        ),
                        class_name="bg-white/80 border border-gray-200 rounded-xl p-3",
                    ),
                    class_name="grid grid-cols-2 lg:grid-cols-4 gap-3",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Risk Activity",
                            class_name="text-xs font-semibold text-gray-700 mb-3",
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name="flex-1 rounded-sm bg-gradient-to-t from-orange-200 to-orange-400",
                                custom_attrs={"style": {"height": "40%"}},
                            ),
                            rx.el.div(
                                class_name="flex-1 rounded-sm bg-gradient-to-t from-orange-200 to-orange-400",
                                custom_attrs={"style": {"height": "60%"}},
                            ),
                            rx.el.div(
                                class_name="flex-1 rounded-sm bg-gradient-to-t from-orange-300 to-orange-500",
                                custom_attrs={"style": {"height": "75%"}},
                            ),
                            rx.el.div(
                                class_name="flex-1 rounded-sm bg-gradient-to-t from-orange-200 to-orange-400",
                                custom_attrs={"style": {"height": "50%"}},
                            ),
                            rx.el.div(
                                class_name="flex-1 rounded-sm bg-gradient-to-t from-red-300 to-red-500",
                                custom_attrs={"style": {"height": "90%"}},
                            ),
                            rx.el.div(
                                class_name="flex-1 rounded-sm bg-gradient-to-t from-orange-300 to-orange-500",
                                custom_attrs={"style": {"height": "65%"}},
                            ),
                            rx.el.div(
                                class_name="flex-1 rounded-sm bg-gradient-to-t from-orange-200 to-orange-400",
                                custom_attrs={"style": {"height": "55%"}},
                            ),
                            class_name="flex items-end gap-2 h-24",
                        ),
                        class_name="bg-white/80 border border-gray-200 rounded-xl p-4 col-span-2",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Verdict Split",
                            class_name="text-xs font-semibold text-gray-700 mb-3",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    class_name="h-2 w-2 rounded-full bg-green-500"
                                ),
                                rx.el.span(
                                    "Safe",
                                    class_name="text-xs text-gray-600 flex-1",
                                ),
                                rx.el.span(
                                    "64",
                                    class_name="text-xs font-semibold text-gray-900",
                                ),
                                class_name="flex items-center gap-2",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    class_name="h-2 w-2 rounded-full bg-yellow-500"
                                ),
                                rx.el.span(
                                    "Medium",
                                    class_name="text-xs text-gray-600 flex-1",
                                ),
                                rx.el.span(
                                    "40",
                                    class_name="text-xs font-semibold text-gray-900",
                                ),
                                class_name="flex items-center gap-2",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    class_name="h-2 w-2 rounded-full bg-red-500"
                                ),
                                rx.el.span(
                                    "High",
                                    class_name="text-xs text-gray-600 flex-1",
                                ),
                                rx.el.span(
                                    "38",
                                    class_name="text-xs font-semibold text-gray-900",
                                ),
                                class_name="flex items-center gap-2",
                            ),
                            class_name="flex flex-col gap-2",
                        ),
                        class_name="bg-white/80 border border-gray-200 rounded-xl p-4",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3",
                ),
                class_name="flex-1 p-4 bg-gray-50/40 overflow-hidden",
            ),
            class_name="flex h-[480px]",
        ),
        class_name="bg-white/70 backdrop-blur-xl border border-gray-200 rounded-2xl overflow-hidden shadow-2xl shadow-orange-100/50",
    )


def landing_footer() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "shield-check", class_name="h-5 w-5 text-white"
                        ),
                        class_name="h-9 w-9 rounded-lg bg-orange-500 flex items-center justify-center",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "FraudRadar",
                            class_name="text-sm font-semibold text-gray-900",
                        ),
                        rx.el.p(
                            "Scam Defense AI",
                            class_name="text-xs text-gray-500",
                        ),
                    ),
                    class_name="flex items-center gap-3",
                ),
                rx.el.p(
                    "AI-powered scam detection for safer digital India. Protecting users from UPI fraud, OTP scams, and phishing attacks in real-time.",
                    class_name="text-sm text-gray-600 mt-4 leading-relaxed max-w-sm",
                ),
                class_name="md:col-span-2",
            ),
            rx.el.div(
                rx.el.p(
                    "Product",
                    class_name="text-xs font-semibold text-gray-900 uppercase tracking-wider mb-3",
                ),
                rx.el.a(
                    "About",
                    href="#about",
                    class_name="block text-sm text-gray-600 hover:text-orange-500 py-1",
                ),
                rx.el.a(
                    "Features",
                    href="#features",
                    class_name="block text-sm text-gray-600 hover:text-orange-500 py-1",
                ),
                rx.el.a(
                    "How it works",
                    href="#how",
                    class_name="block text-sm text-gray-600 hover:text-orange-500 py-1",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    "Resources",
                    class_name="text-xs font-semibold text-gray-900 uppercase tracking-wider mb-3",
                ),
                rx.el.a(
                    "Privacy Policy",
                    href="/legal",
                    class_name="block text-sm text-gray-600 hover:text-orange-500 py-1",
                ),
                rx.el.a(
                    "Contact",
                    href="mailto:hello@fraudradar.app",
                    class_name="block text-sm text-gray-600 hover:text-orange-500 py-1",
                ),
                rx.el.a(
                    rx.el.span(
                        "GitHub", class_name="inline-flex items-center gap-1"
                    ),
                    href="https://github.com",
                    target="_blank",
                    class_name="block text-sm text-gray-600 hover:text-orange-500 py-1",
                ),
            ),
            class_name="grid grid-cols-2 md:grid-cols-4 gap-8 px-6 py-12 max-w-7xl mx-auto",
        ),
        rx.el.div(
            rx.el.p(
                "© 2026 FraudRadar. Built with care.",
                class_name="text-xs text-gray-500",
            ),
            rx.el.div(
                rx.icon(
                    "shield-check", class_name="h-3.5 w-3.5 text-orange-500"
                ),
                rx.el.span(
                    "AI-powered scam defense",
                    class_name="text-xs font-medium text-gray-700",
                ),
                class_name="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-50 border border-orange-200",
            ),
            class_name="flex flex-col sm:flex-row items-center justify-between gap-3 px-6 py-6 border-t border-gray-200 max-w-7xl mx-auto",
        ),
        class_name="bg-white border-t border-gray-200",
    )


def landing_nav() -> rx.Component:
    return rx.el.nav(
        rx.el.div(
            rx.el.a(
                rx.el.div(
                    rx.icon("shield-check", class_name="h-5 w-5 text-white"),
                    class_name="h-9 w-9 rounded-lg bg-orange-500 flex items-center justify-center",
                ),
                rx.el.div(
                    rx.el.p(
                        "FraudRadar",
                        class_name="text-sm font-semibold text-gray-900",
                    ),
                    rx.el.p(
                        "Scam Defense AI",
                        class_name="text-[10px] text-gray-500",
                    ),
                ),
                href="/",
                class_name="flex items-center gap-3",
            ),
            rx.el.div(
                rx.el.a(
                    "Features",
                    href="#features",
                    class_name="text-sm font-medium text-gray-700 hover:text-orange-500",
                ),
                rx.el.a(
                    "How it works",
                    href="#how",
                    class_name="text-sm font-medium text-gray-700 hover:text-orange-500",
                ),
                rx.el.a(
                    "Testimonials",
                    href="#testimonials",
                    class_name="text-sm font-medium text-gray-700 hover:text-orange-500",
                ),
                class_name="hidden md:flex items-center gap-8",
            ),
            rx.el.div(
                rx.el.a(
                    "Sign In",
                    href="/login",
                    class_name="text-sm font-medium text-gray-700 hover:text-orange-500 px-4 py-2",
                ),
                rx.el.a(
                    "Get Started",
                    href="/signup",
                    class_name="text-sm font-medium text-white bg-orange-500 hover:bg-orange-600 px-4 py-2 rounded-lg shadow-md shadow-orange-200 transition-colors",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto",
        ),
        class_name="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200/60",
    )


def landing_page() -> rx.Component:
    return rx.el.div(
        landing_nav(),
        # HERO
        rx.el.section(
            rx.el.div(
                class_name="absolute inset-0 bg-gradient-to-br from-orange-50 via-white to-white pointer-events-none",
            ),
            rx.el.div(
                class_name="absolute top-0 right-0 w-[500px] h-[500px] bg-orange-200/30 rounded-full blur-3xl pointer-events-none animate-pulse-slow",
            ),
            rx.el.div(
                class_name="absolute bottom-0 left-0 w-[400px] h-[400px] bg-orange-100/40 rounded-full blur-3xl pointer-events-none animate-pulse-slow",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "sparkles",
                            class_name="h-3.5 w-3.5 text-orange-500 animate-spin-slow",
                        ),
                        rx.el.span(
                            "AI-Powered Scam Defense for India",
                            class_name="text-xs font-semibold text-gray-700",
                        ),
                        class_name="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/80 border border-orange-200 shadow-xs w-fit animate-fade-in",
                    ),
                    rx.el.h1(
                        "Detect Online Scams Before They Harm You",
                        class_name="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-gray-900 mt-6 leading-[1.1] tracking-tight animate-fade-in-delayed-1",
                    ),
                    rx.el.p(
                        "FraudRadar uses advanced AI to analyze suspicious messages, links, and calls in seconds. Stay one step ahead of UPI fraud, OTP scams, and phishing attacks targeting Indian users.",
                        class_name="text-base sm:text-lg text-gray-600 mt-6 leading-relaxed max-w-xl font-medium animate-fade-in-delayed-2",
                    ),
                    rx.el.div(
                        rx.el.a(
                            rx.el.span("Get Started", class_name="font-bold"),
                            rx.icon(
                                "arrow-right",
                                class_name="h-4 w-4 transition-transform group-hover:translate-x-1",
                            ),
                            href="/signup",
                            class_name="group inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-orange-500 text-white hover:bg-orange-600 shadow-lg shadow-orange-200 hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all focus:ring-2 focus:ring-orange-500 focus:outline-hidden",
                        ),
                        rx.el.a(
                            "Sign In",
                            href="/login",
                            class_name="inline-flex items-center justify-center px-6 py-3.5 rounded-xl bg-white border border-gray-300 text-gray-900 font-bold hover:border-orange-300 hover:bg-orange-50/50 hover:scale-[1.02] active:scale-[0.98] transition-all focus:ring-2 focus:ring-orange-500 focus:outline-hidden",
                        ),
                        class_name="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mt-8 animate-fade-in-delayed-2",
                    ),
                    rx.el.div(
                        trust_badge("brain-circuit", "AI Powered"),
                        trust_badge("map-pin", "India Focused"),
                        trust_badge("zap", "Real-Time Detection"),
                        trust_badge("lock", "Secure Authentication"),
                        class_name="flex flex-wrap items-center gap-2 mt-8 animate-fade-in-delayed-2",
                    ),
                    class_name="flex flex-col",
                ),
                rx.el.div(
                    hero_dashboard_mockup(),
                    class_name="relative animate-fade-in-delayed-1",
                ),
                class_name="relative grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center max-w-7xl mx-auto px-6 py-12 sm:py-16 lg:py-24",
            ),
            class_name="relative overflow-hidden",
        ),
        # STATS
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Trusted by safety-conscious Indians",
                        class_name="text-2xl sm:text-3xl font-bold text-gray-900 text-center",
                    ),
                    rx.el.p(
                        "Real impact, real protection.",
                        class_name="text-sm text-gray-600 text-center mt-2",
                    ),
                    class_name="mb-10",
                ),
                rx.el.div(
                    stat_card_landing("50K+", "Scans Performed", "scan-search"),
                    stat_card_landing("12K+", "Scams Blocked", "shield-alert"),
                    stat_card_landing("99.2%", "Accuracy Rate", "target"),
                    stat_card_landing("0.8s", "Avg Response", "zap"),
                    class_name="grid grid-cols-2 lg:grid-cols-4 gap-4",
                ),
                class_name="max-w-7xl mx-auto px-6 py-16",
            ),
            class_name="bg-white",
        ),
        # FEATURES
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "FEATURES",
                        class_name="inline-block text-xs font-semibold text-orange-500 uppercase tracking-widest",
                    ),
                    rx.el.h2(
                        "Everything you need to stay scam-free",
                        class_name="text-3xl sm:text-4xl font-bold text-gray-900 mt-3 max-w-2xl",
                    ),
                    rx.el.p(
                        "Built specifically for the Indian threat landscape with AI trained on local fraud patterns.",
                        class_name="text-base text-gray-600 mt-4 max-w-2xl",
                    ),
                    class_name="mb-12 text-center mx-auto",
                ),
                rx.el.div(
                    feature_card(
                        "scan-search",
                        "Instant Message Analysis",
                        "Paste any SMS, WhatsApp, or email and get a risk score in under a second.",
                    ),
                    feature_card(
                        "link",
                        "URL Phishing Detection",
                        "Verify suspicious links before you click—catch fake KYC and banking sites.",
                    ),
                    feature_card(
                        "brain-circuit",
                        "AI-Powered Insights",
                        "Powered by Groq's lightning-fast LLM tuned for Indian scam patterns.",
                    ),
                    feature_card(
                        "message-circle",
                        "Safety Assistant",
                        "Chat with our AI assistant for personalized fraud safety guidance.",
                    ),
                    feature_card(
                        "history",
                        "Scan History",
                        "Review every analyzed message with full risk breakdown and timestamps.",
                    ),
                    feature_card(
                        "phone-call",
                        "1930 Helpline Access",
                        "One-tap escalation to India's National Cyber Crime helpline.",
                    ),
                    feature_card(
                        "shield-check",
                        "Privacy First",
                        "End-to-end encrypted, DPDP-compliant, your data stays yours.",
                    ),
                    feature_card(
                        "bell",
                        "Real-Time Alerts",
                        "Get notified about trending scams and emerging fraud patterns.",
                    ),
                    class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4",
                ),
                class_name="max-w-7xl mx-auto px-6 py-20",
                id="features",
            ),
            class_name="bg-gradient-to-b from-orange-50/30 to-white",
        ),
        # HOW IT WORKS
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "HOW IT WORKS",
                        class_name="inline-block text-xs font-semibold text-orange-500 uppercase tracking-widest",
                    ),
                    rx.el.h2(
                        "From suspicious to safe in 4 steps",
                        class_name="text-3xl sm:text-4xl font-bold text-gray-900 mt-3",
                    ),
                    rx.el.p(
                        "A frictionless workflow designed to protect you in seconds.",
                        class_name="text-base text-gray-600 mt-4 max-w-2xl mx-auto",
                    ),
                    class_name="text-center mb-12",
                ),
                rx.el.div(
                    step_card(
                        "01",
                        "Sign Up Securely",
                        "Create your free FraudRadar account with email or Google.",
                        "user-plus",
                    ),
                    step_card(
                        "02",
                        "Paste Suspicious Content",
                        "Drop in the SMS, link, or message you want to verify.",
                        "clipboard-paste",
                    ),
                    step_card(
                        "03",
                        "Get AI Verdict",
                        "Receive a risk score, red flags, and recommended actions instantly.",
                        "sparkles",
                    ),
                    step_card(
                        "04",
                        "Take Safe Action",
                        "Report, block, or call 1930 with one tap—stay protected.",
                        "shield-check",
                    ),
                    class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4",
                ),
                class_name="max-w-7xl mx-auto px-6 py-20",
                id="how",
            ),
            class_name="bg-white",
        ),
        # DASHBOARD PREVIEW
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "DASHBOARD PREVIEW",
                        class_name="inline-block text-xs font-semibold text-orange-500 uppercase tracking-widest",
                    ),
                    rx.el.h2(
                        "A clear view of your defense",
                        class_name="text-3xl sm:text-4xl font-bold text-gray-900 mt-3",
                    ),
                    rx.el.p(
                        "Track every scan, monitor risk trends, and stay informed.",
                        class_name="text-base text-gray-600 mt-4 max-w-2xl mx-auto",
                    ),
                    class_name="text-center mb-12",
                ),
                dashboard_preview(),
                class_name="max-w-6xl mx-auto px-6 py-20",
            ),
            class_name="bg-gradient-to-b from-white to-orange-50/30",
        ),
        # TESTIMONIALS
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "TESTIMONIALS",
                        class_name="inline-block text-xs font-semibold text-orange-500 uppercase tracking-widest",
                    ),
                    rx.el.h2(
                        "Loved by users across India",
                        class_name="text-3xl sm:text-4xl font-bold text-gray-900 mt-3",
                    ),
                    class_name="text-center mb-12",
                ),
                rx.el.div(
                    testimonial_card(
                        "Priya Sharma",
                        "Software Engineer, Mumbai",
                        "FraudRadar caught a fake KYC SMS that almost tricked me. The AI explanation was clear and actionable. A must-have for every Indian.",
                        "P",
                    ),
                    testimonial_card(
                        "Rajesh Kumar",
                        "Small Business Owner, Delhi",
                        "I get suspicious UPI requests daily. FraudRadar tells me which ones are real in seconds. It saved my business from a payment scam.",
                        "R",
                    ),
                    testimonial_card(
                        "Ananya Iyer",
                        "Student, Bangalore",
                        "The assistant helped me understand a job offer scam I almost fell for. The interface is so clean and the responses are super helpful.",
                        "A",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-3 gap-4",
                ),
                class_name="max-w-7xl mx-auto px-6 py-20",
                id="testimonials",
            ),
            class_name="bg-white",
        ),
        # CTA
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        class_name="absolute inset-0 bg-gradient-to-br from-orange-400 via-orange-500 to-orange-600 rounded-3xl",
                    ),
                    rx.el.div(
                        class_name="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl",
                    ),
                    rx.el.div(
                        class_name="absolute bottom-0 left-0 w-64 h-64 bg-orange-300/30 rounded-full blur-3xl",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "shield-check",
                                class_name="h-7 w-7 text-orange-500",
                            ),
                            class_name="h-14 w-14 rounded-2xl bg-white flex items-center justify-center mx-auto shadow-xl",
                        ),
                        rx.el.h2(
                            "Start protecting yourself today",
                            class_name="text-3xl sm:text-4xl font-bold text-white mt-6 text-center max-w-2xl mx-auto",
                        ),
                        rx.el.p(
                            "Join thousands of safety-conscious Indians using FraudRadar to stay ahead of scams. Free to start, no credit card required.",
                            class_name="text-base text-orange-50 mt-4 text-center max-w-xl mx-auto",
                        ),
                        rx.el.div(
                            rx.el.a(
                                rx.icon("scan-search", class_name="h-4 w-4"),
                                rx.el.span(
                                    "Scan Now", class_name="font-semibold"
                                ),
                                href="/analyze",
                                class_name="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-white text-orange-600 hover:bg-orange-50 shadow-lg hover:-translate-y-0.5 transition-all",
                            ),
                            rx.el.a(
                                rx.el.span(
                                    "Create Account", class_name="font-semibold"
                                ),
                                rx.icon("arrow-right", class_name="h-4 w-4"),
                                href="/signup",
                                class_name="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-orange-700/30 backdrop-blur-xl text-white border border-white/30 hover:bg-orange-700/50 transition-all",
                            ),
                            class_name="flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-3 mt-8",
                        ),
                        class_name="relative px-6 py-16 sm:py-20",
                    ),
                    class_name="relative overflow-hidden rounded-3xl",
                ),
                class_name="max-w-6xl mx-auto px-6 py-12",
            ),
            class_name="bg-white",
        ),
        landing_footer(),
        class_name="min-h-screen bg-white font-['Inter'] antialiased",
    )