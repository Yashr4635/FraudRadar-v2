import os
import logging
import reflex as rx
from typing import TypedDict

try:
    from groq import Groq
except Exception:
    logging.exception("Unexpected error")
    Groq = None


class ChatMsg(TypedDict):
    role: str
    content: str


ASSISTANT_PROMPT = """You are FraudRadar Assistant, a helpful AI guide for fraud and scam safety in India. Provide clear, concise, India-context-aware guidance about UPI fraud, OTP scams, KYC scams, phishing, fake job offers, investment scams, loan apps, and cyber safety. Always recommend official channels: cybercrime.gov.in, helpline 1930, and bank official apps. Reply in English only. Keep responses under 200 words."""


class AssistantState(rx.State):
    messages: list[ChatMsg] = []
    current_input: str = ""
    is_thinking: bool = False
    suggested_prompts: list[str] = [
        "I received a suspicious UPI request—what should I do?",
        "Someone is asking for my OTP claiming to be from my bank.",
        "How do I report a scam to cybercrime.gov.in?",
        "I clicked a suspicious link. What now?",
        "Is this loan app safe? It asks for contacts access.",
    ]

    @rx.event
    def set_input(self, v: str):
        self.current_input = v

    @rx.event
    def use_prompt(self, prompt: str):
        self.current_input = prompt

    @rx.event
    def clear_chat(self):
        self.messages = []

    @rx.event
    def send_message(self):
        msg = (self.current_input or "").strip()
        if not msg:
            return
        self.messages.append({"role": "user", "content": msg})
        self.current_input = ""
        self.is_thinking = True
        history = list(self.messages)

        reply = ""
        try:
            reply = self._get_reply(history)
        except Exception as e:
            logging.exception(f"Assistant top-level: {e}")
            reply = ""

        if not reply or not reply.strip():
            reply = (
                "I'm having trouble reaching the analysis service. "
                "For any suspected scam: 1) Do not share OTP/PIN/CVV, "
                "2) Call helpline 1930, 3) Report at cybercrime.gov.in, "
                "4) Block the sender and verify through your bank's official app."
            )

        self.messages.append({"role": "assistant", "content": reply})
        self.is_thinking = False

    def _get_reply(self, history: list[ChatMsg]) -> str:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or Groq is None:
            return (
                "I'm in offline mode right now. For any suspected scam: 1) Do not share OTP/PIN, "
                "2) Call helpline 1930, 3) Report at cybercrime.gov.in, 4) Block the sender. "
                "Verify all messages through official bank apps only."
            )
        try:
            client = Groq(api_key=api_key)
            msgs = [{"role": "system", "content": ASSISTANT_PROMPT}]
            for m in history[-10:]:
                msgs.append({"role": m["role"], "content": m["content"]})
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=msgs,
                temperature=0.4,
                max_tokens=400,
            )
            content = resp.choices[0].message.content or ""
            return content.strip()
        except Exception as e:
            logging.exception(f"Assistant error: {e}")
            return ""