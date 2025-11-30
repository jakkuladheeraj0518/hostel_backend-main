# import requests

# from app.config import settings  # you must expose `settings` in config.py


# def send_email_sendgrid(to_email: str, subject: str, content: str) -> dict:
#     """
#     Send email via SendGrid API.

#     Env needed:
#       - SENDGRID_API_KEY
#       - SENDGRID_FROM_EMAIL
#     """
#     url = "https://api.sendgrid.com/v3/mail/send"
#     headers = {
#         "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "personalizations": [{"to": [{"email": to_email}]}],
#         "from": {"email": settings.SENDGRID_FROM_EMAIL},
#         "subject": subject,
#         "content": [{"type": "text/plain", "value": content}],
#     }
#     resp = requests.post(url, headers=headers, json=data)
#     return {
#         "status_code": resp.status_code,
#         "body": resp.text,
#         "headers": dict(resp.headers),
#     }
