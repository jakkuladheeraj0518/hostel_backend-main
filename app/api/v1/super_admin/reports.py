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
from app.services.report_services import (
    book_room, change_booking_status, pay_commission,
    get_financial_summary_service, fetch_recent_reports, fetch_report_statistics,
    fetch_report, export_report_file
)

router = APIRouter()

# Dummy current user
def get_current_user():
    return {"user_id": "admin_001", "username": "admin"}

# Booking endpoints
@router.post("/api/bookings", tags=["Bookings"], status_code=status.HTTP_201_CREATED)
def create_new_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    booking = book_room(db, booking_data)
    return {"success": True, "data": BookingResponse.model_validate(booking)}

@router.patch("/api/bookings/{booking_id}/status", tags=["Bookings"])
def update_booking(
    booking_id: str,
    status: str,
    payment_status: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    booking = change_booking_status(db, booking_id, status, payment_status)
    return {"success": True, "data": BookingResponse.model_validate(booking)}

# Commission endpoints
@router.post("/api/commissions/{commission_id}/pay", tags=["Commissions"])
def pay_commission_endpoint(
    commission_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    commission = pay_commission(db, commission_id)
    return {"success": True, "data": CommissionResponse.model_validate(commission)}

# Financial summary
@router.get("/api/financial/summary", tags=["Financial"])
def financial_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    def _parse_date(s: str) -> datetime:
        # Accept ISO format and permissive YYYY-M-D (e.g. 2025-11-1)
        if not s:
            raise ValueError("empty date")
        try:
            return datetime.fromisoformat(s)
        except Exception:
            # Fallback: split and construct (handles single-digit month/day)
            try:
                # allow datetime with time portion (take date part)
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

# Report generation
@router.post("/api/reports/generate", tags=["Reports"])
def generate_report(
    request: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    report_type = request.report_type
    user_id = current_user["user_id"]

    if report_type == "revenue":
        report = generate_revenue = None
        report = __import__('app.repositories.report_repositories', fromlist=['']).generate_revenue_report(db, request.start_date, request.end_date, user_id)
    elif report_type == "commission":
        report = __import__('app.repositories.report_repositories', fromlist=['']).generate_commission_report(db, request.start_date, request.end_date, user_id)
    else:
        raise HTTPException(status_code=400, detail="Unsupported report type")

    return {"success": True, "data": ReportResponse.model_validate(report)}

@router.get("/api/reports/recent", tags=["Reports"])
def list_recent_reports(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    reports = fetch_recent_reports(db, limit)
    return {"success": True, "data": [ReportResponse.model_validate(r) for r in reports]}

@router.get("/api/reports/statistics", tags=["Reports"])
def get_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    stats = fetch_report_statistics(db)
    return {"success": True, "data": ReportStatistics(**stats)}

@router.get("/api/reports/{report_id}", tags=["Reports"])
def get_report(report_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    report = fetch_report(db, report_id)
    return {"success": True, "data": ReportResponse.model_validate(report)}

# Export endpoints
@router.get("/api/reports/{report_id}/export", tags=["Export"])
def export_report(report_id: str, format: Optional[str] = Query(None), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    report = fetch_report(db, report_id)
    # use requested format if provided
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

# Health
@router.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
