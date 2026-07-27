import reflex as rx
from fraudradar_ai_scam_detection_v2.states.auth_state import AuthState


def auth_callback_page() -> rx.Component:
    return rx.el.div(

        rx.el.div(
            rx.el.div(
                rx.icon("shield-check", class_name="h-7 w-7 text-white"),
                class_name="h-14 w-14 rounded-2xl bg-gradient-to-br from-[#E8471A] to-[#c43a13] flex items-center justify-center mx-auto shadow-lg shadow-orange-200/60",
            ),
            rx.el.h1(
                "Verifying your account...",
                class_name="text-xl font-bold text-gray-900 mt-5 text-center",
            ),
            rx.el.p(
                "Securely completing your sign in. You'll be redirected in a moment.",
                class_name="text-sm text-gray-500 text-center mt-2 max-w-sm",
            ),
            rx.cond(
                AuthState.auth_error != "",
                rx.el.div(
                    rx.icon("circle-alert", class_name="h-4 w-4 text-red-600"),
                    rx.el.p(AuthState.auth_error, class_name="text-sm text-red-700"),
                    class_name="flex items-center gap-2 p-3 rounded-lg bg-red-50 border border-red-200 mt-4",
                ),
                rx.fragment(),
            ),
            rx.el.div(
                rx.icon("loader-circle", class_name="h-5 w-5 animate-spin text-[#E8471A]"),
                class_name="flex items-center justify-center mt-6",
            ),
            rx.el.div(
                rx.el.a("Go to Sign In", href="/login", class_name="text-xs text-[#E8471A] font-semibold hover:underline"),
                rx.el.span(class_name="h-3 w-px bg-gray-300"),
                rx.el.a("Open Dashboard", href="/dashboard", class_name="text-xs text-[#E8471A] font-semibold hover:underline"),
                class_name="flex items-center justify-center gap-3 mt-5",
            ),
            class_name="bg-white border border-gray-100 rounded-2xl shadow-[0_8px_40px_-12px_rgba(232,71,26,0.15)] p-8 max-w-md w-full",
        ),

        class_name="min-h-screen flex items-center justify-center px-6 bg-gradient-to-br from-gray-50 via-white to-orange-50/30 font-['Inter']",
        on_mount=AuthState.handle_auth_callback,
    )