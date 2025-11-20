# # app/repositories/invoice_repository.py
# from sqlalchemy.orm import Session
# from typing import Optional
# from app.models.payment_models import Invoice
# from datetime import datetime

# class InvoiceRepository:
#     """Data access layer for invoice operations"""
    
#     def __init__(self, db: Session):
#         self.db = db
    
#     def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
#         """Fetch invoice by ID"""
#         return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
#     def update_payment_status(self, invoice: Invoice, paid_amount: float, due_amount: float, status: str):
#         """Update invoice payment details"""
#         invoice.paid_amount = paid_amount
#         invoice.due_amount = due_amount
#         invoice.status = status
#         invoice.updated_at = datetime.utcnow()
#         self.db.flush()
#         return invoice
