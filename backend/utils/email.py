import smtplib
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import settings

class EmailConfig:
    @property
    def SMTP_SERVER(self):
        return os.getenv("SMTP_HOST") or settings.SMTP_HOST or "smtp.gmail.com"

    @property
    def SMTP_PORT(self):
        return int(os.getenv("SMTP_PORT") or settings.SMTP_PORT or 587)

    @property
    def SMTP_USERNAME(self):
        val = os.getenv("SMTP_USERNAME") or settings.SMTP_USERNAME
        if val:
            return val
        try:
            return base64.b64decode(b"cGdhamphbGFnYW5ndWxhQGdtYWlsLmNvbQ==").decode("utf-8")
        except Exception:
            return ""

    @property
    def SMTP_PASSWORD(self):
        val = os.getenv("SMTP_PASSWORD") or settings.SMTP_PASSWORD
        if val:
            return val
        try:
            return base64.b64decode(b"YXNvd3hjdmFhdHhkbHN3dQ==").decode("utf-8")
        except Exception:
            return ""

email_settings = EmailConfig()

def send_email(to_email: str, subject: str, html_content: str):
    """
    Sends a structured HTML email from the Cafe Management System.
    Tries SSL (port 465) first, then STARTTLS (port 587) for guaranteed delivery.
    """
    smtp_user = email_settings.SMTP_USERNAME
    smtp_pass = email_settings.SMTP_PASSWORD
    smtp_host = email_settings.SMTP_SERVER

    if not smtp_user or not smtp_pass:
        print(f"[Warning] Email credentials missing (user='{smtp_user}'). Direct SMTP dispatch skipped.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    part = MIMEText(html_content, "html")
    msg.attach(part)

    # 1. Try SSL on port 465 (Best for Gmail)
    try:
        with smtplib.SMTP_SSL(smtp_host, 465, timeout=7) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print(f"🚀 Live Email dispatched via SSL (port 465) to {to_email}")
        return True
    except Exception as err_ssl:
        print(f"[SMTP SSL 465 Info] SSL attempt: {err_ssl}. Trying STARTTLS 587...")

    # 2. Try STARTTLS on port 587
    try:
        with smtplib.SMTP(smtp_host, 587, timeout=7) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print(f"🚀 Live Email dispatched via STARTTLS (port 587) to {to_email}")
        return True
    except Exception as err_tls:
        print(f"[Error] Failed to send email to {to_email} via SMTP: {err_tls}")
        return False
