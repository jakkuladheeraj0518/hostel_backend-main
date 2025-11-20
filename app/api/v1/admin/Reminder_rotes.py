# app/api/v1/routers/reminders.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import SessionLocal,get_db
from app.models.payment_models import PaymentReminder, Invoice
from app.schemas.payment_schemas import PaymentReminderResponse
from app.services.reminder_services import (
    create_and_schedule_reminder,
    process_single_reminder
)
from app.models.payment_models import ReminderType, ReminderChannel

router = APIRouter(prefix="/reminders", tags=["Reminders"])


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# -----------------------------------------------------------
# 1️⃣ Get reminders for invoice
# -----------------------------------------------------------

@router.get("/invoice/{invoice_id}", response_model=list[PaymentReminderResponse])
def get_invoice_reminders(invoice_id: int, db: Session = Depends(get_db)):
    reminders = db.query(PaymentReminder).filter(
        PaymentReminder.invoice_id == invoice_id
    ).all()

    return reminders


# -----------------------------------------------------------
# 2️⃣ Send manual reminder
# -----------------------------------------------------------

@router.post("/send-manual")
def send_manual(
    invoice_id: int,
    reminder_type: ReminderType,
    channel: ReminderChannel,
    background: BackgroundTasks,
    db: Session = Depends(get_db)
):

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(404, "Invoice not found")

    create_and_schedule_reminder(invoice, reminder_type, channel, db)
    return {"success": True, "message": "Reminder sent successfully"}
