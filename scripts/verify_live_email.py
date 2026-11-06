#!/usr/bin/env python3
"""
Diagnostic & Verification Tool for Real Email OTP Delivery
Usage:
    python3 scripts/verify_live_email.py [recipient_email]

This script tests your SMTP credentials locally, sends a test verification email,
and (optionally) syncs the verified credentials directly to your Reflex Cloud production deployment.
"""

import os
import sys
import getpass
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# Load local .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v


def main():
    print("=" * 65)
    print("  FRAUDRADAR REAL EMAIL OTP DELIVERY & PRODUCTION VERIFIER  ")
    print("=" * 65)

    recipient = sys.argv[1] if len(sys.argv) > 1 else "23e51a6735@hitam.org"
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "yashr4635@gmail.com").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "").strip().replace(" ", "")

    print(f"\nConfiguration:")
    print(f"  • SMTP Host:     {smtp_host}:{smtp_port}")
    print(f"  • Sender Email:  {smtp_user}")
    print(f"  • Test Target:   {recipient}")

    if not smtp_password:
        print("\n[!] No SMTP_PASSWORD found in .env or environment.")
        print("    If using Gmail, enter your 16-character Google App Password.")
        print("    (Generate one at https://myaccount.google.com/apppasswords)\n")
        smtp_password = getpass.getpass("Enter 16-character App Password (hidden): ").strip().replace(" ", "")
        if not smtp_password:
            print("[-] Error: No password provided. Aborting.")
            sys.exit(1)

    print(f"\n[1/3] Connecting to {smtp_host}:{smtp_port}...")
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=12.0)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        print("      [✓] STARTTLS handshake successful.")

        print("[2/3] Authenticating as", smtp_user, "...")
        server.login(smtp_user, smtp_password)
        print("      [✓] SMTP authentication successful!")

        print(f"[3/3] Sending live 8-digit verification OTP to {recipient}...")
        test_otp = "84920153"
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Your FraudRadar Verification Code: {test_otp[:4]} {test_otp[4:]}"
        msg["From"] = f"FraudRadar Scam Defense <{smtp_user}>"
        msg["To"] = recipient

        text_body = f"""Hello,

Your FraudRadar 8-digit verification code is:

    {test_otp[:4]} {test_otp[4:]}

This email confirms that real outbound SMTP email delivery is operational.
Never share this code with anyone.

—
FraudRadar Scam Defense AI
Helpline: 1930 | https://cybercrime.gov.in
"""
        html_body = f"""<!DOCTYPE html>
<html>
<body style="font-family: sans-serif; background: #f8fafc; padding: 24px; margin: 0;">
  <div style="max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; padding: 32px; text-align: center;">
    <h2 style="color: #0f172a; margin: 0 0 8px;">FraudRadar Verification Code</h2>
    <p style="color: #64748b; font-size: 14px; margin-bottom: 24px;">Your 8-digit verification code is:</p>
    <div style="background: #fff7ed; border: 2px dashed #fdba74; border-radius: 10px; padding: 18px; margin-bottom: 24px;">
      <span style="font-family: monospace; font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #9a3412;">{test_otp[:4]} {test_otp[4:]}</span>
    </div>
    <p style="color: #94a3b8; font-size: 12px;">This is a live test from FraudRadar AI Scam Defense System.</p>
  </div>
</body>
</html>"""
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        server.sendmail(smtp_user, [recipient], msg.as_string())
        server.quit()
        print(f"      [✓] SUCCESS: Real test email delivered to {recipient}!")
        print("\n" + "=" * 65)
        print("  DELIVERY STATUS: 100% OPERATIONAL (CHECK YOUR INBOX NOW)  ")
        print("=" * 65)

        # Ask to update Reflex Cloud secrets
        app_id = "1ceac2f4-bb83-48d9-8da8-2ac7cd415489"
        token = "8f9a04f0-ef5f-4156-b33b-b8215bba1c19"
        update_cloud = input("\nDo you want to update Reflex Cloud secrets now? (Y/n): ").strip().lower()
        if update_cloud in ("", "y", "yes"):
            print("\nUpdating Reflex Cloud production secrets...")
            import subprocess
            cmd = [
                ".venv/bin/reflex", "cloud", "secrets", "update", app_id,
                "--env", f"SMTP_PASSWORD={smtp_password}",
                "--env", f"SMTP_HOST={smtp_host}",
                "--env", f"SMTP_PORT={smtp_port}",
                "--env", f"SMTP_USER={smtp_user}",
                "--env", f"SMTP_FROM_EMAIL={smtp_user}",
                "--env", f"SMTP_USE_TLS=true",
                "--env", f"SMTP_USE_SSL=false",
                "--env", "EMAIL_DEV_MODE=false",
                "--token", token,
                "--reboot",
                "--no-interactive",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                print("      [✓] Reflex Cloud production secrets updated and container rebooted!")
                print("      [✓] The live site at https://fraudradar-gray-wood.reflex.run now delivers real emails!")
            else:
                print("      [-] Could not auto-update cloud secrets:", res.stderr or res.stdout)

    except smtplib.SMTPAuthenticationError as e:
        print("\n[-] SMTP Authentication Failed:")
        print(f"    {e}")
        print("\nTroubleshooting:")
        print("  1. Verify 2-Step Verification is ON in your Google Account.")
        print("  2. Ensure you generated a dedicated 16-character 'App Password' at:")
        print("     https://myaccount.google.com/apppasswords")
        print("  3. Do NOT use your regular Gmail account login password.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

