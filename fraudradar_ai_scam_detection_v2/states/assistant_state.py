import os
import logging
import reflex as rx
from typing import TypedDict

try:
    from groq import Groq
except Exception:
    logging.exception("Failed to import groq SDK")
    Groq = None

MODEL_NAME = "llama-3.3-70b-versatile"
MAX_HISTORY_MESSAGES = 12  # ~6 exchanges sent to the API, keeps token usage bounded
REQUEST_TIMEOUT_SECONDS = 20.0

ASSISTANT_PROMPT = """You are FraudRadar Assistant, a professional cybersecurity and fraud-detection guide for users in India.

When the user describes a specific suspicious message, call, link, QR code, or transaction, structure your reply as:
- Verdict: (Likely Safe / Suspicious / Likely Fraud)
- Risk Level: (Low / Medium / High)
- Reasoning: 1-2 sentences on what makes it suspicious or safe
- Recommended Actions: concrete next steps
- Official Resource: cybercrime.gov.in or helpline 1930, only if relevant

For general questions (how scams work, how to stay safe, how to report), skip the Verdict/Risk fields and just answer directly and clearly.

You have deep expertise in UPI fraud, banking fraud, OTP scams, QR code scams, WhatsApp and SMS scams, phishing, fake investment schemes, fake job offers, loan app scams, and KYC-update scams targeting Indian users.

Be concise. Never exceed 200 words. Never ask the user to share OTP, PIN, CVV, or passwords with you. Always reply in English."""

OFFLINE_FALLBACK = (
    "I'm in offline mode right now (no API key configured). "
    "For any suspected scam: 1) Never share OTP/PIN/CVV, 2) Call helpline 1930, "
    "3) Report at cybercrime.gov.in, 4) Verify only through your bank's official app."
)
TIMEOUT_FALLBACK = (
    "The analysis service is taking too long to respond. Please try again in a moment. "
    "If this is urgent: do not share OTP/PIN/CVV, and call 1930 or report at cybercrime.gov.in."
)
NETWORK_FALLBACK = (
    "I couldn't reach the analysis service due to a network issue. Please check your connection and try again. "
    "If urgent: call 1930 or report at cybercrime.gov.in."
)
AUTH_FALLBACK = (
    "The analysis service is misconfigured (authentication issue) — this needs an admin to check the API key. "
    "For any suspected scam meanwhile: never share OTP/PIN/CVV, and call 1930 or report at cybercrime.gov.in."
)
GENERIC_FALLBACK = (
    "I ran into an unexpected issue analyzing that. Please try again. "
    "For any suspected scam meanwhile: never share OTP/PIN/CVV, and call 1930 or report at cybercrime.gov.in."
)


class ChatMsg(TypedDict):
    role: str
    content: str


class AssistantState(rx.State):
    messages: list[ChatMsg] = []
    is_thinking: bool = False
    suggested_prompts: list[str] = [
        "I received a suspicious UPI request—what should I do?",
        "Someone is asking for my OTP claiming to be from my bank.",
        "How do I report a scam to cybercrime.gov.in?",
        "I clicked a suspicious link. What now?",
        "Is this loan app safe? It asks for contacts access.",
    ]

    @rx.event
    def clear_chat(self):
        self.messages = []

    @rx.event
    def send_message(self, form_data: dict):
        msg = (form_data.get("message") or "").strip()
        if not msg or self.is_thinking:
            return

        self.messages.append({"role": "user", "content": msg})
        self.is_thinking = True
        # Flush this state update to the client now (clears input, shows
        # the thinking indicator) before the blocking API call below.
        yield rx.set_value("chat-input", "")

        history = list(self.messages)
        try:
            reply = self._get_reply(history)
        except Exception as e:
            logging.exception(f"Assistant top-level error: {e}")
            reply = GENERIC_FALLBACK

        if not reply or not reply.strip():
            reply = GENERIC_FALLBACK

        self.messages.append({"role": "assistant", "content": reply})
        self.is_thinking = False

    def _get_reply(self, history: list[ChatMsg]) -> str:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or Groq is None:
            return OFFLINE_FALLBACK

        try:
            client = Groq(api_key=api_key, timeout=REQUEST_TIMEOUT_SECONDS)
            msgs = [{"role": "system", "content": ASSISTANT_PROMPT}]
            for m in history[-MAX_HISTORY_MESSAGES:]:
                msgs.append({"role": m["role"], "content": m["content"]})

            resp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=msgs,
                temperature=0.3,
                max_tokens=400,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            logging.exception(f"Assistant API error: {e}")
            err_name = type(e).__name__.lower()
            if "timeout" in err_name:
                return TIMEOUT_FALLBACK
            if "connection" in err_name or "network" in err_name:
                return NETWORK_FALLBACK
            if "auth" in err_name or "permission" in err_name:
                return AUTH_FALLBACK
            return GENERIC_FALLBACK
    def _scroll_chat_to_bottom(self):
        return rx.call_script(
            "setTimeout(() => { "
            "const el = document.getElementById('chat-messages'); "
            "if (el) el.scrollTo({top: el.scrollHeight, behavior: 'smooth'}); "
            "}, 50);"
        )

    @rx.event
    def send_message(self, form_data: dict):
        msg = (form_data.get("message") or "").strip()
        if not msg or self.is_thinking:
            return

        self.messages.append({"role": "user", "content": msg})
        self.is_thinking = True
        yield rx.set_value("chat-input", "")
        yield self._scroll_chat_to_bottom()

        history = list(self.messages)
        try:
            reply = self._get_reply(history)
        except Exception as e:
            logging.exception(f"Assistant top-level error: {e}")
            reply = GENERIC_FALLBACK

        if not reply or not reply.strip():
            reply = GENERIC_FALLBACK

        self.messages.append({"role": "assistant", "content": reply})
        self.is_thinking = False
        yield self._scroll_chat_to_bottom()