# from twilio.rest import Client

# from app.config import settings


# def send_sms_twilio(to_number: str, content: str) -> dict:
#     """
#     Twilio SMS integration.

#     Env needed:
#       - TWILIO_ACCOUNT_SID
#       - TWILIO_AUTH_TOKEN
#       - TWILIO_FROM_NUMBER
#     """
#     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#     message = client.messages.create(
#         body=content,
#         from_=settings.TWILIO_FROM_NUMBER,
#         to=to_number,
#     )
#     return {
#         "sid": message.sid,
#         "status": message.status,
#         "error_code": message.error_code,
#         "error_message": message.error_message,
#     }
