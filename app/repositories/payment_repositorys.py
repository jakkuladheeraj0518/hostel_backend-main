# app/repositories/payment_repository.py

from sqlalchemy.orm import Session
from app.models.payment_models import (
    Invoice, Transaction, Receipt, RefundRequest
)
from app.models.subscription import Payment   # your Payment model


class PaymentRepository:

    # ------------------------------
    # INVOICE METHODS
    # ------------------------------
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

    # ------------------------------
    # PAYMENT METHODS  (MISSING earlier!)
    # ------------------------------
    @staticmethod
    def save_payment(db: Session, payment: Payment):
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def get_payment(db: Session, payment_id: str):
        return db.query(Payment).filter(Payment.id == payment_id).first()

    @staticmethod
    def get_payment_by_transaction(db: Session, transaction_id: int):
        txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not txn:
            return None
        return db.query(Payment).filter(Payment.id == txn.payment_id).first()

    # ------------------------------
    # TRANSACTION METHODS
    # ------------------------------
    @staticmethod
    def save_transaction(db: Session, txn: Transaction):
        db.add(txn)
        db.commit()
        db.refresh(txn)
        return txn

    @staticmethod
    def get_transaction(db: Session, transaction_id: int):
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()

    # ------------------------------
    # RECEIPT METHODS
    # ------------------------------
    @staticmethod
    def save_receipt(db: Session, receipt: Receipt):
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        return receipt

    @staticmethod
    def get_receipt_by_transaction(db: Session, transaction_id: int):
        return db.query(Receipt).filter(Receipt.transaction_id == transaction_id).first()

    # ------------------------------
    # REFUND METHODS
    # ------------------------------
    @staticmethod
    def create_refund_request(db: Session, refund: RefundRequest):
        db.add(refund)
        db.commit()
        db.refresh(refund)
        return refund

    @staticmethod
    def get_refund(db: Session, refund_id: int):
        return db.query(RefundRequest).filter(RefundRequest.id == refund_id).first()
