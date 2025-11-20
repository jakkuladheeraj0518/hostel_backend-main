from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.notification import NotificationCreate, NotificationOut
from app.services.notification_service import NotificationService
from app.core.database import get_db
from app.schemas.notification import TemplateCreate, TemplateOut
from app.models.notification import NotificationTemplate
from typing import List
from fastapi import Body

router = APIRouter(prefix="/admin/notifications", tags=["admin-notifications"])


@router.post("/notify", response_model=NotificationOut)
def notify_admin(payload: NotificationCreate, db: Session = Depends(get_db)):
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


@router.post("/templates", response_model=TemplateOut)
def create_template(payload: TemplateCreate, db: Session = Depends(get_db)):
	repo = NotificationService(db).repo
	tpl = repo.get_template_by_name(payload.name)
	if tpl:
		raise HTTPException(status_code=400, detail="template_exists")
	new = NotificationTemplate(
		name=payload.name,
		channel=payload.channel,
		subject_template=payload.subject_template,
		body_template=payload.body_template,
	)
	created = repo.create_template(new)
	return created


@router.get("/templates", response_model=List[TemplateOut])
def list_templates(db: Session = Depends(get_db)):
	repo = NotificationService(db).repo
	return repo.list_templates()


@router.get("/templates/{template_id}", response_model=TemplateOut)
def get_template(template_id: int, db: Session = Depends(get_db)):
	repo = NotificationService(db).repo
	tpl = repo.get_template(template_id)
	if not tpl:
		raise HTTPException(status_code=404, detail="not_found")
	return tpl


@router.put("/templates/{template_id}", response_model=TemplateOut)
def update_template(template_id: int, payload: TemplateCreate, db: Session = Depends(get_db)):
	svc = NotificationService(db)
	repo = svc.repo
	tpl = repo.get_template(template_id)
	if not tpl:
		raise HTTPException(status_code=404, detail="not_found")
	updated = repo.update_template(tpl, payload.dict())
	return updated


@router.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
	repo = NotificationService(db).repo
	tpl = repo.get_template(template_id)
	if not tpl:
		raise HTTPException(status_code=404, detail="not_found")
	repo.delete_template(tpl)
	return {"deleted": True}


@router.post("/route", response_model=List[dict])
def route_example(payload: dict = Body(...), db: Session = Depends(get_db)):
	"""Demonstrate routing/escalation for a recipient. Payload must include recipient_id and recipient_type."""
	recipient_id = payload.get("recipient_id")
	recipient_type = payload.get("recipient_type")
	if not recipient_id or not recipient_type:
		raise HTTPException(status_code=400, detail="recipient_id and recipient_type required")
	svc = NotificationService(db)
	routed = svc.route_recipients(recipient_id, recipient_type)
	return [{"recipient_id": r[0], "recipient_type": r[1]} for r in routed]
