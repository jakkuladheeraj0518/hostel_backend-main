# import boto3
# from botocore.exceptions import BotoCoreError, ClientError

# from app.config import settings


# def send_email_ses(to_email: str, subject: str, content: str) -> dict:
#     """
#     AWS SES-based email sending.

#     Env needed:
#       - AWS_ACCESS_KEY_ID
#       - AWS_SECRET_ACCESS_KEY
#       - AWS_REGION
#       - SES_FROM_EMAIL
#     """
#     client = boto3.client(
#         "ses",
#         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#         region_name=settings.AWS_REGION,
#     )

#     try:
#         resp = client.send_email(
#             Source=settings.SES_FROM_EMAIL,
#             Destination={"ToAddresses": [to_email]},
#             Message={
#                 "Subject": {"Data": subject},
#                 "Body": {"Text": {"Data": content}},
#             },
#         )
#         return {"status_code": 200, "message_id": resp["MessageId"]}
#     except (BotoCoreError, ClientError) as exc:
#         return {"status_code": 500, "error": str(exc)}
