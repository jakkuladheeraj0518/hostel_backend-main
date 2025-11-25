from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.notification import (
    NotificationCreate,
    NotificationOut,
    TemplateCreate,
    TemplateOut,
    TemplateUpdate,
    BulkNotificationRequest,
)
from app.services.notification_service import NotificationService
from app.models.notification import NotificationTemplate, Notification

router = APIRouter()


@router.post(
    "/notifications/send",
    response_model=NotificationOut,
    status_code=status.HTTP_201_CREATED,
)
def send_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
):
    """
    Send single notification (email/SMS/push) from admin panel.
    """
    return NotificationService.send_single(db, payload)


@router.post(
    "/notifications/bulk-send",
    response_model=List[NotificationOut],
    status_code=status.HTTP_201_CREATED,
)
def bulk_send_notification(
    payload: BulkNotificationRequest,
    db: Session = Depends(get_db),
):
    """
    Bulk + hierarchical routing:
    - direct recipients
    - admins/supervisors/students of a hostel.
    """
    notifs = NotificationService.send_bulk(db, payload)
    return notifs


@router.get(
    "/notifications",
    response_model=List[NotificationOut],
)
def list_notifications(
    db: Session = Depends(get_db),
    hostel_id: int | None = None,
):
    q = db.query(Notification)
    if hostel_id:
        q = q.filter(Notification.hostel_id == hostel_id)
    return q.order_by(Notification.created_at.desc()).limit(200).all()


# ===== Templates management =====


@router.post(
    "/notification-templates",
    response_model=TemplateOut,
    status_code=status.HTTP_201_CREATED,
)
def create_template(
    payload: TemplateCreate,
    db: Session = Depends(get_db),
):
    existing = NotificationService.get_template_by_name(db, payload.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template with this name already exists",
        )
    return NotificationService.create_template(db, payload)


@router.get(
    "/notification-templates",
    response_model=List[TemplateOut],
)
def list_templates(
    db: Session = Depends(get_db),
):
    return NotificationService.list_templates(db)


@router.put(
    "/notification-templates/{template_id}",
    response_model=TemplateOut,
)
def update_template(
    template_id: int,
    payload: TemplateUpdate,
    db: Session = Depends(get_db),
):
    tmpl = NotificationService.update_template(db, template_id, payload)
    if not tmpl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return tmpl
