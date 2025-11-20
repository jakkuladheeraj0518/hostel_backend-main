# app/repositories/payment_repository.py
from sqlalchemy.orm import Session
from app.models.payment_models import Invoice, Transaction, Receipt, RefundRequest

class PaymentRepository:

    @staticmethod
    def create_invoice(db: Session, invoice: Invoice):
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def get_invoice(db: Session, invoice_id: int):
        return db.query(Invoice).filter(Invoice.id == invoice_id).first()

    @staticmethod
    def list_user_invoices(db: Session, user_id: int, status=None):
        q = db.query(Invoice).filter(Invoice.user_id == user_id)
        if status:
            q = q.filter(Invoice.status == status)
        return q.order_by(Invoice.created_at.desc()).all()

    @staticmethod
    def save_transaction(db: Session, txn: Transaction):
        db.add(txn)
        db.commit()
        db.refresh(txn)
        return txn

    @staticmethod
    def get_transaction(db: Session, transaction_id: int):
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()

    @staticmethod
    def save_receipt(db: Session, receipt: Receipt):
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        return receipt

    @staticmethod
    def get_receipt_by_transaction(db: Session, transaction_id: int):
        return db.query(Receipt).filter(Receipt.transaction_id == transaction_id).first()

    @staticmethod
    def create_refund_request(db: Session, refund: RefundRequest):
        db.add(refund)
        db.commit()
        db.refresh(refund)
        return refund

    @staticmethod
    def get_refund(db: Session, refund_id: int):
        return db.query(RefundRequest).filter(RefundRequest.id == refund_id).first()

# app/repositories/refund_repository.py
# from sqlalchemy.orm import Session
# from typing import Optional, List
# from app.models.payment_models import RefundRequest, Transaction
# from datetime import datetime

# class RefundRepository:
#     """Data access layer for refund operations"""
    
#     def __init__(self, db: Session):
#         self.db = db
    
#     def get_by_id(self, refund_id: int) -> Optional[RefundRequest]:
#         """Fetch refund by ID"""
#         return self.db.query(RefundRequest).filter(RefundRequest.id == refund_id).first()
    
#     def get_by_refund_id(self, refund_id: str) -> Optional[RefundRequest]:
#         """Fetch refund by refund_id string"""
#         return self.db.query(RefundRequest).filter(RefundRequest.refund_id == refund_id).first()
    
#     def get_pending_refunds(self) -> List[RefundRequest]:
#         """Get all refunds awaiting approval"""
#         return self.db.query(RefundRequest).filter(
#             RefundRequest.status.in_(["initiated", "processing"])
#         ).all()
    
#     def update_status(self, refund: RefundRequest, status: str, **kwargs) -> RefundRequest:
#         """Update refund status and related fields"""
#         refund.status = status
#         for key, value in kwargs.items():
#             if hasattr(refund, key):
#                 setattr(refund, key, value)
#         self.db.flush()
#         return refund
    
#     def create_refund_transaction(self, transaction_data: dict) -> Transaction:
#         """Create a refund transaction record"""
#         txn = Transaction(**transaction_data)
#         self.db.add(txn)
#         self.db.flush()
#         return txn
