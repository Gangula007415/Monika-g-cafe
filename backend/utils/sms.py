from backend.config import settings

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

class SMSConfig:
    ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
    AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
    PHONE_NUMBER = settings.TWILIO_PHONE_NUMBER

sms_settings = SMSConfig()

def send_sms(to_phone: str, text_message: str):
    """
    Dispatches outbound text notifications / OTPs via the configured SMS gateway.
    """
    print(f"[SMS Log] Outbound to {to_phone}: {text_message}")
    
    if not TWILIO_AVAILABLE:
        print("[Info] 'twilio' package not installed. Running in mock/log mode.")
        return True

    if not sms_settings.ACCOUNT_SID or not sms_settings.AUTH_TOKEN:
        print("[Warning] Twilio credentials absent. SMS not sent over the network.")
        return False

    try:
        client = Client(sms_settings.ACCOUNT_SID, sms_settings.AUTH_TOKEN)
        message = client.messages.create(
            body=text_message,
            from_=sms_settings.PHONE_NUMBER,
            to=to_phone
        )
        return True
    except Exception as e:
        print(f"[Error] Failed to dispatch SMS via API gateway: {str(e)}")
        return False