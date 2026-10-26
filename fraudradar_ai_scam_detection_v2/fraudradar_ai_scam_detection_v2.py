import reflex as rx
from fraudradar_ai_scam_detection_v2.states.auth_state import AuthState
from fraudradar_ai_scam_detection_v2.components.auth_pages import (
    login_page,
    signup_page,
    reset_password_page,
)
from fraudradar_ai_scam_detection_v2.components.auth_callback import auth_callback_page
from fraudradar_ai_scam_detection_v2.components.landing import landing_page
from fraudradar_ai_scam_detection_v2.components.pages import (
    dashboard_page,
    analyze_page,
    history_page,
    assistant_page,
    profile_page,
    settings_page,
    helpline_page,
    scam_guide_page,
    legal_page,
)


def index() -> rx.Component:
    return landing_page()


app = rx.App(
    stylesheets=["/landing_animation.css", "/dashboard_animation.css"],
    head_components=[
        rx.el.script("""
            (function() {
                if (typeof window !== "undefined" && window.location.hash) {
                    var h = window.location.hash;
                    if (h.indexOf("access_token=") !== -1 || h.indexOf("error=") !== -1 || h.indexOf("error_code=") !== -1) {
                        if (window.location.pathname !== "/auth/callback") {
                            window.location.replace("/auth/callback" + h);
                        }
                    }
                }
            })();
        """),
        rx.el.style("""
            a[href*="reflex.dev"],
            #__reflex_badge,
            .reflex-badge-container,
            div[class*="reflex-badge"] {
                display: none !important;
                opacity: 0 !important;
                visibility: hidden !important;
                pointer-events: none !important;
                width: 0 !important;
                height: 0 !important;
                position: absolute !important;
                clip: rect(0 0 0 0) !important;
                clip-path: inset(50%) !important;
                overflow: hidden !important;
            }
            /* Universal Pointer Cursor and Snappy Active States */
            button,
            a,
            [role="button"],
            input[type="submit"],
            input[type="button"],
            input[type="reset"],
            input[type="checkbox"],
            input[type="radio"],
            select,
            summary,
            .cursor-pointer,
            .btn-press,
            .nav-pill,
            .lift-card,
            [tabindex="0"] {
                cursor: pointer !important;
            }
            button:disabled,
            input:disabled,
            select:disabled,
            [role="button"][aria-disabled="true"],
            .disabled {
                cursor: not-allowed !important;
            }
            button:active:not(:disabled),
            a:active,
            [role="button"]:active:not(:disabled),
            .btn-press:active:not(:disabled) {
                transform: scale(0.97) translateY(1px) !important;
                transition: transform 0.05s ease-out !important;
            }
        """),
        rx.el.link(rel="icon", href="/favicon.ico", type="image/x-icon"),
        rx.el.link(rel="icon", href="/favicon.png", type="image/png"),
        rx.el.link(rel="apple-touch-icon", href="/favicon.png"),
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="preconnect",
            href="https://fonts.gstatic.com",
            cross_origin="",
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
    theme=rx.theme(appearance="light"),
)
app.add_page(
    index,
    route="/",
    on_load=AuthState.handle_auth_callback_if_present,
)
app.add_page(
    login_page,
    route="/login",
    title="FraudRadar | Login",
    on_load=AuthState.handle_auth_callback_if_present,
)
app.add_page(
    signup_page,
    route="/signup",
    title="FraudRadar | Sign Up",
    on_load=AuthState.redirect_if_authenticated,
)

app.add_page(
    reset_password_page,
    route="/reset-password",
    title="FraudRadar | Reset Password",
)
app.add_page(auth_callback_page, route="/auth/callback")
app.add_page(dashboard_page, route="/dashboard")
app.add_page(analyze_page, route="/analyze")
app.add_page(history_page, route="/history")
app.add_page(assistant_page, route="/assistant")
app.add_page(profile_page, route="/profile")
app.add_page(settings_page, route="/settings")
app.add_page(helpline_page, route="/helpline")
app.add_page(scam_guide_page, route="/scam-guide")
app.add_page(legal_page, route="/legal")