from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from fastapi import HTTPException
from datetime import datetime
from decimal import Decimal

from app.models.report_models import (
    BookingReport, Commission, SubscriptionRevenue, Report, FinancialSummary,
    BookingStatus, PaymentStatus, CommissionStatus, ReportType
)
from app.config import settings

# Booking CRUD
def create_booking(db: Session, booking_data: BookingReport):
    commission_rate = Decimal(str(settings.COMMISSION_RATE))
    commission_amount = booking_data.amount * commission_rate

    db_booking = BookingReport(
        hostel_id=booking_data.hostel_id,
        hostel_name=booking_data.hostel_name,
        user_id=booking_data.user_id,
        user_name=booking_data.user_name,
        room_type=booking_data.room_type,
        check_in_date=booking_data.check_in_date,
        check_out_date=booking_data.check_out_date,
        amount=booking_data.amount,
        commission_rate=commission_rate,
        commission_amount=commission_amount
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    # Create commission record
    commission = Commission(
        booking_id=db_booking.id,
        amount=commission_amount,
        earned_date=datetime.utcnow(),
        hostel_id=booking_data.hostel_id,
        platform_revenue=commission_amount
    )
    db.add(commission)
    db.commit()
    db.refresh(commission)

    return db_booking

def update_booking_status(db: Session, booking_id: str, status: BookingStatus, payment_status: PaymentStatus):
    booking = db.query(BookingReport).filter(BookingReport.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = status
    booking.payment_status = payment_status

    # Update commission status
    if payment_status == PaymentStatus.PAID and booking.commission:
        booking.commission.status = CommissionStatus.PENDING

    db.commit()
    db.refresh(booking)
    return booking

# Commission CRUD
def get_pending_commissions(db: Session, hostel_id: str = None):
    query = db.query(Commission).filter(Commission.status == CommissionStatus.PENDING)
    if hostel_id:
        query = query.filter(Commission.hostel_id == hostel_id)
    return query.all()

def mark_commission_paid(db: Session, commission_id: str):
    commission = db.query(Commission).filter(Commission.id == commission_id).first()
    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")
    commission.status = CommissionStatus.PAID
    commission.paid_date = datetime.utcnow()
    db.commit()
    db.refresh(commission)
    return commission

# Financial summary
def calculate_financial_summary(db: Session, start_date: datetime, end_date: datetime):
    subscription_revenue = db.query(func.sum(SubscriptionRevenue.amount)).filter(
        and_(SubscriptionRevenue.billing_date >= start_date,
             SubscriptionRevenue.billing_date <= end_date)
    ).scalar() or Decimal("0.00")

    commission_earned = db.query(func.sum(Commission.amount)).filter(
        and_(Commission.earned_date >= start_date,
             Commission.earned_date <= end_date,
             Commission.status != CommissionStatus.PENDING)
    ).scalar() or Decimal("0.00")

    pending_payments = db.query(func.sum(Commission.amount)).filter(
        Commission.status == CommissionStatus.PENDING
    ).scalar() or Decimal("0.00")

    total_income = subscription_revenue + commission_earned

    total_bookings = db.query(func.count(BookingReport.id)).filter(
        and_(BookingReport.created_at >= start_date, BookingReport.created_at <= end_date)
    ).scalar() or 0

    completed_bookings = db.query(func.count(BookingReport.id)).filter(
        and_(BookingReport.created_at >= start_date,
             BookingReport.created_at <= end_date,
             BookingReport.status == BookingStatus.COMPLETED)
    ).scalar() or 0

    cancelled_bookings = db.query(func.count(BookingReport.id)).filter(
        and_(BookingReport.created_at >= start_date,
             BookingReport.created_at <= end_date,
             BookingReport.status == BookingStatus.CANCELLED)
    ).scalar() or 0

    return {
        "total_income": total_income,
        "subscription_revenue": subscription_revenue,
        "commission_earned": commission_earned,
        "pending_payments": pending_payments,
        "total_bookings": total_bookings,
        "completed_bookings": completed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "period_start": start_date,
        "period_end": end_date
    }

# Report generation
def generate_revenue_report(db: Session, start_date: datetime, end_date: datetime, user_id: str):
    data = calculate_financial_summary(db, start_date, end_date)
    daily_revenue = db.query(
        func.date(BookingReport.created_at).label('date'),
        func.sum(BookingReport.amount).label('revenue'),
        func.sum(BookingReport.commission_amount).label('commission')
    ).filter(
        and_(BookingReport.created_at >= start_date,
             BookingReport.created_at <= end_date,
             BookingReport.payment_status == PaymentStatus.PAID)
    ).group_by(func.date(BookingReport.created_at)).all()

    report = Report(
        name=f"Revenue Report ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})",
        report_type=ReportType.REVENUE,
        start_date=start_date,
        end_date=end_date,
        parameters={"type": "revenue"},
        result_data={
            "summary": {
                "total_income": str(data["total_income"]),
                "subscription_revenue": str(data["subscription_revenue"]),
                "commission_earned": str(data["commission_earned"])
            },
            "daily_breakdown": [
                {"date": str(d.date), "revenue": str(d.revenue), "commission": str(d.commission)}
                for d in daily_revenue
            ]
        },
        generated_by=user_id
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def generate_commission_report(db: Session, start_date: datetime, end_date: datetime, user_id: str):
    commissions_by_hostel = db.query(
        Commission.hostel_id,
        BookingReport.hostel_name,
        func.sum(Commission.amount).label('total_commission'),
        func.count(Commission.id).label('booking_count')
    ).join(BookingReport).filter(
        and_(Commission.earned_date >= start_date, Commission.earned_date <= end_date)
    ).group_by(Commission.hostel_id, BookingReport.hostel_name).all()

    pending_total = db.query(func.sum(Commission.amount)).filter(
        and_(Commission.earned_date >= start_date,
             Commission.earned_date <= end_date,
             Commission.status == CommissionStatus.PENDING)
    ).scalar() or Decimal("0.00")

    paid_total = db.query(func.sum(Commission.amount)).filter(
        and_(Commission.earned_date >= start_date,
             Commission.earned_date <= end_date,
             Commission.status == CommissionStatus.PAID)
    ).scalar() or Decimal("0.00")

    report = Report(
        name=f"Commission Report ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})",
        report_type=ReportType.COMMISSION,
        start_date=start_date,
        end_date=end_date,
        parameters={"type": "commission"},
        result_data={
            "summary": {
                "total_pending": str(pending_total),
                "total_paid": str(paid_total),
                "total_earned": str(pending_total + paid_total)
            },
            "by_hostel": [
                {"hostel_id": c.hostel_id, "hostel_name": c.hostel_name,
                 "total_commission": str(c.total_commission), "booking_count": c.booking_count}
                for c in commissions_by_hostel
            ]
        },
        generated_by=user_id
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def get_recent_reports(db: Session, limit: int = 10):
    return db.query(Report).order_by(desc(Report.generated_at)).limit(limit).all()

def get_report_statistics(db: Session):
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    generated_this_month = db.query(func.count(Report.id)).filter(Report.generated_at >= month_start).scalar() or 0
    automated_reports = db.query(func.count(Report.id)).filter(Report.is_automated == True).scalar() or 0
    scheduled_reports = db.query(func.count(Report.id)).filter(Report.is_scheduled == True).scalar() or 0
    return {
        "generated_this_month": generated_this_month,
        "automated_reports": automated_reports,
        "scheduled_reports": scheduled_reports
    }

def get_report_by_id(db: Session, report_id: str):
    return db.query(Report).filter(Report.id == report_id).first()
