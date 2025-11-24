from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List
from app.core.database import get_db
from app.schemas.reports import *
from app.services.analytics_service import AnalyticsService
from app.repositories.hostel_repository import HostelRepository
from fastapi import HTTPException, status


def _validate_hostel(db: Session, hostel_id: int):
    repo = HostelRepository(db)
    if not repo.get_by_id(hostel_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="hostel id not found")



router = APIRouter(prefix="/admin/reports", tags=["Admin Reports"])

@router.get("/dashboard")
def get_admin_dashboard(
    hostel_id: int,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard for a single hostel"""
    if not start_date:
        start_date = date.today().replace(day=1)  # First day of current month
    if not end_date:
        end_date = date.today()
    
    # Validate hostel
    _validate_hostel(db, hostel_id)

    # Get KPI
    kpi = AnalyticsService._get_hostel_kpi(db, hostel_id, start_date, end_date)
    
    # Get complaint metrics
    complaint_metrics = AnalyticsService.get_complaint_metrics(db, [hostel_id], start_date, end_date)
    
    # Get marketing analytics
    marketing = AnalyticsService.get_marketing_analytics(db, [hostel_id], start_date, end_date)
    
    # Get recent complaints
    from app.models.complaint import Complaint
    from app.models.hostel import Hostel
    
    # Get hostel name
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id).first()
    hostel_name = hostel.hostel_name if hostel else "Unknown"
    
    # Query recent complaints for this hostel
    recent_complaints = db.query(Complaint).filter(
        Complaint.hostel_name == hostel_name,
        Complaint.created_at >= datetime.combine(start_date, datetime.min.time()),
        Complaint.created_at <= datetime.combine(end_date, datetime.max.time())
    ).limit(10).all()
    
    return {
        "hostel_id": hostel_id,
        "period": f"{start_date} to {end_date}",
        "kpi": kpi,
        "complaints": complaint_metrics[0] if complaint_metrics else None,
        "marketing": marketing[0] if marketing else None,
        "recent_complaints": recent_complaints,
        "generated_at": datetime.utcnow()
    }

@router.get("/financial/income")
def get_income_statement(
    hostel_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Get income statement for hostel"""
    from sqlalchemy import text
    
    # Validate hostel
    _validate_hostel(db, hostel_id)

    result = db.execute(text("""
        SELECT 
            transaction_type,
            category,
            SUM(amount) as total_amount,
            COUNT(*) as transaction_count
        FROM financial_transactions
        WHERE hostel_id = :hostel_id
        AND transaction_date BETWEEN :start_date AND :end_date
        GROUP BY transaction_type, category
        ORDER BY transaction_type, category
    """), {'hostel_id': hostel_id, 'start_date': start_date, 'end_date': end_date}).fetchall()
    
    revenue = sum(float(row.total_amount) for row in result if row.transaction_type in ['fee', 'booking'])
    expenses = sum(float(row.total_amount) for row in result if row.transaction_type == 'expense')
    
    return {
        "hostel_id": hostel_id,
        "period": f"{start_date} to {end_date}",
        "revenue": revenue,
        "expenses": expenses,
        "profit": revenue - expenses,
        "breakdown": [
            {
                "type": row.transaction_type,
                "category": row.category,
                "amount": float(row.total_amount),
                "count": row.transaction_count
            }
            for row in result
        ]
    }

@router.get("/financial/outstanding-payments")
def get_outstanding_payments(hostel_id: int, db: Session = Depends(get_db)):
    """Get outstanding payment tracking"""
    from sqlalchemy import text
    
    # Validate hostel
    _validate_hostel(db, hostel_id)

    result = db.execute(text("""
        SELECT 
            student_id,
            SUM(amount) as outstanding_amount,
            COUNT(*) as pending_count
        FROM financial_transactions
        WHERE hostel_id = :hostel_id
        AND payment_status = 'pending'
        AND transaction_type = 'fee'
        GROUP BY student_id
        ORDER BY outstanding_amount DESC
    """), {'hostel_id': hostel_id}).fetchall()
    
    return {
        "hostel_id": hostel_id,
        "total_outstanding": sum(float(row.outstanding_amount) for row in result),
        "students": [
            {
                "student_id": row.student_id,
                "outstanding_amount": float(row.outstanding_amount),
                "pending_count": row.pending_count
            }
            for row in result
        ]
    }

@router.get("/operational/occupancy")
def get_occupancy_report(hostel_id: int, start_date: date, end_date: date, 
                        db: Session = Depends(get_db)):
    """Get occupancy reports"""
    # Validate hostel
    _validate_hostel(db, hostel_id)

    trends = AnalyticsService.get_occupancy_trends(db, [hostel_id], start_date, end_date)
    return {"trends": trends}

@router.get("/operational/demographics")
def get_student_demographics(hostel_id: int, db: Session = Depends(get_db)):
    """Get student demographic analysis"""
    from sqlalchemy import text
    
    # Validate hostel
    _validate_hostel(db, hostel_id)

    # This would require a students table - simplified version
    result = db.execute(text("""
        SELECT 
            COUNT(DISTINCT sa.student_id) as total_students
        FROM student_attendance sa
        JOIN users u ON u.id::text = sa.student_id
        WHERE u.hostel_id = :hostel_id
        AND sa.attendance_date >= CURRENT_DATE - INTERVAL '30 days'
    """), {'hostel_id': hostel_id}).first()
    
    return {
        "hostel_id": hostel_id,
        "total_students": result.total_students or 0
    }

@router.get("/operational/attendance-patterns")
def get_attendance_patterns(hostel_id: int, start_date: date, end_date: date,
                           db: Session = Depends(get_db)):
    """Get attendance patterns and trends"""
    # Validate hostel
    _validate_hostel(db, hostel_id)

    return AnalyticsService.get_attendance_trends(db, hostel_id, start_date, end_date)

@router.get("/operational/complaints")
def get_complaint_metrics(hostel_id: int, start_date: date, end_date: date,
                         db: Session = Depends(get_db)):
    """Get complaint resolution metrics"""
    # Validate hostel
    _validate_hostel(db, hostel_id)

    metrics = AnalyticsService.get_complaint_metrics(db, [hostel_id], start_date, end_date)
    return metrics[0] if metrics else {}

@router.get("/operational/maintenance-costs")
def get_maintenance_costs(hostel_id: int, start_date: date, end_date: date,
                         db: Session = Depends(get_db)):
    """Get maintenance costs and trend analysis"""
    from sqlalchemy import text
    
    # Validate hostel
    _validate_hostel(db, hostel_id)

    # complaints table stores `hostel_name` not `hostel_id`; resolve name first
    from app.models.hostel import Hostel

    hostel = db.query(Hostel).filter(Hostel.id == hostel_id).first()
    hostel_name = hostel.hostel_name if hostel else None

    result = db.execute(text("""
        SELECT 
            DATE_TRUNC('month', resolved_at) as month,
            COUNT(*) as complaint_count,
            SUM(actual_cost) as total_cost,
            AVG(actual_cost) as avg_cost
        FROM complaints
        WHERE hostel_name = :hostel_name
        AND resolved_at BETWEEN :start_date AND :end_date
        AND actual_cost IS NOT NULL
        GROUP BY DATE_TRUNC('month', resolved_at)
        ORDER BY month
    """), {'hostel_name': hostel_name, 'start_date': datetime.combine(start_date, datetime.min.time()), 
           'end_date': datetime.combine(end_date, datetime.max.time())}).fetchall()
    
    return {
        "hostel_id": hostel_id,
        "period": f"{start_date} to {end_date}",
        "monthly_breakdown": [
            {
                "month": str(row.month),
                "complaint_count": row.complaint_count,
                "total_cost": float(row.total_cost or 0),
                "average_cost": float(row.avg_cost or 0)
            }
            for row in result
        ]
    }

@router.get("/marketing/profile-views")
def get_profile_analytics(hostel_id: int, start_date: date, end_date: date,
                         db: Session = Depends(get_db)):
    """Get hostel profile view analytics"""
    # Validate hostel
    _validate_hostel(db, hostel_id)

    analytics = AnalyticsService.get_marketing_analytics(db, [hostel_id], start_date, end_date)
    return analytics[0] if analytics else {}

@router.get("/multi-hostel/comparison")
def compare_hostels(
    hostel_ids: List[int] = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    """Compare revenue and performance across hostels"""
    # Validate hostels
    repo = HostelRepository(db)
    missing = [hid for hid in hostel_ids if not repo.get_by_id(hid)]
    if missing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"hostel id(s) not found: {missing}")

    return AnalyticsService.get_revenue_comparison(
        db, hostel_ids, start_date, end_date,
        start_date - timedelta(days=(end_date - start_date).days),
        start_date - timedelta(days=1)
    )