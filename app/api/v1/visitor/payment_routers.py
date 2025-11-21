from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.schemas.payment_schemas import PaymentCreate, PaymentResponse, RefundRequest, RefundResponse, SecurityDepositReleaseRequest, SecurityDepositReleaseResponse, ConfirmationResponse
from app.services import payment_service
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.payment import Confirmation
from app.utils.invoice import INVOICE_DIR, generate_invoice, send_email_simulation, send_sms_simulation

router = APIRouter()

@router.post("/initiate")
def initiate_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return payment_service.initiate_payment(db, data, current_user.id)

@router.post("/{payment_id}/confirm", response_model=PaymentResponse)
def confirm_payment(payment_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    payment = payment_service.confirm_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Lookup the confirmation created by the service (if any)
    confirmation = (
        db.query(Confirmation)
        .filter(Confirmation.booking_id == payment.booking_id)
        .order_by(Confirmation.id.desc())
        .first()
    )

    if confirmation:
        # Build invoice PDF and schedule simulated notifications
        invoice_path = os.path.join(INVOICE_DIR, f"{confirmation.confirmation_number}.pdf")

        # Get user details if available
        user = None
        if payment.user_id:
            try:
                user = db.get(User, payment.user_id)
            except Exception:
                user = None

        user_name = user.name if user and getattr(user, "name", None) else "Guest"
        user_email = user.email if user and getattr(user, "email", None) else None
        user_phone = user.phone if user and getattr(user, "phone", None) else None

        # Generate invoice file synchronously (small file)
        generate_invoice(invoice_path, confirmation.confirmation_number, payment.amount, user_name)

        # Schedule background notifications
        if user_email:
            background_tasks.add_task(send_email_simulation, user_email, confirmation.confirmation_number, payment.amount)
        if user_phone:
            background_tasks.add_task(send_sms_simulation, user_phone, confirmation.confirmation_number, payment.amount)

    return payment

@router.get("", response_model=list[PaymentResponse])
def get_all_payments(db: Session = Depends(get_db)):
    return payment_service.get_all_payments(db)

@router.post("/refund", response_model=RefundResponse)
def refund_payment(data: RefundRequest, db: Session = Depends(get_db)):
    return payment_service.refund_payment(db, data)

@router.post("/security-deposit/release", response_model=SecurityDepositReleaseResponse)
def release_security_deposit(data: SecurityDepositReleaseRequest, db: Session = Depends(get_db)):
    result = payment_service.release_security_deposit(db, data)
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    return result

@router.get("/confirmations/{confirmation_number}", response_model=ConfirmationResponse)
def get_confirmation(confirmation_number: str, db: Session = Depends(get_db)):
    confirmation = payment_service.get_confirmation(db, confirmation_number)
    if not confirmation:
        raise HTTPException(status_code=404, detail="Confirmation not found")
    return confirmation


@router.get("/invoice/{confirmation_number}")
def download_invoice(confirmation_number: str):
    invoice_path = os.path.join(INVOICE_DIR, f"{confirmation_number}.pdf")
    if not os.path.isfile(invoice_path):
        raise HTTPException(status_code=404, detail="Invoice not found")
    return FileResponse(invoice_path, media_type="application/pdf", filename=f"{confirmation_number}.pdf")
