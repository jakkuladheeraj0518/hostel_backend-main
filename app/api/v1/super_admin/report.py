from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from typing import List
from app.core.database import get_db
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required, get_current_active_user, get_repository_context, get_user_hostel_ids
from app.core.exceptions import AccessDeniedException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, AdminCreate
from app.repositories.user_repository import UserRepository
from app.services.permission_service import PermissionService
from app.core.security import get_password_hash
from app.schemas.reports import *
from app.services.analytics_service import AnalyticsService
from app.repositories.hostel_repository import HostelRepository
from fastapi import HTTPException, status

router = APIRouter(prefix="/super-admin/reports", tags=["Super Admin Reports"])

@router.get("/dashboard/multi-hostel", response_model=MultiHostelDashboard)
def get_unified_dashboard(
    hostel_ids: List[int] = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    """Get unified multi-hostel dashboard with aggregate KPIs"""
    # Validate hostels
    repo = HostelRepository(db)
    missing = [hid for hid in hostel_ids if not repo.get_by_id(hid)]
    if missing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"hostel id(s) not found: {missing}")

    return AnalyticsService.get_multi_hostel_dashboard(db, hostel_ids, start_date, end_date)

@router.get("/cross-hostel/revenue-comparison")
def get_revenue_comparison(
    hostel_ids: List[int] = Query(...),
    current_start: date = Query(...),
    current_end: date = Query(...),
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Revenue comparison across multiple properties"""
    days_diff = (current_end - current_start).days
    previous_start = current_start - timedelta(days=days_diff)
    previous_end = current_start - timedelta(days=1)
    
    # Validate hostels
    repo = HostelRepository(db)
    missing = [hid for hid in hostel_ids if not repo.get_by_id(hid)]
    if missing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"hostel id(s) not found: {missing}")

    return AnalyticsService.get_revenue_comparison(
        db, hostel_ids, current_start, current_end, previous_start, previous_end
    )

@router.get("/cross-hostel/occupancy-trends")
def get_occupancy_trends(
    hostel_ids: List[int] = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Occupancy trends across multiple hostels"""
    # Validate hostels
    repo = HostelRepository(db)
    missing = [hid for hid in hostel_ids if not repo.get_by_id(hid)]
    if missing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"hostel id(s) not found: {missing}")

    return AnalyticsService.get_occupancy_trends(db, hostel_ids, start_date, end_date)

@router.get("/cross-hostel/complaint-metrics")
def get_complaint_metrics(
    hostel_ids: List[int] = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Complaint metrics across multiple hostels"""
    # Validate hostels
    repo = HostelRepository(db)
    missing = [hid for hid in hostel_ids if not repo.get_by_id(hid)]
    if missing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"hostel id(s) not found: {missing}")

    return AnalyticsService.get_complaint_metrics(db, hostel_ids, start_date, end_date)

@router.get("/marketing/analytics")
def get_marketing_analytics(
    hostel_ids: List[int] = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Marketing analytics across hostels"""
    # Validate hostels
    repo = HostelRepository(db)
    missing = [hid for hid in hostel_ids if not repo.get_by_id(hid)]
    if missing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"hostel id(s) not found: {missing}")

    return AnalyticsService.get_marketing_analytics(db, hostel_ids, start_date, end_date)

@router.get("/marketing/search-trends")
def get_search_trends(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Search trends and user behavior analytics"""
    from sqlalchemy import text
    
    # Top search queries
    top_queries = db.execute(text("""
        SELECT query_text, COUNT(*) as search_count
        FROM search_queries
        WHERE searched_at BETWEEN :start_date AND :end_date
        AND query_text IS NOT NULL AND query_text != ''
        GROUP BY query_text
        ORDER BY search_count DESC
        LIMIT 10
    """), {
        'start_date': datetime.combine(start_date, datetime.min.time()),
        'end_date': datetime.combine(end_date, datetime.max.time())
    }).fetchall()
    
    # Top cities
    top_cities = db.execute(text("""
        SELECT city, COUNT(*) as search_count
        FROM search_queries
        WHERE searched_at BETWEEN :start_date AND :end_date
        AND city IS NOT NULL
        GROUP BY city
        ORDER BY search_count DESC
        LIMIT 10
    """), {
        'start_date': datetime.combine(start_date, datetime.min.time()),
        'end_date': datetime.combine(end_date, datetime.max.time())
    }).fetchall()
    
    # Daily search volume
    daily_volume = db.execute(text("""
        SELECT DATE(searched_at) as date, COUNT(*) as search_count
        FROM search_queries
        WHERE searched_at BETWEEN :start_date AND :end_date
        GROUP BY DATE(searched_at)
        ORDER BY date
    """), {
        'start_date': datetime.combine(start_date, datetime.min.time()),
        'end_date': datetime.combine(end_date, datetime.max.time())
    }).fetchall()
    
    return {
        "period": f"{start_date} to {end_date}",
        "top_queries": [{"query": row.query_text, "count": row.search_count} for row in top_queries],
        "top_cities": [{"city": row.city, "count": row.search_count} for row in top_cities],
        "daily_volume": [{"date": str(row.date), "count": row.search_count} for row in daily_volume]
    }

@router.get("/marketing/booking-conversion")
def get_booking_conversion_rates(
    hostel_ids: List[int] = Query(None),
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Booking conversion rates and revenue attribution"""
    from sqlalchemy import text
    
    where_clause = "WHERE booking_date BETWEEN :start_date AND :end_date"
    params = {
        'start_date': datetime.combine(start_date, datetime.min.time()),
        'end_date': datetime.combine(end_date, datetime.max.time())
    }
    
    if hostel_ids:
        # Validate hostels
        repo = HostelRepository(db)
        missing = [hid for hid in hostel_ids if not repo.get_by_id(hid)]
        if missing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"hostel id(s) not found: {missing}")
        where_clause += " AND hostel_id = ANY(:hostel_ids)"
        params['hostel_ids'] = hostel_ids
    
    bookings = db.execute(text(f"""
        SELECT 
            hostel_id,
            COUNT(*) as total_bookings,
            SUM(CASE WHEN converted THEN 1 ELSE 0 END) as converted_bookings,
            source
        FROM hostel_bookings
        {where_clause}
        GROUP BY hostel_id, source
    """), params).fetchall()
    
    return {
        "period": f"{start_date} to {end_date}",
        "bookings": [
            {
                "hostel_id": row.hostel_id,
                "total_bookings": row.total_bookings,
                "converted_bookings": row.converted_bookings,
                "conversion_rate": (row.converted_bookings / row.total_bookings * 100) if row.total_bookings > 0 else 0,
                "source": row.source
            }
            for row in bookings
        ]
    }

@router.get("/attendance/consolidated", response_model=ConsolidatedAttendanceReport)
def get_consolidated_attendance(
    hostel_ids: List[int] = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Consolidated attendance report across multiple hostels"""
    # Validate hostels
    repo = HostelRepository(db)
    missing = [hid for hid in hostel_ids if not repo.get_by_id(hid)]
    if missing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"hostel id(s) not found: {missing}")

    return AnalyticsService.get_consolidated_attendance_report(
        db, hostel_ids, start_date, end_date
    )