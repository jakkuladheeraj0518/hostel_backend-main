# import boto3
# from botocore.exceptions import BotoCoreError, ClientError

# from app.config import settings


# def send_sms_sns(to_number: str, content: str) -> dict:
#     """
#     AWS SNS SMS integration.

#     Env needed:
#       - AWS_ACCESS_KEY_ID
#       - AWS_SECRET_ACCESS_KEY
#       - AWS_REGION
#     """
#     client = boto3.client(
#         "sns",
#         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#         region_name=settings.AWS_REGION,
#     )
#     try:
#         resp = client.publish(PhoneNumber=to_number, Message=content)
#         return {"status_code": 200, "message_id": resp.get("MessageId")}
#     except (BotoCoreError, ClientError) as exc:
#         return {"status_code": 500, "error": str(exc)}
