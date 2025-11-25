from celery import shared_task

from app.core.database import SessionLocal
from app.schemas.notification import NotificationCreate, BulkNotificationRequest
from app.services.notification_service import NotificationService


@shared_task(name="send_notification_task")
def send_notification_task(payload: dict):
    """
    Async single notification sender.
    Expects payload compatible with NotificationCreate.
    """
    db = SessionLocal()
    try:
        notif_payload = NotificationCreate(**payload)
        NotificationService.send_single(db, notif_payload)
    finally:
        db.close()


@shared_task(name="send_bulk_notification_task")
def send_bulk_notification_task(payload: dict):
    """
    Async bulk notification sender.
    Expects payload compatible with BulkNotificationRequest.
    """
    db = SessionLocal()
    try:
        bulk_payload = BulkNotificationRequest(**payload)
        NotificationService.send_bulk(db, bulk_payload)
    finally:
        db.close()
