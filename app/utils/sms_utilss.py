import os
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None

def send_sms_reminder(phone: str, message: str) -> bool:
    if not twilio_client:
        print("Twilio not configured")
        return False
    try:
        if not phone.startswith("+"):
            phone = f"+91{phone}"
        msg = twilio_client.messages.create(body=message, from_=TWILIO_PHONE_NUMBER, to=phone)
        return msg.sid is not None
    except Exception as e:
        print("SMS send failed:", e)
        return False
