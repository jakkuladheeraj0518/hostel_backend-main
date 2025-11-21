import random, string
from datetime import datetime
from app.models.payment import BookingPayment as Payment, BookingRefund as Refund, Confirmation
from sqlalchemy.orm import Session

def _generate_ref(prefix: str) -> str:
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}{datetime.utcnow().strftime('%Y%m%d%H%M')}{suffix}"

# 1️⃣ Initiate Payment
def initiate_payment(db: Session, data, user_id: int):
    payment = Payment(
        booking_id=data.booking_id,
        user_id=user_id,
        payment_type=data.payment_type,
        amount=data.amount,
        currency=data.currency,
        payment_method=data.payment_method,
        payment_gateway=data.payment_gateway,
        description=data.description,
        status="processing",
        gateway_order_id=f"order_{''.join(random.choices(string.ascii_lowercase + string.digits, k=14))}"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "client_secret": None,
        "gateway_order_id": payment.gateway_order_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "gateway_url": None
    }

# 2️⃣ Confirm Payment
def confirm_payment(db: Session, payment_id: int):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        return None

    payment.status = "completed"
    payment.payment_reference = _generate_ref("PAY")
    payment.completed_at = datetime.utcnow()
    payment.gateway_transaction_id = payment.gateway_order_id
    db.commit()
    db.refresh(payment)

    confirmation_number = _generate_ref("CONF")
    pdf_html = f"<h1>Booking Payment Confirmation</h1><p>Payment Ref: {payment.payment_reference}</p>"
    confirmation = Confirmation(
        booking_id=payment.booking_id,
        confirmation_number=confirmation_number,
        confirmation_type="booking_payment",
        pdf_content=pdf_html,
        email_sent=True
    )
    db.add(confirmation)
    db.commit()

    # Simulate email log in console
    print("\n📧 EMAIL SENT")
    print(f"To: john.doe@example.com")
    print(f"Subject: Booking Confirmation - {confirmation_number}")
    print(f"Content length: {len(pdf_html)} chars")
    print("="*50)

    return payment

# 3️⃣ Refund
def refund_payment(db: Session, data):
    refund = Refund(
        payment_id=data.payment_id,
        refund_reference=_generate_ref("RFD"),
        amount=data.amount,
        reason=data.reason,
        status="completed"
    )
    db.add(refund)
    db.commit()
    db.refresh(refund)
    return refund

# 4️⃣ Security Deposit Release
def release_security_deposit(db: Session, data):
    payment = db.query(Payment).filter(Payment.id == data.payment_id).first()
    if not payment:
        return None

    refund_amount = max(0.0, payment.amount - data.deduction_amount)
    payment.security_deposit_refunded = True
    db.commit()

    return {
        "message": "Security deposit released successfully",
        "refund_amount": refund_amount,
        "deduction_amount": data.deduction_amount,
        "payment_reference": payment.payment_reference
    }

# 5️⃣ Get Confirmation
def get_confirmation(db: Session, confirmation_number: str):
    return db.query(Confirmation).filter(Confirmation.confirmation_number == confirmation_number).first()

# 6️⃣ List Payments
def get_all_payments(db: Session):
    return db.query(Payment).all()
