from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime as dt
from decimal import Decimal

# Booking Schemas
class BookingCreate(BaseModel):
    hostel_id: str
    hostel_name: str
    user_id: str
    user_name: str
    room_type: str
    check_in_date: dt
    check_out_date: dt
    amount: Decimal

class BookingResponse(BaseModel):
    id: str
    hostel_id: str
    hostel_name: str
    user_id: str
    user_name: str
    room_type: str
    check_in_date: dt
    check_out_date: dt
    amount: Decimal
    commission_rate: Decimal
    commission_amount: Decimal
    status: str
    payment_status: str
    created_at: dt

    class Config:
        from_attributes = True

# Commission Schemas
class CommissionResponse(BaseModel):
    id: str
    booking_id: str
    amount: Decimal
    status: str
    earned_date: dt
    paid_date: Optional[dt]
    hostel_id: str
    platform_revenue: Decimal

    class Config:
        from_attributes = True

# Report Schemas
class ReportGenerateRequest(BaseModel):
    report_type: str
    start_date: dt
    end_date: dt
    export_format: Optional[str] = "pdf"
    parameters: Optional[Dict[str, Any]] = {}

class ReportResponse(BaseModel):
    id: str
    name: str
    report_type: str
    start_date: dt
    end_date: dt
    generated_at: dt
    export_format: Optional[str]
    file_path: Optional[str]

    class Config:
        from_attributes = True

# Financial Summary Schemas
class FinancialSummaryResponse(BaseModel):
    total_income: Decimal
    subscription_revenue: Decimal
    commission_earned: Decimal
    pending_payments: Decimal
    total_bookings: int
    completed_bookings: int
    cancelled_bookings: int
    period_start: dt
    period_end: dt

    class Config:
        from_attributes = True

# Statistics Schemas
class ReportStatistics(BaseModel):
    generated_this_month: int
    automated_reports: int
    scheduled_reports: int
