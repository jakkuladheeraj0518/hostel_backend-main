from fastapi import HTTPException
from app.repositories.razorpay_repositorys import RazorpayRepository
from app.models.subscription import Payment
from app.models.payment_models import PaymentStatus_hms
from app.models.user import User
from datetime import datetime
import  os, uuid
from app.core.razorpay_client import razorpay_client

# ✅ Razorpay client setup
# razorpay_client = razorpay.Client(auth=(
#     os.getenv("RAZORPAY_KEY_ID"),
#     os.getenv("RAZORPAY_KEY_SECRET")
# ))

class RazorpayService:
    @staticmethod
    def create_order(db, request, current_user):
        # ✅ Validate user
        # user = RazorpayRepository.get_user_by_id(db, request.user_id)
        # if not user:
        #     raise HTTPException(status_code=400, detail="Invalid user_id: User does not exist")

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
                "user_id":current_user.id,
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
            status="pending",
            user_id=current_user.id,
            # user_id=request.user_id,
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



from datetime import datetime
import uuid, json
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.payment_models import (
    Invoice, Transaction, Receipt, RefundRequest,
    TransactionType
)
from app.models.subscription import Payment
from app.models.payment_models import PaymentStatus_hms
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
            items=items,
            due_date=due_date,
            status=PaymentStatus_hms.pending.value  # ✅ ensure lowercase enum value
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

            # if amount < invoice.due_amount:
            #     raise ValueError(f"Amount exceeds due amount ₹{invoice.due_amount}")
            # 2️⃣ ALWAYS create a Payment entry for invoice payments
            payment = Payment(
                user_id=invoice.user_id,
                hostel_id=invoice.hostel_id,
                amount=amount,
                currency="INR",
                status="success",
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
                notes=json.dumps({"msg": notes}) if notes else None,   # ✅ FIXED,
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
                invoice.status = PaymentStatus_hms.success.value   
                invoice.due_amount = 0
            elif invoice.paid_amount > 0:
                invoice.status = PaymentStatus_hms.pending.value

            # 5️⃣ Update Payment status too (if exists)
            if payment:
                payment.status = PaymentStatus_hms.success.value
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
    # 💸 Refund – User Requests Refund
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

        invoice = PaymentRepository.get_invoice(db, txn.invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")

        if refund_amount > invoice.paid_amount:
            raise ValueError("Refund amount cannot exceed paid amount")

        refund = RefundRequest(
            refund_id=generate_refund_id(),
            transaction_id=txn.id,
            invoice_id=invoice.id,
            refund_amount=refund_amount,
            reason=reason,
            requested_by=requested_by,
            status="initiated"
        )

        PaymentRepository.create_refund_request(db, refund)

        return {
            "message": "Refund request submitted",
            "refund_id": refund.id,
            "refund_ref": refund.refund_id,
            "status": refund.status,
        }
        

    @staticmethod
    def approve_refund(
        db: Session,
        refund_id: int,
        approved_by: int
    ):
        refund = PaymentRepository.get_refund(db, refund_id)
        if not refund:
            raise ValueError("Refund request not found")

        original_txn = PaymentRepository.get_transaction(db, refund.transaction_id)
        if not original_txn:
            raise ValueError("Original transaction not found")

        if not original_txn.payment_id:
            raise ValueError("Payment ID missing — cannot process refund")

        # 1️⃣ Create Refund Transaction
        refund_txn = Transaction(
            transaction_id=generate_transaction_id(),
            payment_id=original_txn.payment_id,
            invoice_id=refund.invoice_id,
            transaction_type=TransactionType.REFUND,
            amount=-refund.refund_amount,
            payment_method="refund",
            notes=f"Refund processed: {refund.reason}",
            status="success",
            processed_by=approved_by,
            created_at=datetime.utcnow(),
        )
        PaymentRepository.save_transaction(db, refund_txn)

        # 2️⃣ Update Invoice
        invoice = PaymentRepository.get_invoice(db, refund.invoice_id)
        invoice.paid_amount -= refund.refund_amount
        invoice.due_amount += refund.refund_amount

        invoice.paid_amount = max(invoice.paid_amount, 0)
        invoice.due_amount = max(invoice.due_amount, 0)

        if invoice.paid_amount == 0:
            invoice.status = PaymentStatus_hms.pending.value
        else:
            invoice.status = "partial"

        invoice.updated_at = datetime.utcnow()

        # 3️⃣ Update Refund Request
        refund.status = "completed"
        refund.processed_at = datetime.utcnow()

        db.commit()
        db.refresh(invoice)
        db.refresh(refund)
        db.refresh(refund_txn)

        # 4️⃣ Optional Refund Receipt
        try:
            receipt_number = generate_receipt_number()
            receipt = Receipt(
                receipt_number=receipt_number,
                invoice_id=invoice.id,
                transaction_id=refund_txn.id,
                payment_id=original_txn.payment_id,
                amount=-refund.refund_amount,
                qr_code_data=f"Refund:{receipt_number}|Amount:{refund.refund_amount}",
                generated_at=datetime.utcnow(),
            )
            PaymentRepository.save_receipt(db, receipt)
        except Exception as e:
            print("Refund receipt generation failed:", e)

        return {
            "message": "Refund approved successfully",
            "refund_transaction": refund_txn,
            "invoice": invoice,
        }