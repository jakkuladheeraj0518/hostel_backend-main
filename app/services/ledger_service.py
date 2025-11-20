from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import date
from app.repositories.ledger_repositorys import LedgerRepository, ReportRepository

class LedgerService:
    def __init__(self, db: Session):
        self.db = db
        self.ledger_repo = LedgerRepository(db)
        self.report_repo = ReportRepository(db)

    def get_transaction_history(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        hostel_id: Optional[int],
        user_id: Optional[int],          # 🔥 updated
        transaction_type: Optional[str],
        page: int,
        page_size: int
    ):
        offset = (page - 1) * page_size

        transactions, total = self.ledger_repo.get_complete_transaction_history(
            start_date=start_date,
            end_date=end_date,
            hostel_id=hostel_id,
            user_id=user_id,              # 🔥 updated
            transaction_type=transaction_type,
            limit=page_size,
            offset=offset
        )

        return {
            "transactions": transactions,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        }

    def get_outstanding_payments_report(self, hostel_id, overdue_only):
        invoices = self.ledger_repo.get_outstanding_payments(hostel_id, overdue_only)

        overdue = [
            i for i in invoices
            if i.due_date and i.due_date.date() < date.today()]


        return {
            "invoices": invoices,
            "summary": {
                "total_outstanding": sum(i.due_amount for i in invoices),
                "invoice_count": len(invoices),
                "overdue_count": len(overdue),
                "overdue_amount": sum(i.due_amount for i in overdue),
            }
        }

    def get_revenue_report_by_hostel(self, start_date, end_date):
        hostel_data = self.report_repo.get_revenue_by_hostel(start_date, end_date)

        return {
            "hostels": hostel_data,
            "summary": {
                "total_billed": sum(h["total_billed"] for h in hostel_data),
                "total_collected": sum(h["total_collected"] for h in hostel_data),
                "total_outstanding": sum(h["total_outstanding"] for h in hostel_data),
            }
        }
