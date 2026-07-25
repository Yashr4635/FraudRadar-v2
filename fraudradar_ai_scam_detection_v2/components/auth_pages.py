import reflex as rx
from fraudradar_ai_scam_detection_v2.states.auth_state import AuthState
from fraudradar_ai_scam_detection_v2.states.reset_password_state import ResetPasswordState

def _floating_bg_accents() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            class_name="absolute -top-24 -left-24 w-80 h-80 rounded-full bg-white/10 blur-3xl animate-pulse-slow"
        ),
        rx.el.div(
            class_name="absolute top-1/3 -right-20 w-72 h-72 rounded-full bg-orange-300/30 blur-3xl animate-pulse-slow"
        ),
        rx.el.div(
            class_name="absolute bottom-0 left-1/4 w-96 h-96 rounded-full bg-white/5 blur-3xl animate-pulse-slow"
        ),
        rx.el.div(
            rx.icon("shield", class_name="h-32 w-32 text-white/5"),
            class_name="absolute top-10 right-20 animate-float",
        ),
        rx.el.div(
            rx.icon("lock", class_name="h-20 w-20 text-white/5"),
            class_name="absolute bottom-32 left-12 animate-float-delayed",
        ),
        rx.el.div(
            rx.icon("shield-check", class_name="h-16 w-16 text-white/10"),
            class_name="absolute top-1/2 left-1/3 animate-float",
        ),
        rx.el.div(
            class_name="absolute inset-0 opacity-10",
            custom_attrs={
                "style": {
                    "backgroundImage": "radial-gradient(circle at 1px 1px, white 1px, transparent 0)",
                    "backgroundSize": "32px 32px",
                }
            },
        ),
        class_name="absolute inset-0 overflow-hidden pointer-events-none",
    )


def _ai_shield_illustration() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                class_name="absolute inset-0 rounded-full bg-white/10 animate-pulse-slow"
            ),
            rx.el.div(
                class_name="absolute inset-3 rounded-full border border-white/20 animate-spin-slow"
            ),
            rx.el.div(
                class_name="absolute inset-6 rounded-full border border-dashed border-white/30"
            ),
            rx.el.div(
                rx.icon("shield-check", class_name="h-14 w-14 text-white drop-shadow-lg"),
                class_name="relative h-24 w-24 rounded-full bg-gradient-to-br from-white/30 to-white/10 backdrop-blur-xl border border-white/40 flex items-center justify-center shadow-2xl",
            ),
            rx.el.div(
                rx.icon("zap", class_name="h-4 w-4 text-orange-500"),
                class_name="absolute -top-2 -right-2 h-9 w-9 rounded-full bg-white shadow-lg flex items-center justify-center animate-float",
            ),
            rx.el.div(
                rx.icon("brain-circuit", class_name="h-4 w-4 text-orange-500"),
                class_name="absolute -bottom-2 -left-2 h-9 w-9 rounded-full bg-white shadow-lg flex items-center justify-center animate-float-delayed",
            ),
            rx.el.div(
                rx.icon("lock", class_name="h-3.5 w-3.5 text-orange-500"),
                class_name="absolute top-1/2 -right-6 h-8 w-8 rounded-full bg-white shadow-lg flex items-center justify-center animate-float",
            ),
            class_name="relative h-44 w-44 flex items-center justify-center",
        ),
        class_name="flex items-center justify-center mb-6",
    )


def _glass_feature(icon: str, title: str, desc: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 text-white"),
            class_name="h-9 w-9 rounded-xl bg-white/20 backdrop-blur border border-white/30 flex items-center justify-center mb-2.5 shrink-0",
        ),
        rx.el.p(title, class_name="text-sm font-bold text-white"),
        rx.el.p(desc, class_name="text-[11px] text-white/75 mt-0.5 leading-snug"),
        class_name="rounded-xl bg-white/10 backdrop-blur-md border border-white/20 p-3 hover:bg-white/15 hover:border-white/30 transition-all duration-300 hover:-translate-y-0.5",
    )


def _stat_pill(value: str, label: str, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-3.5 w-3.5 text-white"),
            class_name="h-7 w-7 rounded-lg bg-white/20 flex items-center justify-center shrink-0",
        ),
        rx.el.div(
            rx.el.p(value, class_name="text-base font-extrabold text-white leading-tight"),
            rx.el.p(label, class_name="text-[10px] font-medium text-white/70 leading-tight"),
        ),
        class_name="flex items-center gap-2 rounded-lg bg-white/10 backdrop-blur border border-white/15 px-2.5 py-1.5",
    )


def _trust_chip(icon: str, label: str) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-3 w-3 text-white"),
        rx.el.span(label, class_name="text-[11px] font-semibold text-white"),
        class_name="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/15 backdrop-blur border border-white/25",
    )


def login_marketing_panel() -> rx.Component:
    return rx.el.div(
        _floating_bg_accents(),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("shield-check", class_name="h-6 w-6 text-white"),
                    class_name="h-12 w-12 rounded-2xl bg-white/20 backdrop-blur border border-white/30 flex items-center justify-center shadow-lg",
                ),
                rx.el.div(
                    rx.el.p("FraudRadar", class_name="text-lg font-bold text-white tracking-tight"),
                    rx.el.p("Scam Defense AI", class_name="text-[11px] text-white/70 font-medium"),
                ),
                class_name="flex items-center gap-3",
            ),
            _ai_shield_illustration(),
            rx.el.h2(
                "Protect Yourself from Digital Fraud with AI",
                class_name="text-3xl xl:text-4xl font-extrabold text-white leading-[1.15] tracking-tight",
            ),
            rx.el.p(
                "Instantly analyze scam messages, phishing websites, suspicious phone numbers, and fraudulent emails — purpose-built for India's threat landscape.",
                class_name="text-sm text-white/85 leading-relaxed mt-3 max-w-md",
            ),
            rx.el.div(
                _glass_feature("scan-search", "AI Scam Detection", "Real-time risk scoring on any text"),
                _glass_feature("globe", "URL Scanner", "Spot phishing links before you click"),
                _glass_feature("phone", "Phone Verification", "Check numbers for known scams"),
                _glass_feature("sparkles", "AI Assistant", "24×7 fraud safety guidance"),
                class_name="grid grid-cols-2 gap-2.5 mt-6",
            ),
            rx.el.div(
                _stat_pill("98%", "Detection Accuracy", "target"),
                _stat_pill("25K+", "Scans Performed", "scan-search"),
                _stat_pill("24/7", "Protection", "shield"),
                _stat_pill("AI", "Powered Analysis", "brain-circuit"),
                class_name="grid grid-cols-2 gap-2 mt-4",
            ),
            rx.el.div(
                _trust_chip("lock", "Secure Authentication"),
                _trust_chip("key-round", "End-to-End Encryption"),
                _trust_chip("shield-check", "Privacy First"),
                _trust_chip("map-pin", "India-Focused"),
                class_name="flex flex-wrap gap-1.5 mt-5",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("quote", class_name="h-4 w-4 text-white/60"),
                    rx.el.div(
                        rx.foreach(
                            ["star", "star", "star", "star", "star"],
                            lambda s: rx.icon(s, class_name="h-3 w-3 text-yellow-300 fill-yellow-300"),
                        ),
                        class_name="flex items-center gap-0.5 ml-auto",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.p(
                    '"FraudRadar caught a fake KYC SMS that almost tricked me. The AI explanation was crystal clear."',
                    class_name="text-sm text-white/95 italic mt-2 leading-relaxed",
                ),
                rx.el.div(
                    rx.el.div(
                        "P",
                        class_name="h-8 w-8 rounded-full bg-white text-orange-600 flex items-center justify-center text-xs font-bold shrink-0",
                    ),
                    rx.el.div(
                        rx.el.p("Priya Sharma", class_name="text-xs font-bold text-white"),
                        rx.el.p("Software Engineer · Mumbai", class_name="text-[10px] text-white/70"),
                    ),
                    class_name="flex items-center gap-2 mt-3",
                ),
                class_name="mt-5 p-4 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20",
            ),
            class_name="relative max-w-md w-full",
        ),
        class_name="hidden lg:flex relative overflow-hidden bg-gradient-to-br from-[#E8471A] via-[#d63d12] to-[#a82e0d] p-10 xl:p-12 items-center justify-center lg:basis-[55%]",
    )


def marketing_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("shield-check", class_name="h-6 w-6 text-white"),
                class_name="h-11 w-11 rounded-xl bg-white/15 flex items-center justify-center",
            ),
            rx.el.h2("FraudRadar", class_name="text-2xl font-bold text-white mt-6"),
            rx.el.p(
                "AI-powered scam defense designed for India.",
                class_name="text-white/80 text-sm mt-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("zap", class_name="h-4 w-4 text-white"),
                    rx.el.p("Real-time message & link analysis", class_name="text-sm text-white/90"),
                    class_name="flex items-center gap-3",
                ),
                rx.el.div(
                    rx.icon("lock", class_name="h-4 w-4 text-white"),
                    rx.el.p("Private & secure—your data stays yours", class_name="text-sm text-white/90"),
                    class_name="flex items-center gap-3",
                ),
                rx.el.div(
                    rx.icon("users", class_name="h-4 w-4 text-white"),
                    rx.el.p("Trusted by safety-conscious Indians", class_name="text-sm text-white/90"),
                    class_name="flex items-center gap-3",
                ),
                class_name="flex flex-col gap-4 mt-10",
            ),
            rx.el.div(
                rx.el.p('"Saved me from a fake KYC scam last week."', class_name="text-white/90 text-sm italic"),
                rx.el.p("— Priya, Mumbai", class_name="text-white/70 text-xs mt-2"),
                class_name="mt-12 p-4 rounded-xl bg-white/10 border border-white/20",
            ),
            class_name="max-w-sm",
        ),
        class_name="hidden lg:flex flex-1 bg-gradient-to-br from-[#E8471A] to-[#c43a13] p-12 items-center justify-center",
    )


def auth_input(
    label: str,
    name: str,
    value,
    placeholder: str,
    type_: str,
    on_change,
    icon: str,
) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-gray-700 mb-1.5"),
        rx.el.div(
            rx.icon(icon, class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400"),
            rx.el.input(
                name=name,
                type=type_,
                placeholder=placeholder,
                default_value=value,
                on_change=on_change.debounce(200),
                class_name="w-full pl-10 pr-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm text-gray-900 placeholder-gray-400 focus:outline-hidden focus:ring-2 focus:ring-[#E8471A] focus:border-transparent",
            ),
            class_name="relative",
        ),
        class_name="w-full",
    )


def message_alert() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.auth_error != "",
            rx.el.div(
                rx.icon("circle-alert", class_name="h-4 w-4 text-red-600"),
                rx.el.p(AuthState.auth_error, class_name="text-sm text-red-700"),
                class_name="flex items-center gap-2 p-3 rounded-lg bg-red-50 border border-red-200 mb-4",
            ),
            rx.fragment(),
        ),
        rx.cond(
            AuthState.auth_success != "",
            rx.el.div(
                rx.icon("circle-check", class_name="h-4 w-4 text-green-600"),
                rx.el.p(AuthState.auth_success, class_name="text-sm text-green-700"),
                class_name="flex items-center gap-2 p-3 rounded-lg bg-green-50 border border-green-200 mb-4",
            ),
            rx.fragment(),
        ),
    )


def _login_input(
    label: str,
    placeholder: str,
    value,
    on_change,
    icon: str,
    type_: str = "text",
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label,
            class_name="block text-xs font-semibold text-gray-700 mb-1.5 tracking-wide",
        ),
        rx.el.div(
            rx.icon(
                icon,
                class_name="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 group-focus-within:text-[#E8471A] transition-colors",
            ),
            rx.el.input(
                type=type_,
                placeholder=placeholder,
                default_value=value,
                on_change=on_change.debounce(200),
                class_name="w-full pl-11 pr-3 py-3 rounded-xl border border-gray-200 bg-gray-50/60 text-sm text-gray-900 placeholder-gray-400 focus:outline-hidden focus:ring-4 focus:ring-orange-500/15 focus:border-[#E8471A] focus:bg-white transition-all",
            ),
            class_name="group relative",
        ),
    )


def forgot_password_modal() -> rx.Component:
    return rx.cond(
        AuthState.show_forgot_modal,
        rx.el.div(
            rx.el.div(
                on_click=AuthState.close_forgot_modal,
                class_name="absolute inset-0 bg-black/50 backdrop-blur-sm",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("key-round", class_name="h-5 w-5 text-white"),
                        class_name="h-11 w-11 rounded-2xl bg-gradient-to-br from-[#E8471A] to-[#c43a13] flex items-center justify-center shadow-lg shadow-orange-200/60",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4 text-gray-500"),
                        on_click=AuthState.close_forgot_modal,
                        type="button",
                        class_name="h-8 w-8 rounded-lg hover:bg-gray-100 flex items-center justify-center",
                    ),
                    class_name="flex items-start justify-between",
                ),
                rx.el.h3("Reset your password", class_name="text-lg font-bold text-gray-900 mt-4"),
                rx.el.p(
                    "Enter your account email and we'll send you a secure password reset link.",
                    class_name="text-sm text-gray-500 mt-1 leading-relaxed",
                ),
                rx.cond(
                    AuthState.forgot_error != "",
                    rx.el.div(
                        rx.icon("circle-alert", class_name="h-3.5 w-3.5 text-red-600"),
                        rx.el.p(AuthState.forgot_error, class_name="text-xs font-semibold text-red-700"),
                        class_name="flex items-center gap-1.5 mt-3 p-2.5 rounded-lg bg-red-50 border border-red-200",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    AuthState.forgot_success != "",
                    rx.el.div(
                        rx.icon("circle-check", class_name="h-3.5 w-3.5 text-green-600"),
                        rx.el.p(AuthState.forgot_success, class_name="text-xs font-semibold text-green-700"),
                        class_name="flex items-center gap-1.5 mt-3 p-2.5 rounded-lg bg-green-50 border border-green-200",
                    ),
                    rx.fragment(),
                ),
                rx.el.div(
                    rx.el.label(
                        "Email Address",
                        class_name="block text-xs font-bold text-gray-700 mb-1.5 uppercase tracking-wider",
                    ),
                    rx.el.div(
                        rx.icon("mail", class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400"),
                        rx.el.input(
                            type="email",
                            placeholder="you@example.com",
                            default_value=AuthState.forgot_email,
                            on_change=AuthState.set_forgot_email.debounce(200),
                            class_name="w-full pl-10 pr-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm focus:outline-hidden focus:ring-2 focus:ring-[#E8471A]",
                        ),
                        class_name="relative",
                    ),
                    class_name="mt-4",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        type="button",
                        on_click=AuthState.close_forgot_modal,
                        class_name="flex-1 px-4 py-2.5 rounded-lg border border-gray-300 text-gray-700 text-sm font-bold hover:bg-gray-50",
                    ),
                    rx.el.button(
                        rx.cond(
                            AuthState.forgot_loading,
                            rx.fragment(
                                rx.icon("loader-circle", class_name="h-3.5 w-3.5 animate-spin"),
                                rx.el.span("Sending..."),
                            ),
                            rx.fragment(
                                rx.icon("send", class_name="h-3.5 w-3.5"),
                                rx.el.span("Send reset link"),
                            ),
                        ),
                        type="button",
                        on_click=AuthState.send_password_reset,
                        disabled=AuthState.forgot_loading,
                        class_name="flex-1 inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-lg bg-[#E8471A] text-white text-sm font-bold hover:bg-[#c43a13] disabled:opacity-60",
                    ),
                    class_name="flex items-center gap-2 mt-5",
                ),
                rx.el.div(
                    rx.icon("shield-check", class_name="h-3 w-3 text-green-600"),
                    rx.el.span(
                        "Reset links expire in 1 hour for your security.",
                        class_name="text-[10px] text-gray-500 font-medium",
                    ),
                    class_name="flex items-center gap-1.5 justify-center mt-4",
                ),
                class_name="relative bg-white rounded-2xl shadow-2xl p-6 max-w-md w-full mx-4",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center",
        ),
        rx.fragment(),
    )


def login_page() -> rx.Component:
    return rx.el.div(
        forgot_password_modal(),
        login_marketing_panel(),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("shield-check", class_name="h-5 w-5 text-white"),
                        class_name="h-11 w-11 rounded-2xl bg-gradient-to-br from-[#E8471A] to-[#c43a13] flex items-center justify-center lg:hidden shadow-lg shadow-orange-200/60",
                    ),
                    rx.el.div(
                        rx.el.p("FraudRadar", class_name="text-sm font-bold text-gray-900 lg:hidden"),
                        rx.el.p("Scam Defense AI", class_name="text-[10px] text-gray-500 font-medium lg:hidden"),
                    ),
                    class_name="flex items-center gap-3 lg:hidden mb-8",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(class_name="h-2 w-2 rounded-full bg-green-500 animate-pulse"),
                        rx.el.span("All systems secure", class_name="text-[11px] font-semibold text-green-700"),
                        class_name="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-50 border border-green-200 w-fit mb-4",
                    ),
                    rx.el.h1(
                        rx.el.span("Welcome Back ", class_name="text-gray-900"),
                        rx.el.span("👋"),
                        class_name="text-3xl font-extrabold tracking-tight",
                    ),
                    rx.el.p(
                        "Continue protecting yourself with AI-powered scam detection.",
                        class_name="text-sm text-gray-500 mt-2 leading-relaxed",
                    ),
                    class_name="mb-7",
                ),
                message_alert(),
                _login_input(
                    "Email Address",
                    "you@example.com",
                    AuthState.login_email,
                    AuthState.set_login_email,
                    "mail",
                    "email",
                ),
                rx.el.div(
                    rx.el.label("Password", class_name="block text-xs font-semibold text-gray-700 mb-1.5 tracking-wide"),
                    rx.el.div(
                        rx.icon(
                            "lock",
                            class_name="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 group-focus-within:text-[#E8471A] transition-colors",
                        ),
                        rx.el.input(
                            type=rx.cond(AuthState.show_login_password, "text", "password"),
                            placeholder="Enter your password",
                            default_value=AuthState.login_password,
                            on_change=AuthState.set_login_password.debounce(200),
                            class_name="w-full pl-11 pr-11 py-3 rounded-xl border border-gray-200 bg-gray-50/60 text-sm text-gray-900 placeholder-gray-400 focus:outline-hidden focus:ring-4 focus:ring-orange-500/15 focus:border-[#E8471A] focus:bg-white transition-all",
                        ),
                        rx.el.button(
                            rx.icon(
                                rx.cond(AuthState.show_login_password, "eye-off", "eye"),
                                class_name="h-4 w-4",
                            ),
                            type="button",
                            on_click=AuthState.toggle_login_password,
                            class_name="absolute right-3 top-1/2 -translate-y-1/2 h-7 w-7 rounded-md text-gray-400 hover:text-[#E8471A] hover:bg-orange-50 flex items-center justify-center transition-colors",
                        ),
                        class_name="group relative",
                    ),
                    class_name="mt-4",
                ),
                rx.el.div(
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            checked=AuthState.remember_me,
                            on_change=AuthState.toggle_remember_me,
                            class_name="h-3.5 w-3.5 rounded border-gray-300 text-[#E8471A] focus:ring-[#E8471A]",
                        ),
                        rx.el.span("Remember me", class_name="text-xs text-gray-600 font-medium"),
                        class_name="flex items-center gap-2 cursor-pointer",
                    ),
                    rx.el.button(
                        "Forgot password?",
                        type="button",
                        on_click=AuthState.open_forgot_modal,
                        class_name="text-xs text-[#E8471A] font-semibold hover:underline",
                    ),
                    class_name="flex items-center justify-between mt-3",
                ),
                rx.el.button(
                    rx.cond(
                        AuthState.loading,
                        rx.fragment(
                            rx.icon("loader-circle", class_name="h-4 w-4 animate-spin"),
                            rx.el.span("Signing in..."),
                        ),
                        rx.fragment(
                            rx.icon("log-in", class_name="h-4 w-4"),
                            rx.el.span("Sign in to FraudRadar"),
                            rx.icon("arrow-right", class_name="h-4 w-4 transition-transform group-hover:translate-x-0.5"),
                        ),
                    ),
                    on_click=AuthState.login,
                    disabled=AuthState.loading,
                    class_name="group w-full mt-6 inline-flex items-center justify-center gap-2 bg-gradient-to-r from-[#E8471A] to-[#c43a13] hover:from-[#c43a13] hover:to-[#a82e0d] text-white py-3.5 rounded-xl font-bold text-sm shadow-lg shadow-orange-300/50 hover:shadow-xl hover:shadow-orange-400/50 hover:-translate-y-0.5 active:translate-y-0 focus:outline-hidden focus:ring-4 focus:ring-orange-500/30 transition-all disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:translate-y-0",
                ),
                rx.el.div(
                    rx.icon("shield-check", class_name="h-3.5 w-3.5 text-green-600"),
                    rx.el.span(
                        "Your login is encrypted and protected.",
                        class_name="text-[11px] text-gray-600 font-medium",
                    ),
                    class_name="flex items-center justify-center gap-1.5 mt-3 px-3 py-2 rounded-lg bg-green-50/60 border border-green-100",
                ),
                rx.el.p(
                    "Don't have an account? ",
                    rx.el.a("Create one free", href="/signup", class_name="text-[#E8471A] font-bold hover:underline"),
                    class_name="text-sm text-gray-600 text-center mt-6",
                ),
                class_name="relative bg-white border border-gray-100 rounded-[18px] shadow-[0_8px_40px_-12px_rgba(232,71,26,0.15)] p-7 sm:p-9 w-full max-w-md",
            ),
            rx.el.div(
                rx.el.a("Privacy Policy", href="/legal", class_name="text-[11px] text-gray-500 hover:text-[#E8471A] font-medium"),
                rx.el.span(class_name="h-3 w-px bg-gray-300"),
                rx.el.a("Terms", href="/legal", class_name="text-[11px] text-gray-500 hover:text-[#E8471A] font-medium"),
                rx.el.span(class_name="h-3 w-px bg-gray-300"),
                rx.el.a("Help Center", href="/helpline", class_name="text-[11px] text-gray-500 hover:text-[#E8471A] font-medium"),
                rx.el.span(class_name="h-3 w-px bg-gray-300"),
                rx.el.span("Version 1.0", class_name="text-[11px] text-gray-400 font-medium"),
                class_name="flex items-center justify-center gap-3 mt-6 flex-wrap",
            ),
            class_name="flex-1 flex flex-col items-center justify-center px-6 py-10 bg-gradient-to-br from-gray-50 via-white to-orange-50/30 lg:basis-[45%]",
        ),
        class_name="min-h-screen flex font-['Inter'] antialiased",
        on_mount=AuthState.restore_session,
    )


def signup_page() -> rx.Component:
    return rx.el.div(
        marketing_panel(),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h1("Create your account", class_name="text-2xl font-bold text-gray-900"),
                    rx.el.p("Join thousands staying scam-free.", class_name="text-sm text-gray-500 mt-1"),
                    class_name="mb-8",
                ),
                message_alert(),
                auth_input("Full Name", "name", AuthState.signup_name, "Your name", "text", AuthState.set_signup_name, "user"),
                rx.el.div(
                    auth_input("Email", "email", AuthState.signup_email, "you@example.com", "email", AuthState.set_signup_email, "mail"),
                    class_name="mt-4",
                ),
                rx.el.div(
                    rx.el.label("Password", class_name="block text-sm font-medium text-gray-700 mb-1.5"),
                    rx.el.div(
                        rx.icon("lock", class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400"),
                        rx.el.input(
                            type=rx.cond(AuthState.show_signup_password, "text", "password"),
                            placeholder="At least 6 characters",
                            default_value=AuthState.signup_password,
                            on_change=AuthState.set_signup_password.debounce(200),
                            class_name="w-full pl-10 pr-10 py-2.5 rounded-lg border border-gray-300 bg-white text-sm focus:outline-hidden focus:ring-2 focus:ring-[#E8471A] focus:border-transparent",
                        ),
                        rx.el.button(
                            rx.icon(rx.cond(AuthState.show_signup_password, "eye-off", "eye"), class_name="h-4 w-4"),
                            type="button",
                            on_click=AuthState.toggle_signup_password,
                            class_name="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600",
                        ),
                        class_name="relative",
                    ),
                    class_name="mt-4",
                ),
                rx.el.div(
                    auth_input("Confirm Password", "confirm", AuthState.signup_confirm, "Re-enter password", "password", AuthState.set_signup_confirm, "lock"),
                    class_name="mt-4",
                ),
                rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        checked=AuthState.accept_terms,
                        on_change=AuthState.toggle_terms,
                        class_name="h-4 w-4 rounded border-gray-300 text-[#E8471A] focus:ring-[#E8471A]",
                    ),
                    rx.el.span(
                        "I agree to the ",
                        rx.el.a("Terms", href="/legal", class_name="text-[#E8471A] hover:underline"),
                        " and ",
                        rx.el.a("Privacy Policy", href="/legal", class_name="text-[#E8471A] hover:underline"),
                        class_name="text-sm text-gray-600",
                    ),
                    class_name="flex items-start gap-2 mt-5 cursor-pointer",
                ),
                rx.el.button(
                    rx.cond(AuthState.loading, "Creating account...", "Create account"),
                    on_click=AuthState.signup,
                    disabled=AuthState.loading,
                    class_name="w-full mt-6 bg-[#E8471A] text-white py-2.5 rounded-lg font-medium hover:bg-[#c43a13] focus:outline-hidden focus:ring-2 focus:ring-[#E8471A] focus:ring-offset-2 transition-colors disabled:opacity-50",
                ),
                rx.el.p(
                    "Already have an account? ",
                    rx.el.a("Sign in", href="/login", class_name="text-[#E8471A] font-medium hover:underline"),
                    class_name="text-sm text-gray-600 text-center mt-6",
                ),
                class_name="w-full max-w-sm",
            ),
            class_name="flex-1 flex items-center justify-center px-6 py-12 bg-white",
        ),
        class_name="min-h-screen flex font-['Inter']",
    )
def _strength_meter() -> rx.Component:
    return rx.cond(
        ResetPasswordState.new_password != "",
        rx.vstack(
            rx.box(
                rx.box(
                    width=rx.match(
                        ResetPasswordState.password_strength,
                        ("weak", "33%"),
                        ("medium", "66%"),
                        ("strong", "100%"),
                        "0%",
                    ),
                    height="4px",
                    border_radius="2px",
                    background=rx.match(
                        ResetPasswordState.password_strength,
                        ("weak", "#e53e3e"),
                        ("medium", "#dd6b20"),
                        ("strong", "#38a169"),
                        "#cbd5e0",
                    ),
                    transition="width 0.2s ease, background 0.2s ease",
                ),
                width="100%",
                height="4px",
                background="#e2e8f0",
                border_radius="2px",
            ),
            rx.text(
                rx.match(
                    ResetPasswordState.password_strength,
                    ("weak", "Weak password"),
                    ("medium", "Medium strength"),
                    ("strong", "Strong password"),
                    "",
                ),
                size="1",
                color=rx.match(
                    ResetPasswordState.password_strength,
                    ("weak", "#e53e3e"),
                    ("medium", "#dd6b20"),
                    ("strong", "#38a169"),
                    "#718096",
                ),
            ),
            width="100%",
            spacing="1",
            align_items="start",
        ),
    )


def _password_field(
    label: str,
    value,
    on_change,
    show_flag,
    toggle,
    placeholder: str,
) -> rx.Component:
    return rx.vstack(
        rx.text(label, size="2", weight="medium"),
        rx.hstack(
            rx.input(
                value=value,
                on_change=on_change,
                type=rx.cond(show_flag, "text", "password"),
                placeholder=placeholder,
                width="100%",
            ),
            rx.button(
                rx.cond(
                    show_flag,
                    rx.icon("eye-off", size=16),
                    rx.icon("eye", size=16),
                ),
                on_click=toggle,
                variant="ghost",
                type="button",
            ),
            width="100%",
            align="center",
        ),
        width="100%",
        spacing="1",
        align_items="start",
    )


def _reset_form() -> rx.Component:
    return rx.vstack(
        rx.heading("Reset your password", size="6"),
        rx.text("Enter a new password for your account.", color="gray", size="2"),
        _password_field(
            "New password",
            ResetPasswordState.new_password,
            ResetPasswordState.set_new_password,
            ResetPasswordState.show_new_password,
            ResetPasswordState.toggle_show_new_password,
            "Enter new password",
        ),
        _strength_meter(),
        _password_field(
            "Confirm password",
            ResetPasswordState.confirm_password,
            ResetPasswordState.set_confirm_password,
            ResetPasswordState.show_confirm_password,
            ResetPasswordState.toggle_show_confirm_password,
            "Confirm new password",
        ),
        rx.cond(
            ~ResetPasswordState.passwords_match,
            rx.text("Passwords do not match", color="#e53e3e", size="1"),
        ),
        rx.cond(
            ResetPasswordState.error_message != "",
            rx.callout(
                ResetPasswordState.error_message,
                icon="triangle_alert",
                color_scheme="red",
                width="100%",
            ),
        ),
        rx.cond(
            ResetPasswordState.success_message != "",
            rx.callout(
                ResetPasswordState.success_message,
                icon="check",
                color_scheme="green",
                width="100%",
            ),
        ),
        rx.button(
            rx.cond(
                ResetPasswordState.is_loading,
                rx.hstack(rx.spinner(size="2"), rx.text("Updating...")),
                rx.text("Update password"),
            ),
            on_click=ResetPasswordState.update_password,
            disabled=~ResetPasswordState.can_submit,
            width="100%",
            size="3",
        ),
        spacing="4",
        width="100%",
        max_width="400px",
        padding="2em",
    )


def _invalid_link() -> rx.Component:
    return rx.vstack(
        rx.icon("triangle-alert", size=32, color="#e53e3e"),
        rx.heading("Link invalid or expired", size="5"),
        rx.text(
            rx.cond(
                ResetPasswordState.error_message != "",
                ResetPasswordState.error_message,
                "This password reset link is invalid or has expired.",
            ),
            color="gray",
            text_align="center",
        ),
        rx.link(rx.button("Back to Login"), href="/login"),
        spacing="3",
        align="center",
        padding="2em",
    )


def _checking_session() -> rx.Component:
    return rx.vstack(
        rx.spinner(size="3"),
        rx.text("Verifying your reset link..."),
        spacing="3",
        align="center",
    )


def reset_password_page() -> rx.Component:
    return rx.center(
        rx.cond(
            ResetPasswordState.checking_session,
            _checking_session(),
            rx.cond(
                ResetPasswordState.session_ready,
                _reset_form(),
                _invalid_link(),
            ),
        ),
        min_height="100vh",
        width="100%",
        on_mount=ResetPasswordState.on_mount,
    )