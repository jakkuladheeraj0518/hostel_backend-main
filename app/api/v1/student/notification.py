from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.notification import NotificationCreate, NotificationOut
from app.services.notification_service import NotificationService
from app.core.database import get_db

router = APIRouter(prefix="/student/notifications", tags=["student-notifications"])


@router.post("/notify", response_model=NotificationOut)
def notify_student(payload: NotificationCreate, db: Session = Depends(get_db)):
	svc = NotificationService(db)
	try:
		notif = svc.send_notification(
			recipient_id=payload.recipient_id,
			recipient_type=payload.recipient_type,
			channel=payload.channel,
			subject=payload.subject or "",
			body=payload.body or "",
		)
		return notif
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc))
