from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
 
from app.repositories.report_repositories import (
    create_booking, update_booking_status, get_pending_commissions, mark_commission_paid,
    calculate_financial_summary, generate_revenue_report, generate_commission_report,
    get_recent_reports, get_report_statistics, get_report_by_id, get_financial_summaries
)
from app.utils.utils import generate_pdf_report, generate_csv_report, generate_excel_report
 
 
 
def book_room(db: Session, booking_data):
    return create_booking(db, booking_data)
 
def change_booking_status(db: Session, booking_id: str, status, payment_status):
    return update_booking_status(db, booking_id, status, payment_status)
 
def list_pending_commissions(db: Session, hostel_id: str = None):
    return get_pending_commissions(db, hostel_id)
 
def pay_commission(db: Session, commission_id: str):
    return mark_commission_paid(db, commission_id)
 
def get_financial_summary_service(db: Session, start_date: datetime, end_date: datetime):
    return calculate_financial_summary(db, start_date, end_date)
 
def fetch_recent_reports(db: Session, limit: int = 10):
    return get_recent_reports(db, limit)
 
 
def fetch_financial_summaries_service(db: Session, start_date: datetime = None, end_date: datetime = None, limit: int = 50):
    return get_financial_summaries(db, start_date, end_date, limit)
 
def fetch_report_statistics(db: Session):
    return get_report_statistics(db)
 
def fetch_report(db: Session, report_id: str):
    report = get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
 
def export_report_file(report):
    export_format = (report.export_format or "pdf").lower()
    data = {
        "id": report.id,
        "name": report.name,
        "result_data": report.result_data or {}
    }
    print("Export format:", export_format)
    print("Result data keys:", data["result_data"].keys())  # check keys exist
    print("Daily breakdown length:", len(data["result_data"].get("daily_breakdown", [])))
   
    if export_format == "pdf":
        return generate_pdf_report(data)
    if export_format == "csv":
        return generate_csv_report(data)
    if export_format == "excel":
        return generate_excel_report(data)
    raise HTTPException(status_code=400, detail="Unsupported export format")
 
 
 