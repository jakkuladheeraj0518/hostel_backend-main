

 
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from fastapi.responses import StreamingResponse
 
from app.core.database import get_db
from app.schemas.report_schemas import (
    BookingCreate, BookingResponse, CommissionResponse,
    ReportGenerateRequest, ReportResponse, FinancialSummaryResponse, ReportStatistics
)
 
# RBAC imports
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required
from app.models.user import User
 
from app.services.report_services import (
    book_room, change_booking_status, pay_commission,
    get_financial_summary_service, fetch_recent_reports,
    fetch_report_statistics, fetch_report, export_report_file, fetch_financial_summaries_service
)
 
router = APIRouter()
 
 
# -----------------------------------------------------------
# BOOKING — Admin + Supervisor + SuperAdmin
# -----------------------------------------------------------
@router.post("/api/bookings", tags=["Bookings"], status_code=status.HTTP_201_CREATED)
def create_new_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_BOOKINGS)),
):
    booking = book_room(db, booking_data)
    return {"success": True, "data": BookingResponse.model_validate(booking)}
 
 
# -----------------------------------------------------------
# UPDATE BOOKING STATUS — Admin + Supervisor + SuperAdmin
# -----------------------------------------------------------
@router.patch("/api/bookings/{booking_id}/status", tags=["Bookings"])
def update_booking(
    booking_id: str,
    status: str,
    payment_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_BOOKINGS)),
):
    booking = change_booking_status(db, booking_id, status, payment_status)
    return {"success": True, "data": BookingResponse.model_validate(booking)}
 
 
# -----------------------------------------------------------
# PAY COMMISSION — Admin + SuperAdmin
# -----------------------------------------------------------
@router.post("/api/commissions/{commission_id}/pay", tags=["Commissions"])
def pay_commission_endpoint(
    commission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_COMMISSIONS)),
):
    commission = pay_commission(db, commission_id)
    return {"success": True, "data": CommissionResponse.model_validate(commission)}
 
 
# -----------------------------------------------------------
# FINANCIAL SUMMARY — Admin + SuperAdmin
# -----------------------------------------------------------
@router.get("/api/financial/summary", tags=["Financial"])
def financial_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.VIEW_FINANCIALS)),
):
    def _parse_date(s: str) -> datetime:
        if not s:
            raise ValueError("empty date")
        try:
            return datetime.fromisoformat(s)
        except Exception:
            try:
                date_part = s.split('T')[0]
                y, m, d = date_part.split('-')
                return datetime(int(y), int(m), int(d))
            except Exception:
                raise HTTPException(status_code=400, detail=f"Invalid date format: {s}")
 
    if not start_date or not end_date:
        now = datetime.utcnow()
        start = datetime(now.year, now.month, 1)
        from calendar import monthrange
        _, last_day = monthrange(now.year, now.month)
        end = datetime(now.year, now.month, last_day, 23, 59, 59)
    else:
        start = _parse_date(start_date)
        end = _parse_date(end_date)
 
    summary = get_financial_summary_service(db, start, end)
    return {"success": True, "data": FinancialSummaryResponse(**summary)}
 
 
@router.get("/api/financial/summaries", tags=["Financial"])
def list_financial_summaries(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.VIEW_FINANCIALS)),
):
    def _parse_date(s: str) -> datetime:
        if not s:
            raise ValueError("empty date")
        try:
            return datetime.fromisoformat(s)
        except Exception:
            try:
                date_part = s.split('T')[0]
                y, m, d = date_part.split('-')
                return datetime(int(y), int(m), int(d))
            except Exception:
                raise HTTPException(status_code=400, detail=f"Invalid date format: {s}")
 
    start = _parse_date(start_date) if start_date else None
    end = _parse_date(end_date) if end_date else None
 
    rows = fetch_financial_summaries_service(db, start, end, limit)
    return {"success": True, "data": [FinancialSummaryResponse(
        total_income=r.total_income,
        subscription_revenue=r.subscription_revenue,
        commission_earned=r.commission_earned,
        pending_payments=r.pending_payments,
        total_bookings=r.total_bookings,
        completed_bookings=r.completed_bookings,
        cancelled_bookings=r.cancelled_bookings,
        period_start=r.period_start,
        period_end=r.period_end
    ) for r in rows]}
 
 
# -----------------------------------------------------------
# GENERATE REPORT — Admin + SuperAdmin
# -----------------------------------------------------------
@router.post("/api/reports/generate", tags=["Reports"])
def generate_report(
    request: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_REPORTS)),
):
    report_type = request.report_type
    user_id = current_user.id
 
    repo = __import__('app.repositories.report_repositories', fromlist=[''])
 
    if report_type == "revenue":
        report = repo.generate_revenue_report(db, request.start_date, request.end_date, user_id)
    elif report_type == "commission":
        report = repo.generate_commission_report(db, request.start_date, request.end_date, user_id)
    else:
        raise HTTPException(status_code=400, detail="Unsupported report type")
 
    return {"success": True, "data": ReportResponse.model_validate(report)}
 
 
# -----------------------------------------------------------
# RECENT REPORTS — Admin + SuperAdmin
# -----------------------------------------------------------
@router.get("/api/reports/recent", tags=["Reports"])
def list_recent_reports(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.VIEW_REPORTS)),
):
    reports = fetch_recent_reports(db, limit)
    return {"success": True, "data": [ReportResponse.model_validate(r) for r in reports]}
 
 
# -----------------------------------------------------------
# REPORT STATISTICS — Admin + SuperAdmin
# -----------------------------------------------------------
@router.get("/api/reports/statistics", tags=["Reports"])
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.VIEW_REPORTS)),
):
    stats = fetch_report_statistics(db)
    return {"success": True, "data": ReportStatistics(**stats)}
 
 
# -----------------------------------------------------------
# GET REPORT — Admin + SuperAdmin
# -----------------------------------------------------------
@router.get("/api/reports/{report_id}", tags=["Reports"])
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.VIEW_REPORTS)),
):
    report = fetch_report(db, report_id)
    return {"success": True, "data": ReportResponse.model_validate(report)}
 
 
# -----------------------------------------------------------
# EXPORT REPORT — Admin + SuperAdmin
# -----------------------------------------------------------
@router.get("/api/reports/{report_id}/export", tags=["Export"])
def export_report(
    report_id: str,
    format: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
    _: None = Depends(permission_required(Permission.EXPORT_REPORTS)),
):
    report = fetch_report(db, report_id)
 
    if format:
        report.export_format = format
 
    file_stream = export_report_file(report)
    export_format = (report.export_format or "pdf").lower()
 
    content_type = {
        "pdf": "application/pdf",
        "csv": "text/csv",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }.get(export_format, "application/octet-stream")
 
    filename = f"report_{report.id}.{export_format if export_format != 'excel' else 'xlsx'}"
 
    return StreamingResponse(
        file_stream,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
 
 
 