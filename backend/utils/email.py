import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import settings

class EmailConfig:
    SMTP_SERVER = settings.SMTP_HOST
    SMTP_PORT = settings.SMTP_PORT
    SMTP_USERNAME = settings.SMTP_USERNAME
    SMTP_PASSWORD = settings.SMTP_PASSWORD

email_settings = EmailConfig()

def send_email(to_email: str, subject: str, html_content: str):
    """
    Sends a structured HTML email from the Cafe Management System.
    """
    if not email_settings.SMTP_USERNAME or not email_settings.SMTP_PASSWORD:
        print("[Warning] Email credentials missing. Skipping email dispatch.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email_settings.SMTP_USERNAME
    msg["To"] = to_email

    # Attach HTML Content
    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        with smtplib.SMTP(email_settings.SMTP_SERVER, email_settings.SMTP_PORT) as server:
            server.starttls()  # Upgrade connection to secure encrypted SSL/TLS
            server.login(email_settings.SMTP_USERNAME, email_settings.SMTP_PASSWORD)
            server.sendmail(email_settings.SMTP_USERNAME, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[Error] Failed to send email to {to_email}: {str(e)}")
        return False