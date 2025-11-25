from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.students import Student
from app.models.supervisors import Supervisor
from app.models.user import User
from app.models.admin_hostel_mapping import AdminHostelMapping

from app.schemas.notification import NotificationCreate, NotificationOut
from app.services.notification_service import NotificationService
from app.models.notification import Notification, NotificationChannel

router = APIRouter()

# ------------------------------------------------------
# Helper: get student hostel id
# ------------------------------------------------------
def get_student_hostel(db: Session, user_id: int) -> int:
    # Query by User relationship or adjust column name based on Student model
    student = db.query(Student).filter(Student.user_id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student.hostel_id


# ------------------------------------------------------
# Send to supervisors of student's hostel
# ------------------------------------------------------
@router.post(
    "/notify-supervisors",
    response_model=List[NotificationOut],
    status_code=status.HTTP_201_CREATED,
)
def notify_supervisors(
    message: str,
    channel: NotificationChannel = NotificationChannel.email,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Student sends message to ALL supervisors of his hostel
    """
    hostel_id = get_student_hostel(db, current_user.id)

    supervisors = (
        db.query(User)
        .join(Supervisor, Supervisor.user_id == User.id)
        .filter(Supervisor.hostel_id == hostel_id)
        .all()
    )

    if not supervisors:
        raise HTTPException(status_code=404, detail="No supervisors found")

    results = []

    for supervisor in supervisors:
        notification = NotificationCreate(
            hostel_id=hostel_id,
            recipient_id=supervisor.email,
            recipient_type="supervisor",
            channel=channel,
            subject="Message from Student",
            body=message,
        )

        result = NotificationService.send_single(db, notification)
        results.append(result)

    return results


# ------------------------------------------------------
# Send to admins of student's hostel
# ------------------------------------------------------
@router.post(
    "/notify-admins",
    response_model=List[NotificationOut],
    status_code=status.HTTP_201_CREATED,
)
def notify_admins(
    message: str,
    channel: NotificationChannel = NotificationChannel.email,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Student sends message to ALL admins of his hostel
    """
    hostel_id = get_student_hostel(db, current_user.id)

    admins = (
        db.query(User)
        .join(
            AdminHostelMapping,
            AdminHostelMapping.admin_id == User.id
        )
        .filter(AdminHostelMapping.hostel_id == hostel_id)
        .all()
    )

    if not admins:
        raise HTTPException(status_code=404, detail="No admins found")

    results = []

    for admin in admins:
        notification = NotificationCreate(
            hostel_id=hostel_id,
            recipient_id=admin.email,
            recipient_type="admin",
            channel=channel,
            subject="Message from Student",
            body=message,
        )

        result = NotificationService.send_single(db, notification)
        results.append(result)

    return results


# ------------------------------------------------------
# Student receives system / admin messaging
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
    Student gets all messages sent to him
    """
    notifications = (
        db.query(Notification)
        .filter(Notification.recipient_id == current_user.email)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return notifications
