# from sqlalchemy.orm import Session
# from sqlalchemy import func, extract
# from typing import List, Optional, Dict
# from datetime import date
# from app.models.fee_structure_models import Hostel
# from app.models.payment_models import Transaction, Invoice, Customer

# class LedgerRepository:
#     def __init__(self, db: Session):
#         self.db = db

#     def get_complete_transaction_history(
#         self,
#         start_date: Optional[date],
#         end_date: Optional[date],
#         hostel_id: Optional[int],
#         user_id: Optional[int],     # 🔥 Changed
#         transaction_type: Optional[str],
#         limit: int,
#         offset: int
#     ):
#         query = self.db.query(Transaction).join(Invoice)

#         if start_date:
#             query = query.filter(Transaction.created_at >= start_date)

#         if end_date:
#             query = query.filter(Transaction.created_at <= end_date)

#         if hostel_id:
#             query = query.filter(Invoice.hostel_id == hostel_id)

#         if user_id:
#             query = query.filter(Invoice.user_id == user_id)   # 🔥 Changed

#         if transaction_type:
#             query = query.filter(Transaction.transaction_type == transaction_type)

#         total = query.count()
#         rows = query.order_by(Transaction.created_at.desc()).limit(limit).offset(offset).all()
#         return rows, total

#     def get_outstanding_payments(self, hostel_id: Optional[int], overdue_only: bool):
#         query = self.db.query(Invoice).filter(Invoice.due_amount > 0)

#         if hostel_id:
#             query = query.filter(Invoice.hostel_id == hostel_id)

#         if overdue_only:
#             query = query.filter(Invoice.due_date < date.today())

#         return query.order_by(Invoice.due_date).all()

#     def get_user_ledger(self, user_id: int):   # 🔥 Renamed from get_student_ledger
#         user = self.db.query(Customer).filter(Customer.id == user_id).first()
#         if not user:
#             return None

#         invoices = self.db.query(Invoice).filter(Invoice.user_id == user_id).all()

#         return {
#             "user": user,
#             "invoices": invoices,
#             "summary": {
#                 "total_billed": sum(i.total_amount for i in invoices),
#                 "total_paid": sum(i.paid_amount for i in invoices),
#                 "total_outstanding": sum(i.due_amount for i in invoices),
#             }
#         }


# class ReportRepository:
#     def __init__(self, db: Session):
#         self.db = db

#     def get_revenue_by_hostel(self, start_date, end_date):
#         query = self.db.query(
#             Hostel.id,
#             Hostel.name,
#             # Hostel.code,
#             func.sum(Invoice.total_amount).label("total_billed"),
#             func.sum(Invoice.paid_amount).label("total_collected"),
#             func.sum(Invoice.due_amount).label("total_outstanding")
#         ).join(Invoice)

#         if start_date:
#             query = query.filter(Invoice.created_at >= start_date)
#         if end_date:
#             query = query.filter(Invoice.created_at <= end_date)

#         query = query.group_by(Hostel.id, Hostel.name, Hostel.name)
#         rows = query.all()

#         return [
#             {
#                 "hostel_id": r.id,
#                 "hostel_name": r.name,
#                 # "hostel_code": r.code,
#                 "total_billed": float(r.total_billed or 0),
#                 "total_collected": float(r.total_collected or 0),
#                 "total_outstanding": float(r.total_outstanding or 0),
#             }
#             for r in rows
#         ]
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional
from datetime import date

from app.models.hostel import Hostel
from app.models.payment_models import Transaction, Invoice, Customer


class LedgerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_complete_transaction_history(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        hostel_id: Optional[int],
        user_id: Optional[int],
        transaction_type: Optional[str],
        limit: int,
        offset: int
    ):
        query = self.db.query(Transaction).join(Invoice)

        if start_date:
            query = query.filter(Transaction.created_at >= start_date)

        if end_date:
            query = query.filter(Transaction.created_at <= end_date)

        if hostel_id:
            query = query.filter(Invoice.hostel_id == hostel_id)

        if user_id:
            query = query.filter(Invoice.user_id == user_id)

        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)

        total = query.count()
        rows = (
            query.order_by(Transaction.created_at.desc())
                 .limit(limit)
                 .offset(offset)
                 .all()
        )

        return rows, total

    def get_outstanding_payments(self, hostel_id: Optional[int], overdue_only: bool):
        query = self.db.query(Invoice).filter(Invoice.due_amount > 0)

        if hostel_id:
            query = query.filter(Invoice.hostel_id == hostel_id)

        if overdue_only:
            query = query.filter(Invoice.due_date < date.today())

        return query.order_by(Invoice.due_date).all()

    def get_user_ledger(self, user_id: int):
        user = self.db.query(Customer).filter(Customer.id == user_id).first()
        if not user:
            return None

        invoices = self.db.query(Invoice).filter(Invoice.user_id == user_id).all()

        return {
            "user": user,
            "invoices": invoices,
            "summary": {
                "total_billed": sum(invoice.total_amount for invoice in invoices),
                "total_paid": sum(invoice.paid_amount for invoice in invoices),
                "total_outstanding": sum(invoice.due_amount for invoice in invoices),
            }
        }


# class ReportRepository:
#     def __init__(self, db: Session):
#         self.db = db

#     def get_revenue_by_hostel(self, start_date, end_date):
#         query = self.db.query(
#             Hostel.id,
#             Hostel.name,
#             func.sum(Invoice.total_amount).label("total_billed"),
#             func.sum(Invoice.paid_amount).label("total_collected"),
#             func.sum(Invoice.due_amount).label("total_outstanding"),
#         ).join(Invoice)

#         if start_date:
#             query = query.filter(Invoice.created_at >= start_date)

#         if end_date:
#             query = query.filter(Invoice.created_at <= end_date)

#         query = query.group_by(Hostel.id, Hostel.name)
#         rows = query.all()

#         return [
#             {
#                 "hostel_id": r.id,
#                 "hostel_name": r.name,
#                 "total_billed": float(r.total_billed or 0),
#                 "total_collected": float(r.total_collected or 0),
#                 "total_outstanding": float(r.total_outstanding or 0),
#             }
#             for r in rows
#         ]

#     # ------------------------------------------------------------
#     # 📌 Monthly Revenue Report (Correctly inside the class)
#     # ------------------------------------------------------------
#     def get_monthly_revenue_report(self, year: int, hostel_id: int = None):
#         query = self.db.query(
#             extract("month", Invoice.created_at).label("month"),
#             func.sum(Invoice.total_amount).label("total_billed"),
#             func.sum(Invoice.paid_amount).label("total_collected"),
#             func.count(Invoice.id).label("invoice_count"),
#         ).filter(extract("year", Invoice.created_at) == year)

#         if hostel_id:
#             query = query.filter(Invoice.hostel_id == hostel_id)

#         query = query.group_by("month").order_by("month")
#         rows = query.all()

#         return [
#             {
#                 "month": int(r.month),
#                 "total_billed": float(r.total_billed or 0),
#                 "total_collected": float(r.total_collected or 0),
#                 "invoice_count": r.invoice_count,
#                 "collection_rate": (
#                     (float(r.total_collected or 0) / float(r.total_billed or 1)) * 100
#                 ),
#             }
#             for r in rows
#         ]
    

#     # You can add: get_payment_method_breakdown() here if needed
class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_revenue_by_hostel(self, start_date, end_date):
        query = self.db.query(
            Hostel.id,
            Hostel.hostel_name,
            func.sum(Invoice.total_amount).label("total_billed"),
            func.sum(Invoice.paid_amount).label("total_collected"),
            func.sum(Invoice.due_amount).label("total_outstanding")
        ).join(Invoice)

        if start_date:
            query = query.filter(Invoice.created_at >= start_date)
        if end_date:
            query = query.filter(Invoice.created_at <= end_date)

        query = query.group_by(Hostel.id, Hostel.hostel_name)
        rows = query.all()

        return [
            {
                "hostel_id": r.id,
                "hostel_name": r.hostel_name,
                "total_billed": float(r.total_billed or 0),
                "total_collected": float(r.total_collected or 0),
                "total_outstanding": float(r.total_outstanding or 0),
            }
            for r in rows
        ]

    def get_monthly_revenue_report(self, year: int, hostel_id: int = None):
        query = self.db.query(
            extract("month", Invoice.created_at).label("month"),
            func.sum(Invoice.total_amount).label("total_billed"),
            func.sum(Invoice.paid_amount).label("total_collected"),
            func.count(Invoice.id).label("invoice_count"),
        ).filter(extract("year", Invoice.created_at) == year)

        if hostel_id:
            query = query.filter(Invoice.hostel_id == hostel_id)

        query = query.group_by("month").order_by("month")

        rows = query.all()

        return [
            {
                "month": int(r.month),
                "total_billed": float(r.total_billed or 0),
                "total_collected": float(r.total_collected or 0),
                "invoice_count": r.invoice_count,
                "collection_rate": (
                    (float(r.total_collected or 0) / float(r.total_billed or 1)) * 100
                ),
            }
            for r in rows
        ]

    def get_payment_method_breakdown(self, start_date=None, end_date=None, hostel_id=None):
        from app.models.subscription import Payment

        query = self.db.query(
            Payment.payment_method,
            func.count(Payment.id).label("count"),
            func.sum(Payment.amount).label("total_amount")
        )

        if start_date:
            query = query.filter(Payment.created_at >= start_date)

        if end_date:
            query = query.filter(Payment.created_at <= end_date)

        if hostel_id:
            query = query.filter(Payment.hostel_id == hostel_id)

        query = query.group_by(Payment.payment_method)

        rows = query.all()

        return [
            {
                "payment_method": r.payment_method,
                "count": r.count,
                "total_amount": float(r.total_amount or 0.0)
            }
            for r in rows
        ]
