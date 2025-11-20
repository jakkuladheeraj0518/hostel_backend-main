# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models.payment_models import Payment, Transaction, TransactionType, PaymentStatus
# from app.schemas.payment_schemas import TransactionResponse, PartialPaymentRequest, RefundRequest
# from app.services.payment_services import generate_reference_id
# from app.utils.pdf_generator import generate_pdf_receipt

# router = APIRouter()


# # ✅ Full Payment Processing
# @router.post("/{payment_id}/process", response_model=TransactionResponse)
# def process_full_payment(payment_id: int, db: Session = Depends(get_db)):
#     payment = db.query(Payment).filter(Payment.id == payment_id).first()
#     if not payment:
#         raise HTTPException(status_code=404, detail="Payment not found")

#     if payment.status == PaymentStatus.COMPLETED:
#         raise HTTPException(status_code=400, detail="Payment already completed")

#     remaining = payment.amount - payment.paid_amount
#     transaction = Transaction(
#         payment_id=payment.id,
#         amount=remaining,
#         transaction_type=TransactionType.PAYMENT,
#         reference_id=generate_reference_id(),
#     )

#     payment.paid_amount = payment.amount
#     payment.status = PaymentStatus.COMPLETED

#     db.add(transaction)
#     db.commit()
#     db.refresh(transaction)
#     return transaction


# # ✅ Partial Payment Processing
# @router.post("/{payment_id}/partial", response_model=TransactionResponse)
# def process_partial_payment(payment_id: int, request: PartialPaymentRequest, db: Session = Depends(get_db)):
#     payment = db.query(Payment).filter(Payment.id == payment_id).first()
#     if not payment:
#         raise HTTPException(status_code=404, detail="Payment not found")

#     if payment.status == PaymentStatus.COMPLETED:
#         raise HTTPException(status_code=400, detail="Payment already completed")

#     remaining = payment.amount - payment.paid_amount
#     if request.amount > remaining:
#         raise HTTPException(status_code=400, detail=f"Amount exceeds remaining balance of ${remaining:.2f}")

#     transaction = Transaction(
#         payment_id=payment.id,
#         amount=request.amount,
#         transaction_type=TransactionType.PARTIAL_PAYMENT,
#         reference_id=generate_reference_id(),
#     )

#     payment.paid_amount += request.amount
#     payment.status = PaymentStatus.COMPLETED if payment.paid_amount >= payment.amount else PaymentStatus.PARTIAL

#     db.add(transaction)
#     db.commit()
#     db.refresh(transaction)
#     return transaction


# # ✅ Refund Payment
# @router.post("/{payment_id}/refund", response_model=TransactionResponse)
# def refund_payment(payment_id: int, request: RefundRequest, db: Session = Depends(get_db)):
#     payment = db.query(Payment).filter(Payment.id == payment_id).first()
#     if not payment:
#         raise HTTPException(status_code=404, detail="Payment not found")

#     if payment.paid_amount == 0:
#         raise HTTPException(status_code=400, detail="No amount paid to refund")

#     refund_amount = request.amount if request.amount else payment.paid_amount
#     if refund_amount > payment.paid_amount:
#         raise HTTPException(status_code=400, detail=f"Refund amount exceeds paid amount of ${payment.paid_amount:.2f}")

#     transaction = Transaction(
#         payment_id=payment.id,
#         amount=refund_amount,
#         transaction_type=TransactionType.REFUND,
#         reference_id=generate_reference_id(),
#     )

#     payment.paid_amount -= refund_amount
#     payment.status = PaymentStatus.REFUNDED if payment.paid_amount == 0 else PaymentStatus.PARTIAL

#     db.add(transaction)
#     db.commit()
#     db.refresh(transaction)
#     return transaction


# # ✅ Download Receipt (PDF)
# @router.get("/{payment_id}/receipt/{transaction_id}")
# def download_receipt(payment_id: int, transaction_id: int, db: Session = Depends(get_db)):
#     payment = db.query(Payment).filter(Payment.id == payment_id).first()
#     if not payment:
#         raise HTTPException(status_code=404, detail="Payment not found")

#     transaction = db.query(Transaction).filter(
#         Transaction.id == transaction_id,
#         Transaction.payment_id == payment_id
#     ).first()
#     if not transaction:
#         raise HTTPException(status_code=404, detail="Transaction not found")

#     pdf_buffer = generate_pdf_receipt(payment, transaction)

#     return StreamingResponse(
#         pdf_buffer,
#         media_type="application/pdf",
#         headers={
#             "Content-Disposition": f"attachment; filename=receipt_{transaction.reference_id}.pdf"
#         },
#     )


# # ✅ Get all transactions for a payment
# @router.get("/{payment_id}/transactions", response_model=list[TransactionResponse])
# def get_payment_transactions(payment_id: int, db: Session = Depends(get_db)):
#     payment = db.query(Payment).filter(Payment.id == payment_id).first()
#     if not payment:
#         raise HTTPException(status_code=404, detail="Payment not found")
#     return payment.transactions
# app/api/v1/routers/transactions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal,get_db
from app.schemas.payment_schemas import PaymentCreate, TransactionResponse
from app.services.payment_services import PaymentService

router = APIRouter()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@router.post("/process", response_model=TransactionResponse)
def process_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    try:
        txn = PaymentService.process_payment(
            db=db,
            invoice_id=payment.invoice_id,
            amount=payment.amount,
            payment_method=payment.payment_method,
            payment_gateway=payment.payment_gateway,
            gateway_transaction_id=payment.gateway_transaction_id,
            notes=payment.notes
        )
        return txn
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(__import__("app").models.payment_models.Transaction).filter(__import__("app").models.payment_models.Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx
