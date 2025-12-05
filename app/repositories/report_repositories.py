from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
 
 
def get_hostel_occupancy_and_revenue(db: Session, hostel_id: int):
    """Try calling PostgreSQL stored procedure get_hostel_occupancy_and_revenue.
 
    If the function does not exist in the connected database (UndefinedFunction),
    fall back to a direct query that returns the latest occupancy and revenue
    for the given hostel. This prevents the ASGI app from crashing when the
    migration or function creation hasn't been applied.
    """
    query = text("SELECT * FROM get_hostel_occupancy_and_revenue(:hostel_id)")
    try:
        result = db.execute(query, {"hostel_id": hostel_id}).fetchall()
    except ProgrammingError:
        # The DB function likely doesn't exist. The failed execution leaves the
        # current transaction in an aborted state — roll back the session so we
        # can safely run the fallback query in a clean transaction.
        try:
            db.rollback()
        except Exception:
            # If rollback itself fails, ignore and attempt fallback (caller will
            # see any remaining DB errors). We don't want to mask the original
            # error details here.
            pass
 
        # Fallback to a direct query.
        fallback_query = text(
            """
            SELECT o.occupancy_rate, r.revenue, h.hostel_name
            FROM hostels h
            LEFT JOIN (
                SELECT occupancy_rate, hostel_id
                FROM occupancies
                WHERE hostel_id = :hostel_id
                ORDER BY month DESC
                LIMIT 1
            ) o ON h.id = o.hostel_id
            LEFT JOIN (
                SELECT revenue, hostel_id
                FROM revenues
                WHERE hostel_id = :hostel_id
                ORDER BY month DESC
                LIMIT 1
            ) r ON h.id = r.hostel_id
            WHERE h.id = :hostel_id
            """
        )
        result = db.execute(fallback_query, {"hostel_id": hostel_id}).fetchall()
 
    # Fetch hostel canonical values once to use as fallback when proc/fallback
    # returns NULLs.
    hostel_row = db.execute(
        text("SELECT hostel_name, current_occupancy, monthly_revenue FROM hostels WHERE id = :hostel_id"),
        {"hostel_id": hostel_id}
    ).fetchone()
 
    hostel_name = hostel_row[0] if hostel_row is not None else None
    hostel_current = hostel_row[1] if hostel_row is not None else None
    hostel_revenue = hostel_row[2] if hostel_row is not None else None
 
    # Convert to list of dictionaries for easy JSON serialization
    out = []
    for row in result:
        # Stored proc may return (occupancy, revenue) or (occupancy, revenue, hostel_name)
        occ = row[0] if len(row) > 0 else None
        rev = row[1] if len(row) > 1 else None
        name = row[2] if len(row) > 2 else None
 
        # Fill missing values from hostels table
        if occ is None:
            occ = hostel_current
        if rev is None:
            rev = hostel_revenue
        if not name:
            name = hostel_name
 
        out.append({
            "current_occupancy": occ,
            "monthly_revenue": rev,
            "hostel_name": name,
        })
 
    return out
 
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from fastapi import HTTPException
from datetime import datetime
from decimal import Decimal
 
from app.models.report_models import (
    BookingReport, Commission, SubscriptionRevenue, Report, FinancialSummary,
    BookingStatus, PaymentStatus, CommissionStatus, ReportType
)
from app.models.subscription import organizationPayment, PaymentStatus as SubPaymentStatus, PaymentType as SubPaymentType
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
    # Treat end_date as inclusive (include the whole end day)
    end_date_inclusive = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
 
    # Sum explicit subscription revenue records
    subscription_revenue = db.query(func.sum(SubscriptionRevenue.amount)).filter(
        and_(SubscriptionRevenue.billing_date >= start_date,
             SubscriptionRevenue.billing_date <= end_date_inclusive)
    ).scalar() or Decimal("0.00")
 
    # Also include organisation-level payments for subscriptions (some deployments use this table)
    try:
        org_subscription_payments = db.query(func.sum(organizationPayment.amount)).filter(
            and_(organizationPayment.paid_at >= start_date,
                 organizationPayment.paid_at <= end_date_inclusive,
                 organizationPayment.payment_type == SubPaymentType.subscription,
                 organizationPayment.status == SubPaymentStatus.succeeded)
        ).scalar() or Decimal("0.00")
    except Exception:
        # If the organisation payments model/table isn't present in this deployment, ignore it
        org_subscription_payments = Decimal("0.00")
 
    # Combine both sources
    subscription_revenue = (subscription_revenue or Decimal("0.00")) + (org_subscription_payments or Decimal("0.00"))
 
    # Commissions earned (excluding pending) within the period
    commission_earned = db.query(func.sum(Commission.amount)).filter(
        and_(Commission.earned_date >= start_date,
             Commission.earned_date <= end_date_inclusive,
             Commission.status != CommissionStatus.PENDING)
    ).scalar() or Decimal("0.00")
 
    # Pending commissions within the period
    pending_payments = db.query(func.sum(Commission.amount)).filter(
        and_(Commission.earned_date >= start_date,
             Commission.earned_date <= end_date_inclusive,
             Commission.status == CommissionStatus.PENDING)
    ).scalar() or Decimal("0.00")
 
    total_income = subscription_revenue + commission_earned
 
    total_bookings = db.query(func.count(BookingReport.id)).filter(
        and_(BookingReport.created_at >= start_date, BookingReport.created_at <= end_date_inclusive)
    ).scalar() or 0
 
    completed_bookings = db.query(func.count(BookingReport.id)).filter(
        and_(BookingReport.created_at >= start_date,
             BookingReport.created_at <= end_date_inclusive,
             BookingReport.status == BookingStatus.COMPLETED)
    ).scalar() or 0
 
    cancelled_bookings = db.query(func.count(BookingReport.id)).filter(
        and_(BookingReport.created_at >= start_date,
             BookingReport.created_at <= end_date_inclusive,
             BookingReport.status == BookingStatus.CANCELLED)
    ).scalar() or 0
 
    # Build summary dict
    summary = {
        "total_income": total_income,
        "subscription_revenue": subscription_revenue,
        "commission_earned": commission_earned,
        "pending_payments": pending_payments,
        "total_bookings": total_bookings,
        "completed_bookings": completed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "period_start": start_date,
        "period_end": end_date_inclusive
    }
 
    # Persist the summary into financial_summaries matching by date-only (ignore time)
    try:
        existing = db.query(FinancialSummary).filter(
            func.date(FinancialSummary.period_start) == start_date.date(),
            func.date(FinancialSummary.period_end) == end_date_inclusive.date()
        ).first()
        if existing:
            existing.total_income = summary["total_income"]
            existing.subscription_revenue = summary["subscription_revenue"]
            existing.commission_earned = summary["commission_earned"]
            existing.pending_payments = summary["pending_payments"]
            existing.total_bookings = summary["total_bookings"]
            existing.completed_bookings = summary["completed_bookings"]
            existing.cancelled_bookings = summary["cancelled_bookings"]
            db.add(existing)
        else:
            fs = FinancialSummary(
                period_start=summary["period_start"],
                period_end=summary["period_end"],
                total_income=summary["total_income"],
                subscription_revenue=summary["subscription_revenue"],
                commission_earned=summary["commission_earned"],
                pending_payments=summary["pending_payments"],
                total_bookings=summary["total_bookings"],
                completed_bookings=summary["completed_bookings"],
                cancelled_bookings=summary["cancelled_bookings"]
            )
            db.add(fs)
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
 
    return summary
 
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
    # Ensure end_date includes the full day by setting to end of day
    end_date_inclusive = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
   
    print(f"\n[DEBUG] Commission Report Query Parameters:")
    print(f"  start_date: {start_date}")
    print(f"  end_date_inclusive: {end_date_inclusive}")
   
    # Count total commissions in database
    total_count = db.query(func.count(Commission.id)).scalar()
    print(f"  Total commissions in DB: {total_count}")
   
    # Count commissions matching date range
    matching_count = db.query(func.count(Commission.id)).filter(
        and_(Commission.earned_date >= start_date, Commission.earned_date <= end_date_inclusive)
    ).scalar()
    print(f"  Commissions matching date range: {matching_count}")
   
    commissions_by_hostel = db.query(
        Commission.hostel_id,
        BookingReport.hostel_name,
        func.sum(Commission.amount).label('total_commission'),
        func.count(Commission.id).label('booking_count')
    ).join(BookingReport).filter(
        and_(Commission.earned_date >= start_date, Commission.earned_date <= end_date_inclusive)
    ).group_by(Commission.hostel_id, BookingReport.hostel_name).all()
 
    pending_total = db.query(func.sum(Commission.amount)).filter(
        and_(Commission.earned_date >= start_date,
             Commission.earned_date <= end_date_inclusive,
             Commission.status == CommissionStatus.PENDING)
    ).scalar() or Decimal("0.00")
 
    paid_total = db.query(func.sum(Commission.amount)).filter(
        and_(Commission.earned_date >= start_date,
             Commission.earned_date <= end_date_inclusive,
             Commission.status == CommissionStatus.PAID)
    ).scalar() or Decimal("0.00")
   
    print(f"  pending_total: {pending_total}")
    print(f"  paid_total: {paid_total}")
 
    # Fetch detailed commission records
    detailed_commissions = db.query(Commission).filter(
        and_(Commission.earned_date >= start_date, Commission.earned_date <= end_date_inclusive)
    ).order_by(Commission.earned_date.desc()).all()
   
    print(f"  detailed_commissions count: {len(detailed_commissions)}")
    for c in detailed_commissions:
        print(f"    - {c.id}: amount={c.amount}, earned_date={c.earned_date}, status={c.status}")
 
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
            ],
            "commissions": [
                {
                    "id": c.id,
                    "booking_id": c.booking_id,
                    "amount": str(c.amount),
                    "status": c.status.value if c.status else "unknown",
                    "earned_date": c.earned_date.strftime('%Y-%m-%d %H:%M:%S') if c.earned_date else "",
                    "paid_date": c.paid_date.strftime('%Y-%m-%d %H:%M:%S') if c.paid_date else "Not Paid",
                    "hostel_id": c.hostel_id,
                    "platform_revenue": str(c.platform_revenue)
                }
                for c in detailed_commissions
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
 
 
def get_financial_summaries(db: Session, start_date: datetime = None, end_date: datetime = None, limit: int = 50):
    """Return persisted FinancialSummary rows filtered by optional date range."""
    query = db.query(FinancialSummary).order_by(FinancialSummary.period_start.desc())
    if start_date:
        query = query.filter(FinancialSummary.period_start >= start_date)
    if end_date:
        # treat provided end_date as inclusive
        end_inclusive = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        query = query.filter(FinancialSummary.period_end <= end_inclusive)
    return query.limit(limit).all()
 
 