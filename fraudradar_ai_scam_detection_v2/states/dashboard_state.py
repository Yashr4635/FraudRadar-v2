import datetime
import reflex as rx
from typing import TypedDict
from fraudradar_ai_scam_detection_v2.states.scan_state import ScanState
import logging


class Notification(TypedDict):
    id: str
    icon: str
    title: str
    message: str
    time: str
    severity: str
    unread: bool


class WeeklyPoint(TypedDict):
    day: str
    scans: int
    threats: int


class ThreatSlice(TypedDict):
    name: str
    value: int
    color: str


class DashboardState(rx.State):
    search_query: str = ""
    current_tip: int = 0
    unread_count: int = 3

    # Static educational tips delivered as a notification feed.
    # These are NOT user-specific telemetry — they are India-focused
    # cyber-safety alerts shown to every authenticated user.
    notifications: list[Notification] = [
        {
            "id": "edu1",
            "icon": "shield-alert",
            "title": "Stay alert: UPI collect-request scams",
            "message": "Fraudsters disguise payment requests as refunds. Never approve UPI collect requests from unknown VPAs.",
            "time": "Safety alert",
            "severity": "high",
            "unread": True,
        },
        {
            "id": "edu2",
            "icon": "trending-up",
            "title": "Trending: Fake courier delivery scams",
            "message": "Callers claim a parcel contains illegal items and demand 'verification' fees. Hang up and call the official courier.",
            "time": "Trending in India",
            "severity": "medium",
            "unread": True,
        },
        {
            "id": "edu3",
            "icon": "key",
            "title": "Reminder: Never share OTP",
            "message": "RBI, banks, and government agencies will never ask for your OTP, PIN, or CVV over phone or SMS.",
            "time": "Safety tip",
            "severity": "info",
            "unread": True,
        },
        {
            "id": "edu4",
            "icon": "phone-call",
            "title": "Helpline 1930 is free 24×7",
            "message": "Report any suspected cyber fraud immediately. Faster reports give a better chance of fund recovery.",
            "time": "Resource",
            "severity": "info",
            "unread": False,
        },
    ]

    threat_distribution: list[ThreatSlice] = [
        {"name": "SMS", "value": 35, "color": "#E8471A"},
        {"name": "Calls", "value": 22, "color": "#F97316"},
        {"name": "URLs", "value": 18, "color": "#FB923C"},
        {"name": "Emails", "value": 15, "color": "#FDBA74"},
        {"name": "Social", "value": 10, "color": "#FED7AA"},
    ]

    risk_categories: list[dict[str, str | int]] = [
        {"name": "UPI Fraud", "value": 78, "color": "bg-red-500"},
        {"name": "OTP Scams", "value": 64, "color": "bg-orange-500"},
        {"name": "Phishing URLs", "value": 52, "color": "bg-yellow-500"},
        {"name": "Job Scams", "value": 38, "color": "bg-blue-500"},
        {"name": "Loan Apps", "value": 25, "color": "bg-emerald-500"},
    ]

    achievements: list[dict[str, str]] = [
        {
            "icon": "shield-check",
            "title": "Guardian",
            "desc": "100+ scans completed",
            "color": "bg-orange-500",
        },
        {
            "icon": "zap",
            "title": "Quick Reflex",
            "desc": "Sub-second analysis",
            "color": "bg-yellow-500",
        },
        {
            "icon": "target",
            "title": "Sharp Eye",
            "desc": "Detected 25 high-risk",
            "color": "bg-red-500",
        },
        {
            "icon": "flame",
            "title": "On Fire",
            "desc": "7-day streak active",
            "color": "bg-emerald-500",
        },
        {
            "icon": "award",
            "title": "Verified",
            "desc": "Account secured",
            "color": "bg-blue-500",
        },
        {
            "icon": "star",
            "title": "Top User",
            "desc": "Top 10% in India",
            "color": "bg-purple-500",
        },
    ]

    tips: list[dict[str, str]] = [
        {
            "icon": "lock",
            "title": "Never share your OTP",
            "desc": "Banks, RBI, or government officials will never ask for your OTP, PIN, or CVV. Hang up immediately.",
        },
        {
            "icon": "link",
            "title": "Inspect every link",
            "desc": "Hover before you click. Look for misspellings, unusual domains, and shortened URLs in suspicious messages.",
        },
        {
            "icon": "phone-call",
            "title": "Verify caller identity",
            "desc": "If a 'bank official' calls, hang up and call back using the official number printed on your card.",
        },
        {
            "icon": "indian-rupee",
            "title": "UPI requests are not refunds",
            "desc": "Genuine refunds happen automatically. A 'collect request' for a refund is always a scam.",
        },
        {
            "icon": "user-x",
            "title": "Stranger danger online",
            "desc": "Be wary of new connections offering jobs, investments, or romantic interest with money asks.",
        },
    ]

    @rx.event
    def set_search(self, v: str):
        self.search_query = v

    @rx.event
    def next_tip(self):
        self.current_tip = (self.current_tip + 1) % len(self.tips)

    @rx.event
    def prev_tip(self):
        self.current_tip = (self.current_tip - 1) % len(self.tips)

    @rx.event
    def set_tip(self, i: int):
        self.current_tip = i

    @rx.event
    def mark_all_read(self):
        self.notifications = [
            {**n, "unread": False} for n in self.notifications
        ]
        self.unread_count = 0

    @rx.var
    async def weekly_data(self) -> list[WeeklyPoint]:
        """Derive last-7-day scan/threat activity from real scan history."""
        try:
            history = await self.get_var_value(ScanState.history)
        except Exception:
            logging.exception("Unexpected error")
            history = []
        days: list[datetime.date] = []
        today = datetime.datetime.now().date()
        for i in range(6, -1, -1):
            days.append(today - datetime.timedelta(days=i))
        buckets: dict[str, dict[str, int]] = {
            d.isoformat(): {"scans": 0, "threats": 0} for d in days
        }
        for h in history or []:
            ts = h.get("timestamp", "")
            try:
                dt = datetime.datetime.strptime(ts[:10], "%Y-%m-%d").date()
                key = dt.isoformat()
                if key in buckets:
                    buckets[key]["scans"] += 1
                    if h.get("verdict") == "HIGH":
                        buckets[key]["threats"] += 1
            except Exception:
                logging.exception("Unexpected error")
                continue
        out: list[WeeklyPoint] = []
        for d in days:
            b = buckets[d.isoformat()]
            out.append(
                {
                    "day": d.strftime("%a"),
                    "scans": b["scans"],
                    "threats": b["threats"],
                }
            )
        return out

    @rx.var
    def current_date(self) -> str:
        return datetime.datetime.now().strftime("%A, %B %d, %Y")

    @rx.var
    def current_time(self) -> str:
        return datetime.datetime.now().strftime("%I:%M %p")

    @rx.var
    def greeting(self) -> str:
        h = datetime.datetime.now().hour
        if h < 12:
            return "Good Morning"
        if h < 17:
            return "Good Afternoon"
        return "Good Evening"

    @rx.var
    def selected_tip(self) -> dict[str, str]:
        if 0 <= self.current_tip < len(self.tips):
            return self.tips[self.current_tip]
        return {"icon": "lightbulb", "title": "", "desc": ""}