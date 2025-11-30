import os
from fastapi import HTTPException
from twilio.rest import Client
import boto3


class TwilioService:
    """
    Thin wrapper around Twilio sync client.
    Actual sending should be executed with asyncio.to_thread
    from router or service layer to avoid blocking the event loop.
    """

    def __init__(self):
        self.sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")

        if not (self.sid and self.token and self.from_number):
            self.client = None
        else:
            self.client = Client(self.sid, self.token)

    def send_sms(self, to_number: str, message: str):
        """
        Synchronous Twilio call.
        Must be run inside asyncio.to_thread().
        """
        if not self.client:
            raise HTTPException(
                status_code=500,
                detail="Twilio credentials missing or not configured"
            )

        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            # msg.status examples: queued, sent, delivered, failed, undelivered
            return msg.sid, msg.status
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Twilio error: {str(e)}"
            )


class AWSSNSService:
    """
    AWS SNS (sync) SMS service wrapper.
    Must be run inside asyncio.to_thread().
    """

    def __init__(self):
        region = os.getenv("AWS_REGION", "us-east-1")
        key = os.getenv("AWS_ACCESS_KEY_ID")
        secret = os.getenv("AWS_SECRET_ACCESS_KEY")

        if not (key and secret):
            self.client = None
        else:
            try:
                self.client = boto3.client(
                    "sns",
                    region_name=region,
                    aws_access_key_id=key,
                    aws_secret_access_key=secret
                )
            except Exception as e:
                self.client = None
                raise HTTPException(500, f"AWS SNS initialization failed: {str(e)}")

    def send_sms(self, to_number: str, message: str):
        """
        Synchronous AWS SNS call.
        Must be run inside asyncio.to_thread().
        """
        if not self.client:
            raise HTTPException(
                status_code=500,
                detail="AWS SNS credentials missing or not configured"
            )

        try:
            res = self.client.publish(
                PhoneNumber=to_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            message_id = res.get("MessageId")
            # SNS has no explicit status; assume 'sent'
            return message_id, "sent"

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"AWS SNS error: {str(e)}"
            )
