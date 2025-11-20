from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Numeric, Integer, JSON, Boolean, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class CommissionStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"

class ReportType(str, enum.Enum):
    REVENUE = "revenue"
    COMMISSION = "commission"
    BOOKING = "booking"
    USER_ACTIVITY = "user_activity"
    SUBSCRIPTION = "subscription"
    SYSTEM_PERFORMANCE = "system_performance"

class ExportFormat(str, enum.Enum):
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"

class BookingReport(Base):
    __tablename__ = "booking_reports"

    id = Column(String, primary_key=True, default=lambda: f"book_{uuid.uuid4().hex[:8]}")
    hostel_id = Column(String, nullable=False, index=True)
    hostel_name = Column(String, nullable=False)
    user_id = Column(String, nullable=False, index=True)
    user_name = Column(String, nullable=False)

    room_type = Column(String, nullable=False)
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)

    amount = Column(Numeric(10, 2), nullable=False)
    commission_rate = Column(Numeric(5, 4), nullable=False)
    commission_amount = Column(Numeric(10, 2), nullable=False)

    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    commission = relationship("Commission", back_populates="booking", uselist=False)


class Commission(Base):
    __tablename__ = "commissions"

    id = Column(String, primary_key=True, default=lambda: f"comm_{uuid.uuid4().hex[:8]}")
    booking_id = Column(String, ForeignKey('booking_reports.id'), nullable=False, unique=True)

    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(CommissionStatus), default=CommissionStatus.PENDING)

    earned_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime, nullable=True)

    hostel_id = Column(String, nullable=False, index=True)
    platform_revenue = Column(Numeric(10, 2), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    booking = relationship("BookingReport", back_populates="commission")


class SubscriptionRevenue(Base):
    __tablename__ = "subscription_revenues"

    id = Column(String, primary_key=True, default=lambda: f"subrev_{uuid.uuid4().hex[:8]}")
    subscription_id = Column(String, nullable=False, index=True)
    organization_id = Column(String, nullable=False, index=True)
    organization_name = Column(String, nullable=False)

    amount = Column(Numeric(10, 2), nullable=False)
    plan_name = Column(String, nullable=False)

    billing_date = Column(DateTime, nullable=False, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: f"rep_{uuid.uuid4().hex[:8]}")
    name = Column(String, nullable=False)
    report_type = Column(SQLEnum(ReportType), nullable=False)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    parameters = Column(JSON)
    result_data = Column(JSON)

    file_path = Column(String, nullable=True)
    export_format = Column(SQLEnum(ExportFormat), nullable=True)

    generated_by = Column(String, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)

    is_automated = Column(Boolean, default=False)
    is_scheduled = Column(Boolean, default=False)


class FinancialSummary(Base):
    __tablename__ = "financial_summaries"

    id = Column(String, primary_key=True, default=lambda: f"finsum_{uuid.uuid4().hex[:8]}")

    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)

    total_income = Column(Numeric(10, 2), default=0)
    subscription_revenue = Column(Numeric(10, 2), default=0)
    commission_earned = Column(Numeric(10, 2), default=0)
    pending_payments = Column(Numeric(10, 2), default=0)

    total_bookings = Column(Integer, default=0)
    completed_bookings = Column(Integer, default=0)
    cancelled_bookings = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
