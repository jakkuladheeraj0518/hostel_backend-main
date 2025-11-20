# import json
# from datetime import datetime
# import razorpay
# from fastapi import HTTPException
# from sqlalchemy.orm import Session
# from app.models.payment_models import Payment, Refund, PaymentStatus, PaymentGateway, PaymentMethod
# from app.schemas.payment_schemas import PaymentCreate, RefundCreate
# from app.utils.helpers import generate_order_id
# from app.config import settings
# from app.api.v1.routers.razorpay_client import razorpay_client


# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# class PaymentService:
#     @staticmethod
#     def create_razorpay_order(payment: PaymentCreate, db: Session):
#         try:
#             order_id = generate_order_id()
#             razorpay_order = razorpay_client.order.create({
#                 "amount": int(payment.amount * 100),
#                 "currency": payment.currency,
#                 "receipt": order_id,
#                 "notes": payment.notes or {}
#             })
#             db_payment = Payment(
#                 order_id=order_id,
#                 gateway_order_id=razorpay_order["id"],
#                 gateway=PaymentGateway.RAZORPAY,
#                 amount=payment.amount,
#                 currency=payment.currency,
#                 status=PaymentStatus.INITIATED,
#                 user_id=payment.user_id,
#                 hostel_id=payment.hostel_id,
#                 description=payment.description,
#                 notes=json.dumps(payment.notes),
#                 gateway_response=json.dumps(razorpay_order)
#             )
#             db.add(db_payment)
#             db.commit()
#             db.refresh(db_payment)
#             return db_payment
#         except Exception as e:
#             db.rollback()
#             raise HTTPException(status_code=500, detail=str(e))
from fastapi import HTTPException
from app.repositories.razorpay_repositorys import RazorpayRepository
from app.models.subscription import Payment
from datetime import datetime
import razorpay, os, uuid

# ✅ Razorpay client setup
razorpay_client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_KEY_SECRET")
))

class RazorpayService:
    @staticmethod
    def create_order(db, request):
        # ✅ Validate user
        user = RazorpayRepository.get_user_by_id(db, request.user_id)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid user_id: User does not exist")

        # ✅ Validate hostel
        hostel = RazorpayRepository.get_hostel_by_id(db, request.hostel_id)
        if not hostel:
            raise HTTPException(status_code=400, detail="Invalid hostel_id: Hostel does not exist")

        # ✅ Prepare Razorpay order payload
        order_data = {
            "amount": int(request.amount * 100),
            "currency": request.currency,
            "receipt": f"rcpt_{uuid.uuid4().hex[:8]}",
            "notes": {
                "user_id": request.user_id,
                "hostel_id": request.hostel_id,
                "description": request.description
            },
        }

        # ✅ Create order in Razorpay
        razorpay_order = razorpay_client.order.create(order_data)

        # ✅ Store in DB
        payment = Payment(
            order_id=razorpay_order["id"],
            gateway_order_id=razorpay_order["id"],
            gateway="razorpay",
            amount=request.amount,
            currency=request.currency,
            status="initiated",
            user_id=request.user_id,
            hostel_id=request.hostel_id,
            description=request.description,
            created_at=datetime.utcnow()
        )

        RazorpayRepository.save_payment(db, payment)

        return {
            "message": "Order created successfully",
            "razorpay_order": razorpay_order,
            "local_payment_id": payment.id
        }

#payments,partial payments, refunds, customers, and generates PDF receipts.
# app/services/payment_service.py
# from datetime import datetime
# import uuid
# from app.models.payment_models import Invoice, Transaction, Receipt, RefundRequest, TransactionType, PaymentStatus
# from app.repositories.payment_repository import PaymentRepository
# from app.utils.receipt_generator import generate_receipt_pdf
# from sqlalchemy.orm import Session

# def generate_invoice_number():
#     return f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

# def generate_transaction_id():
#     return f"TXN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"

# def generate_receipt_number():
#     return f"RCP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

# def generate_refund_id():
#     return f"RFN-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

# class PaymentService:

#     @staticmethod
#     def create_invoice(db: Session, user_id: int, hostel_id: int, items: list, description: str, due_date):
#         total = sum(i['amount'] for i in items)
#         inv = Invoice(
#             invoice_number=generate_invoice_number(),
#             user_id=user_id,
#             hostel_id=hostel_id,
#             total_amount=total,
#             paid_amount=0.0,
#             due_amount=total,
#             description=description,
#             items=__import__("json").dumps(items),
#             due_date=due_date,
#             status=PaymentStatus.PENDING
#         )
#         return PaymentRepository.create_invoice(db, inv)

#     @staticmethod
#     def process_payment(db: Session, invoice_id: int, amount: float, payment_method: str, payment_gateway: str=None, gateway_transaction_id: str=None, notes: str=None, processed_by: int=None):
#         invoice = PaymentRepository.get_invoice(db, invoice_id)
#         if not invoice:
#             raise ValueError("Invoice not found")
#         if amount > invoice.due_amount:
#             raise ValueError("Amount exceeds due amount")
#         txn = Transaction(
#             transaction_id=generate_transaction_id(),
#             invoice_id=invoice.id,
#             transaction_type=TransactionType.PAYMENT,
#             amount=amount,
#             payment_method=payment_method,
#             payment_gateway=payment_gateway,
#             gateway_transaction_id=gateway_transaction_id,
#             notes=notes,
#             status="success",
#             processed_by=processed_by
#         )
#         PaymentRepository.save_transaction(db, txn)

#         # update invoice
#         invoice.paid_amount += amount
#         invoice.due_amount -= amount
#         invoice.updated_at = datetime.utcnow()
#         if invoice.due_amount <= 0:
#             invoice.status = PaymentStatus.COMPLETED
#             invoice.due_amount = 0
#         elif invoice.paid_amount > 0:
#             invoice.status = PaymentStatus.PARTIAL
#         db.commit()
#         db.refresh(txn)

#         # create receipt
#         receipt = Receipt(
#             receipt_number=generate_receipt_number(),
#             invoice_id=invoice.id,
#             transaction_id=txn.id,
#             amount=txn.amount,
#             qr_code_data=f"R:{generate_receipt_number()}|A:{txn.amount}"
#         )
#         PaymentRepository.save_receipt(db, receipt)

#         # generate pdf synchronously (you can move to background)
#         pdf_path = generate_receipt_pdf(receipt, invoice, txn)
#         receipt.pdf_path = pdf_path
#         db.commit()
#         db.refresh(receipt)

#         return txn

#     @staticmethod
#     def request_refund(db: Session, transaction_id: int, refund_amount: float, reason: str, requested_by: int):
#         txn = PaymentRepository.get_transaction(db, transaction_id)
#         if not txn:
#             raise ValueError("Transaction not found")
#         refund = RefundRequest(
#             refund_id=generate_refund_id(),
#             transaction_id=txn.id,
#             invoice_id=txn.invoice_id,
#             refund_amount=refund_amount,
#             reason=reason,
#             requested_by=requested_by,
#             status='initiated'
#         )
#         return PaymentRepository.create_refund_request(db, refund)



# from datetime import datetime
# import uuid, json
# from sqlalchemy.orm import Session
# from app.models.payment_models import (
#     Invoice, Transaction, Receipt, RefundRequest,
#     TransactionType, PaymentStatus
# )
# from app.repositories.payment_repository import PaymentRepository
# from app.utils.receipt_generator import generate_receipt_pdf


# # -------------------------------------------------------------------
# # 🔹 Helper ID Generators
# # -------------------------------------------------------------------
# def generate_invoice_number():
#     return f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

# def generate_transaction_id():
#     return f"TXN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"

# def generate_receipt_number():
#     return f"RCP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

# def generate_refund_id():
#     return f"RFN-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


# # -------------------------------------------------------------------
# # 💳 Payment Service Layer
# # -------------------------------------------------------------------
# class PaymentService:

#     # ---------------------------------------------------------------
#     # 🧾 Create Invoice
#     # ---------------------------------------------------------------
#     @staticmethod
#     def create_invoice(db: Session, user_id: int, hostel_id: int, items: list, description: str, due_date):
#         total = sum(i['amount'] for i in items)
#         invoice = Invoice(
#             invoice_number=generate_invoice_number(),
#             user_id=user_id,
#             hostel_id=hostel_id,
#             total_amount=total,
#             paid_amount=0.0,
#             due_amount=total,
#             description=description,
#             items=json.dumps(items),
#             due_date=due_date,
#             status=PaymentStatus.PENDING.value  # ✅ ensure lowercase enum value
#         )
#         return PaymentRepository.create_invoice(db, invoice)


#     # ---------------------------------------------------------------
#     # 💰 Process Payment → Creates Transaction + Receipt
#     # ---------------------------------------------------------------
#     @staticmethod
#     def process_payment(
#         db: Session,
#         invoice_id: int,
#         amount: float,
#         payment_method: str,
#         payment_gateway: str = None,
#         gateway_transaction_id: str = None,
#         notes: str = None,
#         processed_by: int = None
#     ):
#         try:
#             invoice = PaymentRepository.get_invoice(db, invoice_id)
#             if not invoice:
#                 raise ValueError("Invoice not found")

#             if amount > invoice.due_amount:
#                 raise ValueError(f"Amount exceeds due amount ₹{invoice.due_amount}")

#             # 💳 Create Transaction
#             txn = Transaction(
#                 transaction_id=generate_transaction_id(),
#                 invoice_id=invoice.id,
#                 transaction_type=TransactionType.PAYMENT,
#                 amount=amount,
#                 payment_method=payment_method,
#                 payment_gateway=payment_gateway,
#                 gateway_transaction_id=gateway_transaction_id,
#                 notes=notes,
#                 status="success",
#                 processed_by=processed_by
#             )
#             PaymentRepository.save_transaction(db, txn)

#             # 💡 Update Invoice status and amounts
#             invoice.paid_amount += amount
#             invoice.due_amount = max(invoice.due_amount - amount, 0)
#             invoice.updated_at = datetime.utcnow()

#             if invoice.due_amount <= 0:
#                 invoice.status = PaymentStatus.COMPLETED.value
#                 invoice.due_amount = 0
#             elif invoice.paid_amount > 0:
#                 invoice.status = PaymentStatus.PARTIAL.value

#             db.commit()
#             db.refresh(invoice)
#             db.refresh(txn)

#             # 🧾 Create Receipt (always, even if PDF fails)
#             receipt_number = generate_receipt_number()
#             receipt = Receipt(
#                 receipt_number=receipt_number,
#                 invoice_id=invoice.id,
#                 transaction_id=txn.id,
#                 amount=txn.amount,
#                 qr_code_data=f"Receipt:{receipt_number}|Amount:{txn.amount}|Date:{datetime.utcnow().isoformat()}",
#                 generated_at=datetime.utcnow()
#             )
#             PaymentRepository.save_receipt(db, receipt)

#             # 🧾 Try generating PDF
#             try:
#                 pdf_path = generate_receipt_pdf(receipt, invoice, txn, db)
#                 receipt.pdf_path = pdf_path
#                 db.commit()
#                 db.refresh(receipt)
#                 print(f"✅ Receipt generated successfully: {receipt.receipt_number}")
#             except Exception as pdf_error:
#                 db.commit()  # commit even if PDF fails
#                 print(f"⚠️ PDF generation failed for receipt {receipt.receipt_number}: {pdf_error}")

#             return txn

#         except Exception as e:
#             db.rollback()
#             print(f"❌ Payment processing error: {e}")
#             raise ValueError(f"Payment processing failed: {str(e)}")


#     # ---------------------------------------------------------------
#     # 💸 Request Refund
#     # ---------------------------------------------------------------
#     @staticmethod
#     def request_refund(db: Session, transaction_id: int, refund_amount: float, reason: str, requested_by: int):
#         txn = PaymentRepository.get_transaction(db, transaction_id)
#         if not txn:
#             raise ValueError("Transaction not found")

#         refund = RefundRequest(
#             refund_id=generate_refund_id(),
#             transaction_id=txn.id,
#             invoice_id=txn.invoice_id,
#             refund_amount=refund_amount,
#             reason=reason,
#             requested_by=requested_by,
#             status='initiated'
#         )
#         return PaymentRepository.create_refund_request(db, refund)

from datetime import datetime
import uuid, json
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.payment_models import (
    Invoice, Transaction, Receipt, RefundRequest,
    TransactionType
)
from app.models.subscription import Payment
from app.models.subscription import PaymentStatus
from app.repositories.payment_repositorys import PaymentRepository
from app.utils.receipt_generatorss import generate_receipt_pdf


# -------------------------------------------------------------------
# 🔹 Helper ID Generators
# -------------------------------------------------------------------
def generate_invoice_number():
    return f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

def generate_transaction_id():
    return f"TXN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"

def generate_receipt_number():
    return f"RCP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

def generate_refund_id():
    return f"RFN-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


# -------------------------------------------------------------------
# 💳 Payment Service Layer
# -------------------------------------------------------------------
class PaymentService:

    # ---------------------------------------------------------------
    # 🧾 Create Invoice
    # ---------------------------------------------------------------
    @staticmethod
    def create_invoice(db: Session, user_id: int, hostel_id: int, items: list, description: str, due_date):
        total = sum(i['amount'] for i in items)
        invoice = Invoice(
            invoice_number=generate_invoice_number(),
            user_id=user_id,
            hostel_id=hostel_id,
            total_amount=total,
            paid_amount=0.0,
            due_amount=total,
            description=description,
            items=json.dumps(items),
            due_date=due_date,
            status=PaymentStatus.pending.value  # ✅ ensure lowercase enum value
        )
        return PaymentRepository.create_invoice(db, invoice)


    # ---------------------------------------------------------------
    # 💰 Process Payment → Creates Transaction + Receipt
    # ---------------------------------------------------------------
    @staticmethod
    def process_payment(
        db: Session,
        invoice_id: int,
        amount: float,
        payment_method: str,
        payment_gateway: str = None,
        gateway_transaction_id: str = None,
        notes: str = None,
        processed_by: int = None
    ):
        try:
            # 1️⃣ Validate invoice
            invoice = PaymentRepository.get_invoice(db, invoice_id)
            if not invoice:
                raise ValueError("Invoice not found")

            if amount > invoice.due_amount:
                raise ValueError(f"Amount exceeds due amount ₹{invoice.due_amount}")
            # 2️⃣ ALWAYS create a Payment entry for invoice payments
            payment = Payment(
                user_id=invoice.user_id,
                hostel_id=invoice.hostel_id,
                amount=amount,
                currency="INR",
                status=PaymentStatus.succeeded.value,
                description=notes or "Invoice payment",
                created_at=datetime.utcnow()
                )
            db.add(payment)
            db.commit()
            db.refresh(payment)
            payment_id = payment.id


            # 2️⃣ Find related Payment automatically
            
            # payment = (
            #     db.query(Payment)
            #     .filter(
            #         Payment.user_id == invoice.user_id,
            #         Payment.hostel_id == invoice.hostel_id
            #     )
            #     .order_by(Payment.created_at.desc())
            #     .first()
            # )
            # payment_id = payment.id if payment else None

            # 3️⃣ Create Transaction
            txn = Transaction(
                transaction_id=generate_transaction_id(),
                payment_id=payment_id,  # ✅ Auto-linked
                invoice_id=invoice.id,
                transaction_type=TransactionType.PAYMENT,
                amount=amount,
                payment_method=payment_method,
                payment_gateway=payment_gateway,
                gateway_transaction_id=gateway_transaction_id,
                notes=notes,
                status="success",
                processed_by=processed_by,
                created_at=datetime.utcnow()
            )
            PaymentRepository.save_transaction(db, txn)

            # 4️⃣ Update Invoice totals and status
            invoice.paid_amount += amount
            invoice.due_amount = max(invoice.due_amount - amount, 0)
            invoice.updated_at = datetime.utcnow()

            if invoice.due_amount <= 0:
                invoice.status = PaymentStatus.succeeded.value   
                invoice.due_amount = 0
            elif invoice.paid_amount > 0:
                invoice.status = PaymentStatus.pending.value

            # 5️⃣ Update Payment status too (if exists)
            if payment:
                payment.status = PaymentStatus.succeeded.value
                payment.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(invoice)
            db.refresh(txn)

            # 6️⃣ Generate Receipt
            receipt_number = generate_receipt_number()
            receipt = Receipt(
                receipt_number=receipt_number,
                invoice_id=invoice.id,
                transaction_id=txn.id,
                payment_id=txn.payment_id,
                amount=txn.amount,
                qr_code_data=f"Receipt:{receipt_number}|Amount:{txn.amount}|Date:{datetime.utcnow().isoformat()}",
                generated_at=datetime.utcnow()
            )
            PaymentRepository.save_receipt(db, receipt)

            # 7️⃣ Try generating PDF
            try:
                pdf_path = generate_receipt_pdf(receipt, invoice, txn, db)
                receipt.pdf_path = pdf_path
                db.commit()
                db.refresh(receipt)
                print(f"✅ Receipt generated successfully: {receipt.receipt_number}")
            except Exception as pdf_error:
                db.commit()  # commit even if PDF generation fails
                print(f"⚠️ PDF generation failed for {receipt.receipt_number}: {pdf_error}")

            return txn

        except Exception as e:
            db.rollback()
            print(f"❌ Payment processing error: {e}")
            raise ValueError(f"Payment processing failed: {str(e)}")


    # ---------------------------------------------------------------
    # 💸 Request Refund
    # ---------------------------------------------------------------
    @staticmethod
    def request_refund(
        db: Session,
        transaction_id: int,
        refund_amount: float,
        reason: str,
        requested_by: int
    ):
        txn = PaymentRepository.get_transaction(db, transaction_id)
        if not txn:
            raise ValueError("Transaction not found")

        refund = RefundRequest(
            refund_id=generate_refund_id(),
            transaction_id=txn.id,
            invoice_id=txn.invoice_id,
            refund_amount=refund_amount,
            reason=reason,
            requested_by=requested_by,
            status="initiated"
        )
        return PaymentRepository.create_refund_request(db, refund)


# app/services/refund_service.py
# from sqlalchemy.orm import Session
# from datetime import datetime
# import uuid
# from typing import Dict
# from app.repositories.payment_repository import RefundRepository
# from app.repositories.invoice_repository import InvoiceRepository
# from app.models.payment_models import TransactionType, PaymentStatus
# from app.schemas.payment_schemas import RefundApproval

# class RefundService:
#     """Business logic for refund operations"""
    
#     def __init__(self, db: Session):
#         self.db = db
#         self.refund_repo = RefundRepository(db)
#         self.invoice_repo = InvoiceRepository(db)
    
#     @staticmethod
#     def generate_transaction_id() -> str:
#         """Generate unique transaction ID"""
#         timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
#         unique_id = uuid.uuid4().hex[:8].upper()
#         return f"TXN-{timestamp}-{unique_id}"
    
#     def calculate_invoice_status(self, paid_amount: float, due_amount: float) -> str:
#         """Determine invoice status based on payment amounts"""
#         if paid_amount <= 0:
#             return PaymentStatus.PENDING.value
#         elif due_amount > 0:
#             return PaymentStatus.PARTIAL.value
#         else:
#             return PaymentStatus.SUCCESS.value
    
#     def approve_refund(self, refund_id: int, approval: RefundApproval) -> Dict:
#         """Approve a refund request and update invoice"""
#         refund = self.refund_repo.get_by_id(refund_id)
#         if not refund:
#             raise ValueError("Refund request not found")
        
#         if refund.status not in ["initiated", "processing"]:
#             raise ValueError(f"Refund already {refund.status}")

#         try:
#             txn_id = self.generate_transaction_id()
#             transaction_data = {
#                 "transaction_id": txn_id,
#                 "invoice_id": refund.invoice_id,
#                 "transaction_type": TransactionType.REFUND.value,
#                 "amount": -abs(refund.refund_amount),
#                 "payment_method": "refund",
#                 "notes": f"Refund processed: {refund.reason}",
#                 "status": "success",
#                 "processed_by": approval.approved_by,
#                 "created_at": datetime.utcnow()
#             }
#             txn = self.refund_repo.create_refund_transaction(transaction_data)

#             invoice = self.invoice_repo.get_by_id(refund.invoice_id)
#             if not invoice:
#                 raise ValueError("Invoice linked to refund not found")

#             new_paid = max(invoice.paid_amount - refund.refund_amount, 0)
#             new_due = invoice.due_amount + refund.refund_amount
#             new_status = self.calculate_invoice_status(new_paid, new_due)

#             self.invoice_repo.update_payment_status(invoice, new_paid, new_due, new_status)

#             self.refund_repo.update_status(
#                 refund,
#                 status="completed",
#                 approved_by=approval.approved_by,
#                 processed_at=datetime.utcnow(),
#                 completed_at=datetime.utcnow()
#             )

#             self.db.commit()
#             self.db.refresh(refund)

#             return {
#                 "success": True,
#                 "message": "Refund approved successfully",
#                 "refund": {
#                     "refund_id": refund.refund_id,
#                     "status": refund.status,
#                     "refund_amount": refund.refund_amount,
#                     "approved_by": refund.approved_by,
#                     "processed_at": refund.processed_at,
#                     "completed_at": refund.completed_at,
#                 },
#                 "transaction_id": txn_id
#             }

#         except Exception as e:
#             self.db.rollback()
#             raise Exception(f"Refund approval failed: {str(e)}")

#     def reject_refund(self, refund_id: int, approval: RefundApproval) -> Dict:
#         """Reject a refund request"""
#         refund = self.refund_repo.get_by_id(refund_id)
#         if not refund:
#             raise ValueError("Refund request not found")
#         if refund.status not in ["initiated", "processing"]:
#             raise ValueError(f"Refund already {refund.status}")
        
#         try:
#             self.refund_repo.update_status(
#                 refund,
#                 status="rejected",
#                 rejection_reason=approval.rejection_reason,
#                 approved_by=approval.approved_by,
#                 processed_at=datetime.utcnow()
#             )
#             self.db.commit()
#             self.db.refresh(refund)

#             return {
#                 "success": True,
#                 "message": "Refund request rejected",
#                 "refund": {
#                     "refund_id": refund.refund_id,
#                     "status": refund.status,
#                     "refund_amount": refund.refund_amount,
#                     "approved_by": refund.approved_by,
#                     "rejection_reason": refund.rejection_reason,
#                     "processed_at": refund.processed_at,
#                 }
#             }

#         except Exception as e:
#             self.db.rollback()
#             raise Exception(f"Refund rejection failed: {str(e)}")


