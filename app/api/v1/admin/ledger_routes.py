from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.services.ledger_service import LedgerService
from app.core.database import get_db


router = APIRouter(prefix="/ledger", tags=["Payment Ledger & Reports"])


# ---------------------------------------------------------
# 🔹 Transaction History (user_id instead of student_id)
# ---------------------------------------------------------
@router.get("/transactions")
def get_transaction_history(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    hostel_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),       # 🔥 updated
    transaction_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    return LedgerService(db).get_transaction_history(
        start_date=start_date,
        end_date=end_date,
        hostel_id=hostel_id,
        user_id=user_id,                          # 🔥 updated
        transaction_type=transaction_type,
        page=page,
        page_size=page_size
    )


# ---------------------------------------------------------
# 🔹 Outstanding Payments
# ---------------------------------------------------------
@router.get("/outstanding")
def get_outstanding_payments(
    hostel_id: Optional[int] = Query(None),
    overdue_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    return LedgerService(db).get_outstanding_payments_report(
        hostel_id=hostel_id,
        overdue_only=overdue_only
    )


# ---------------------------------------------------------
# 🔹 Revenue by Hostel
# ---------------------------------------------------------
@router.get("/reports/revenue-by-hostel")
def get_revenue_by_hostel(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    return LedgerService(db).get_revenue_report_by_hostel(
        start_date=start_date,
        end_date=end_date
    )


# ---------------------------------------------------------
# 🔹 Monthly Revenue
# ---------------------------------------------------------
@router.get("/reports/monthly-revenue/{year}")
def monthly_revenue(
    year: int,
    hostel_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    return LedgerService(db).report_repo.get_monthly_revenue_report(
        year=year,
        hostel_id=hostel_id
    )


# ---------------------------------------------------------
# 🔹 Payment Method Breakdown
# ---------------------------------------------------------
# @router.get("/reports/payment-methods")
# def payment_methods(
#     start_date: Optional[date] = None,
#     end_date: Optional[date] = None,
#     hostel_id: Optional[int] = None,
#     db: Session = Depends(get_db)
# ):
#     return LedgerService(db).report_repo.get_payment_method_breakdown(
#         start_date=start_date,
#         end_date=end_date,
#         hostel_id=hostel_id
#     )
