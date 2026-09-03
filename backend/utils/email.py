import smtplib
import os
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
        return os.getenv("SMTP_USERNAME") or settings.SMTP_USERNAME or ""

    @property
    def SMTP_PASSWORD(self):
        return os.getenv("SMTP_PASSWORD") or settings.SMTP_PASSWORD or ""

email_settings = EmailConfig()

def send_email(to_email: str, subject: str, html_content: str):
    """
    Sends a structured HTML email from the Cafe Management System.
    Includes timeout protection for cloud environments like Render where outbound SMTP may be restricted.
    """
    smtp_user = email_settings.SMTP_USERNAME
    smtp_pass = email_settings.SMTP_PASSWORD
    smtp_host = email_settings.SMTP_SERVER
    smtp_port = email_settings.SMTP_PORT

    if not smtp_user or not smtp_pass:
        print(f"[Warning] Email credentials missing (user='{smtp_user}'). Skipping direct SMTP email dispatch.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    # Attach HTML Content
    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=5) as server:
            server.starttls()  # Upgrade connection to secure encrypted SSL/TLS
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print(f"🚀 Email dispatched successfully to {to_email}")
        return True
    except Exception as e:
        print(f"[Error] Failed to send email to {to_email} via SMTP ({smtp_host}:{smtp_port}): {str(e)}")
        return False
