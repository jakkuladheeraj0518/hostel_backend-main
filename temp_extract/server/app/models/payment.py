from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .base import BaseEntity
from .enums import PaymentStatus, PaymentMethod, FeeType


class Payment(BaseEntity):
    """Payment model"""
    __tablename__ = "payments"
    
    # Payment details (as per drawio)
    student_id = Column(String, nullable=False)  # Changed from user_id as per drawio
    fee_amount = Column(Float, nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    payment_due_date = Column(String, nullable=True)  # Changed field name as per drawio (using string as per drawio)
    transaction_id = Column(String(255), unique=True, nullable=True)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True)
    
    # Legacy fields for backward compatibility (minimal set)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    fee_type = Column(SQLEnum(FeeType), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    hostel = relationship("Hostel", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.fee_amount}, status={self.payment_status})>"
    
    @property
    def total_amount(self):
        """Calculate total amount"""
        return self.fee_amount