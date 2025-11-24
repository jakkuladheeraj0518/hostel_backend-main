from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from app.core.database import get_db
from app.schemas.reports import AttendanceReport, AttendanceTrend
from app.services.analytics_service import AnalyticsService
from app.repositories.hostel_repository import HostelRepository
from fastapi import HTTPException, status


def _validate_hostel(db: Session, hostel_id: int):
    repo = HostelRepository(db)
    if not repo.get_by_id(hostel_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="hostel id not found")

router = APIRouter(prefix="/supervisor/reports", tags=["Supervisor Reports"])

@router.get("/daily-summary")
def get_daily_summary(hostel_id: int, report_date: date = None, db: Session = Depends(get_db)):
    """Get end-of-day operational summary"""
    if not report_date:
        report_date = date.today()
    
    # Validate hostel
    _validate_hostel(db, hostel_id)

    # Attendance summary
    attendance = AnalyticsService.get_attendance_report(db, hostel_id, report_date)
    
    # Complaint summary
    from app.models.complaint import Complaint
    from app.models.hostel import Hostel
    
    # Get hostel name
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id).first()
    hostel_name = hostel.hostel_name if hostel else "Unknown"
    
    # Query complaints for this hostel
    complaints_query = db.query(Complaint).filter(
        Complaint.hostel_name == hostel_name,
        Complaint.created_at >= datetime.combine(report_date, datetime.min.time()),
        Complaint.created_at <= datetime.combine(report_date, datetime.max.time())
    ).all()
    
    new_complaints = len([c for c in complaints_query if c.created_at.date() == report_date])
    resolved_complaints = len([c for c in complaints_query if c.resolved_at and c.resolved_at.date() == report_date])
    
    return {
        "date": report_date,
        "hostel_id": hostel_id,
        "attendance": attendance,
        "complaints": {
            "new": new_complaints,
            "resolved": resolved_complaints,
            "pending": len([c for c in complaints_query if c.status == "pending"])
        },
        "generated_at": datetime.utcnow()
    }

@router.get("/weekly-summary")
def get_weekly_summary(hostel_id: int, end_date: date = None, db: Session = Depends(get_db)):
    """Get weekly performance overview"""
    from app.repositories.complaint_repository import ComplaintRepository
    
    if not end_date:
        end_date = date.today()
    
    start_date = end_date - timedelta(days=7)
    
    # Validate hostel
    _validate_hostel(db, hostel_id)

    # Attendance trends
    attendance_trend = AnalyticsService.get_attendance_trends(db, hostel_id, start_date, end_date)
    
    # Complaint stats
    complaint_stats = ComplaintRepository.get_statistics(
        db, [hostel_id],
        datetime.combine(start_date, datetime.min.time()),
        datetime.combine(end_date, datetime.max.time())
    )
    
    return {
        "period": f"{start_date} to {end_date}",
        "hostel_id": hostel_id,
        "attendance_trends": attendance_trend,
        "complaint_statistics": complaint_stats,
        "generated_at": datetime.utcnow()
    }

@router.get("/monthly-performance")
def get_monthly_performance(hostel_id: int, month: int, year: int, db: Session = Depends(get_db)):
    """Get detailed monthly operational analysis"""
    from calendar import monthrange
    from app.services.analytics_service import AnalyticsService
    
    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)
    
    # Validate hostel
    _validate_hostel(db, hostel_id)

    # Attendance analysis
    attendance_trend = AnalyticsService.get_attendance_trends(db, hostel_id, start_date, end_date)
    
    # Complaint metrics
    complaint_metrics = AnalyticsService.get_complaint_metrics(db, [hostel_id], start_date, end_date)
    
    # Financial summary (if supervisor has access)
    from sqlalchemy import text
    financial = db.execute(text("""
        SELECT 
            SUM(CASE WHEN transaction_type = 'expense' AND amount <= 10000 THEN amount ELSE 0 END) as approved_expenses
        FROM financial_transactions
        WHERE hostel_id = :hostel_id
        AND transaction_date BETWEEN :start_date AND :end_date
    """), {'hostel_id': hostel_id, 'start_date': start_date, 'end_date': end_date}).first()
    
    return {
        "period": f"{month}/{year}",
        "hostel_id": hostel_id,
        "attendance": attendance_trend,
        "complaints": complaint_metrics[0] if complaint_metrics else None,
        "financial": {
            "approved_expenses": float(financial.approved_expenses or 0)
        },
        "generated_at": datetime.utcnow()
    }

@router.get("/attendance/daily")
def get_daily_attendance(hostel_id: int, report_date: date, db: Session = Depends(get_db)):
    """Get attendance report for specific date"""
    _validate_hostel(db, hostel_id)

    return AnalyticsService.get_attendance_report(db, hostel_id, report_date)

@router.get("/attendance/trends")
def get_attendance_trends(hostel_id: int, start_date: date, end_date: date, 
                         db: Session = Depends(get_db)):
    """Get attendance trends over period"""
    _validate_hostel(db, hostel_id)

    return AnalyticsService.get_attendance_trends(db, hostel_id, start_date, end_date)