import reflex as rx
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
    rx.el.link(rel="icon", href="/favicon.ico", type="image/x-icon"),

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
app.add_page(index, route="/")
app.add_page(
    login_page,
    route="/login",
    title="FraudRadar | Login",
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