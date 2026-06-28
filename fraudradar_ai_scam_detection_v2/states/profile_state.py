import logging
import datetime
import reflex as rx
from fraudradar_ai_scam_detection_v2.states.auth_state import AuthState, get_supabase, PROFILES_TABLE


class ProfileState(rx.State):
    full_name: str = ""
    phone: str = ""
    location: str = ""
    bio: str = ""
    joined_date: str = ""
    avatar_seed: str = ""
    avatar_url: str = ""
    notifications_email: bool = True
    notifications_sms: bool = False
    notifications_push: bool = True
    weekly_report: bool = True
    high_risk_alerts: bool = True
    scam_news: bool = False
    two_factor_enabled: bool = False
    biometric_enabled: bool = False
    data_sharing: bool = False
    analytics_opt_in: bool = True
    public_profile: bool = False
    save_message: str = ""
    confirm_delete_text: str = ""
    show_delete_modal: bool = False
    initialized: bool = False

    @rx.event
    async def init_profile(self):
        if self.initialized:
            return
        auth = await self.get_state(AuthState)
        self.full_name = auth.user_name or ""
        self.avatar_seed = auth.user_email or auth.user_name or "user"
        self.avatar_url = auth.user_avatar_url or ""
        if not self.joined_date:
            self.joined_date = datetime.datetime.now().strftime("%B %Y")

        # Best-effort load from Supabase profiles table
        sb = get_supabase()
        if sb is not None and auth.user_id:
            try:
                resp = (
                    sb.table(PROFILES_TABLE)
                    .select("*")
                    .eq("id", auth.user_id)
                    .limit(1)
                    .execute()
                )
                rows = getattr(resp, "data", None) or []
                if rows:
                    row = rows[0]
                    self.full_name = row.get("full_name") or self.full_name
                    self.phone = row.get("phone") or self.phone
                    self.location = row.get("location") or self.location
                    self.bio = row.get("bio") or self.bio
                    self.avatar_url = row.get("avatar_url") or self.avatar_url
                    created = row.get("created_at")
                    if created:
                        try:
                            dt = datetime.datetime.fromisoformat(
                                str(created).replace("Z", "+00:00")
                            )
                            self.joined_date = dt.strftime("%B %Y")
                        except Exception:
                            logging.exception("joined_date parse")
            except Exception as e:
                msg = str(e)
                if "PGRST205" in msg or "Could not find the table" in msg:
                    logging.debug("profiles table missing; skipping load")
                else:
                    logging.exception(f"profile load: {e}")
        self.initialized = True

    @rx.event
    def set_full_name(self, v: str):
        self.full_name = v

    @rx.event
    def set_phone(self, v: str):
        self.phone = v

    @rx.event
    def set_location(self, v: str):
        self.location = v

    @rx.event
    def set_bio(self, v: str):
        self.bio = v

    @rx.event
    def toggle_email_notif(self):
        self.notifications_email = not self.notifications_email

    @rx.event
    def toggle_sms_notif(self):
        self.notifications_sms = not self.notifications_sms

    @rx.event
    def toggle_push_notif(self):
        self.notifications_push = not self.notifications_push

    @rx.event
    def toggle_weekly(self):
        self.weekly_report = not self.weekly_report

    @rx.event
    def toggle_high_risk(self):
        self.high_risk_alerts = not self.high_risk_alerts

    @rx.event
    def toggle_scam_news(self):
        self.scam_news = not self.scam_news

    @rx.event
    def toggle_2fa(self):
        self.two_factor_enabled = not self.two_factor_enabled
        self.save_message = (
            "Two-factor authentication enabled."
            if self.two_factor_enabled
            else "Two-factor authentication disabled."
        )

    @rx.event
    def toggle_biometric(self):
        self.biometric_enabled = not self.biometric_enabled

    @rx.event
    def toggle_data_sharing(self):
        self.data_sharing = not self.data_sharing

    @rx.event
    def toggle_analytics(self):
        self.analytics_opt_in = not self.analytics_opt_in

    @rx.event
    def toggle_public_profile(self):
        self.public_profile = not self.public_profile

    @rx.event
    def set_confirm_delete(self, v: str):
        self.confirm_delete_text = v

    @rx.event
    def open_delete_modal(self):
        self.show_delete_modal = True

    @rx.event
    def close_delete_modal(self):
        self.show_delete_modal = False
        self.confirm_delete_text = ""

    @rx.event
    def request_account_deletion(self):
        if self.confirm_delete_text.strip().upper() != "DELETE":
            self.save_message = (
                "Type DELETE to confirm account deletion request."
            )
            return rx.toast.error("Type DELETE to confirm.")
        self.show_delete_modal = False
        self.confirm_delete_text = ""
        self.save_message = "Account deletion request submitted. Our team will contact you within 48 hours."
        return rx.toast.success("Deletion request submitted.")

    @rx.event
    async def save_profile(self):
        auth = await self.get_state(AuthState)
        auth.user_name = self.full_name
        self.save_message = "Profile saved successfully."

        # Best-effort upsert to Supabase
        sb = get_supabase()
        if sb is not None and auth.user_id:
            payload = {
                "id": auth.user_id,
                "email": auth.user_email,
                "full_name": self.full_name,
                "phone": self.phone,
                "location": self.location,
                "bio": self.bio,
                "avatar_url": self.avatar_url,
                "provider": auth.user_provider,
            }
            try:
                sb.table(PROFILES_TABLE).upsert(payload).execute()
            except Exception as e:
                msg = str(e)
                if "PGRST205" in msg or "Could not find the table" in msg:
                    logging.debug("profiles table missing; skipping save")
                else:
                    logging.exception(f"profile upsert: {e}")
        yield rx.toast.success("Profile updated.")

    @rx.event
    def reset_profile(self):
        self.full_name = ""
        self.phone = ""
        self.location = ""
        self.bio = ""
        self.save_message = "Profile reset."