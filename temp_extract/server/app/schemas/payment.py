from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from .common import BaseSchema
from app.models.enums import PaymentStatus, PaymentMethod, FeeType


class PaymentBase(BaseSchema):
    """Base payment schema"""
    fee_amount: float
    fee_type: FeeType
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class PaymentCreate(PaymentBase):
    """Payment creation schema"""
    user_id: str
    hostel_id: int  # Changed from str to int to match database
    
    @validator('fee_amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Fee amount must be greater than 0')
        return v


class PaymentUpdate(BaseSchema):
    """Payment update schema"""
    payment_status: Optional[PaymentStatus] = None
    payment_method: Optional[PaymentMethod] = None
    transaction_id: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    gateway_response: Optional[str] = None
    late_fee: Optional[float] = None
    discount: Optional[float] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None


class PaymentResponse(PaymentBase):
    """Payment response schema"""
    id: str
    user_id: str
    hostel_id: int  # Changed from str to int to match database
    payment_status: PaymentStatus
    payment_method: Optional[PaymentMethod] = None
    transaction_id: Optional[str] = None
    paid_date: Optional[datetime] = None
    late_fee: float
    discount: float
    total_amount: float
    gateway_transaction_id: Optional[str] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PaymentListResponse(BaseSchema):
    """Payment list response schema"""
    id: str
    user_id: str
    user_name: str
    hostel_id: int  # Changed from str to int to match database
    hostel_name: str
    fee_amount: float
    fee_type: FeeType
    payment_status: PaymentStatus
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    created_at: datetime


class PaymentSearchParams(BaseSchema):
    """Payment search parameters"""
    user_id: Optional[str] = None
    hostel_id: Optional[int]  # Changed from str to int to match database = None
    payment_status: Optional[PaymentStatus] = None
    fee_type: Optional[FeeType] = None
    payment_method: Optional[PaymentMethod] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class PaymentProcessRequest(BaseSchema):
    """Payment processing request"""
    payment_id: str
    payment_method: PaymentMethod
    gateway_data: Optional[dict] = None