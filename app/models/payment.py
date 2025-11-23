from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


# ---------------------------------------------------------
# ⭐ Booking Payment Model (renamed to avoid conflict)
# ---------------------------------------------------------
class BookingPayment(Base):
    __tablename__ = "booking_payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=True)

    payment_reference = Column(String, unique=True, nullable=True)
    payment_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")

    status = Column(String, default="processing")
    payment_method = Column(String, nullable=True)
    payment_gateway = Column(String, nullable=True)

    gateway_transaction_id = Column(String, nullable=True)
    gateway_order_id = Column(String, nullable=True)

    description = Column(String, nullable=True)

    is_security_deposit = Column(Boolean, default=False)
    security_deposit_refunded = Column(Boolean, default=False)

    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationship
    refunds = relationship("BookingRefund", back_populates="payment")


# ---------------------------------------------------------
# ⭐ Booking Refund Model (renamed table)
# ---------------------------------------------------------
class BookingRefund(Base):
    __tablename__ = "booking_refunds"   # ← FIXED NAME

    id = Column(Integer, primary_key=True, index=True)

    payment_id = Column(Integer, ForeignKey("booking_payments.id"))
    refund_reference = Column(String, unique=True)

    amount = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="completed")

    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, default=datetime.utcnow)

    payment = relationship("BookingPayment", back_populates="refunds")

    # Backwards-compatibility accessors expected by response schemas
    @property
    def refund_id(self):
        """Alias used by older schemas for refund identifier."""
        return self.refund_reference

    @property
    def created_at(self):
        """Alias mapping created_at to initiated_at for compatibility."""
        return self.initiated_at


# ---------------------------------------------------------
# ⭐ Confirmation Model
# ---------------------------------------------------------
class Confirmation(Base):
    __tablename__ = "confirmations"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(Integer, nullable=False)
    confirmation_number = Column(String, unique=True)

    confirmation_type = Column(String)
    pdf_content = Column(String)
    email_sent = Column(Boolean, default=False)

    generated_at = Column(DateTime, default=datetime.utcnow)
