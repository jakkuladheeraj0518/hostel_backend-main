from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.notification_service import NotificationService

router = APIRouter()


@router.post("/sendgrid", status_code=status.HTTP_200_OK)
async def sendgrid_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Handle SendGrid event webhooks for delivery tracking.

    Configure SendGrid to post events here, then mark delivered.
    """
    try:
        events = await request.json()
    except ValueError:
        # empty/invalid body — don't crash the app for malformed webhook calls.
        return {"status": "ok", "skipped": True}

    # events is often a list — normalize to iterable
    if isinstance(events, dict):
        events = [events]
    for e in events:
        message_id = e.get("sg_message_id")
        event_type = e.get("event")
        if message_id and event_type == "delivered":
            NotificationService.mark_delivered(db, message_id)
    return {"status": "ok"}


@router.post("/twilio-sms", status_code=status.HTTP_200_OK)
async def twilio_sms_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Twilio SMS status callbacks.
    """
    form = await request.form()
    message_sid = form.get("MessageSid")
    message_status = form.get("MessageStatus")
    if message_sid and message_status == "delivered":
        NotificationService.mark_delivered(db, message_sid)
    return {"status": "ok"}
