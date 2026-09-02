from backend.config import settings
import os

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

class SMSConfig:
    @property
    def ACCOUNT_SID(self):
        return settings.TWILIO_ACCOUNT_SID or os.getenv("TWILIO_ACCOUNT_SID", "")
    
    @property
    def AUTH_TOKEN(self):
        return settings.TWILIO_AUTH_TOKEN or os.getenv("TWILIO_AUTH_TOKEN", "")
    
    @property
    def PHONE_NUMBER(self):
        return settings.TWILIO_FROM_NUMBER or os.getenv("TWILIO_FROM_NUMBER", "+12193552493")

sms_settings = SMSConfig()

def send_sms(to_phone: str, text_message: str):
    """
    Dispatches outbound text notifications / OTPs via the configured SMS gateway.
    """
    raw_phone = to_phone.strip().replace(" ", "").replace("-", "")
    if not raw_phone.startswith("+"):
        if len(raw_phone) == 10:
            formatted_phone = f"+91{raw_phone}"
        else:
            formatted_phone = f"+{raw_phone}"
    else:
        formatted_phone = raw_phone

    print(f"[SMS Log] Outbound to {formatted_phone}: {text_message}")
    
    if not TWILIO_AVAILABLE:
        print("[Info] 'twilio' package not installed. Running in mock/log mode.")
        return False

    if not sms_settings.ACCOUNT_SID or not sms_settings.AUTH_TOKEN:
        print("[Warning] Twilio credentials absent. SMS not sent over the network.")
        return False

    try:
        client = Client(sms_settings.ACCOUNT_SID, sms_settings.AUTH_TOKEN)
        message = client.messages.create(
            body=text_message,
            from_=sms_settings.PHONE_NUMBER,
            to=formatted_phone
        )
        print(f"🚀 Twilio SMS dispatched successfully! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"[Error] Failed to dispatch SMS via API gateway: {str(e)}")
        return False