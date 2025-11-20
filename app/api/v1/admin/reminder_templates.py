# app/api/v1/routers/templates.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal,get_db
from app.models.payment_models import ReminderTemplate, ReminderType
from app.schemas.payment_schemas import TemplateCreate, TemplateResponse

router = APIRouter(prefix="/reminders/templates", tags=["Reminder Templates"])


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# -----------------------------------------------------------
# Create template
# -----------------------------------------------------------

@router.post("/", response_model=TemplateResponse)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    new_template = ReminderTemplate(**template.dict())
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template


# -----------------------------------------------------------
# Get templates
# -----------------------------------------------------------

@router.get("/", response_model=list[TemplateResponse])
def get_templates(reminder_type: ReminderType = None, db: Session = Depends(get_db)):

    query = db.query(ReminderTemplate)
    if reminder_type:
        query = query.filter(ReminderTemplate.reminder_type == reminder_type)

    return query.all()
