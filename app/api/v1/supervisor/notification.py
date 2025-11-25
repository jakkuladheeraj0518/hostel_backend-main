from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db

from app.models.user import User
from app.models.students import Student
from app.models.supervisors import Supervisor, SupervisorHostel

from app.models.admin_hostel_mapping import AdminHostelMapping
from app.models.notification import Notification, NotificationChannel

from app.schemas.notification import NotificationCreate, NotificationOut, BulkNotificationRequest
from app.services.notification_service import NotificationService

router = APIRouter()


# ------------------------------------------------------
# Get hostel_id of supervisor
# ------------------------------------------------------
def get_supervisor_hostel_id(db: Session, user_id: int) -> int:
    supervisor = (
        db.query(Supervisor)
        .filter(Supervisor.user_id == user_id)
        .first()
    )
    if not supervisor:
        raise HTTPException(status_code=404, detail="Supervisor not found")
    return supervisor.hostel_id


# ------------------------------------------------------
# Supervisor sends message to all students in hostel
# ------------------------------------------------------
@router.post(
    "/notify-students",
    response_model=List[NotificationOut],
    status_code=status.HTTP_201_CREATED,
)
def notify_students(
    message: str,
    channel: NotificationChannel = NotificationChannel.email,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Supervisor sends message to all students of the same hostel
    """
    hostel_id = get_supervisor_hostel_id(db, current_user.id)

    bulk = BulkNotificationRequest(
        hostel_id=hostel_id,
        channel=channel,
        body=message,
        send_to_students=True,
    )

    return NotificationService.send_bulk(db, bulk)


# ------------------------------------------------------
# Supervisor escalates to admins
# ------------------------------------------------------
@router.post(
    "/escalate-to-admins",
    response_model=List[NotificationOut],
    status_code=status.HTTP_201_CREATED,
)
def escalate_to_admins(
    message: str,
    channel: NotificationChannel = NotificationChannel.email,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Supervisor escalates an issue to admins
    """
    hostel_id = get_supervisor_hostel_id(db, current_user.id)

    bulk = BulkNotificationRequest(
        hostel_id=hostel_id,
        channel=channel,
        body=message,
        send_to_admins=True,
    )

    return NotificationService.send_bulk(db, bulk)


# ------------------------------------------------------
# Supervisor personal inbox
# ------------------------------------------------------
@router.get(
    "/my-notifications",
    response_model=List[NotificationOut],
)
def my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Supervisor receives messages here
    """
    notifications = (
        db.query(Notification)
        .filter(Notification.recipient_id == current_user.email)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return notifications
