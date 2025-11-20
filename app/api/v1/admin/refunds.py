# app/api/v1/routers/refunds.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, get_db
from app.schemas.payment_schemas import RefundCreate, RefundApproval
from app.services.payment_services import PaymentService
from app.models.payment_models import RefundRequest, Invoice, Transaction, PaymentStatus
from app.models.payment_models import TransactionType
from datetime import datetime
import uuid
import traceback


router = APIRouter()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@router.post("/request")
def request_refund(refund: RefundCreate, db: Session = Depends(get_db)):
    try:
        req = PaymentService.request_refund(
            db=db,
            transaction_id=refund.transaction_id,
            refund_amount=refund.refund_amount,
            reason=refund.reason,
            requested_by=refund.requested_by
        )
        return req
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{refund_id}/approve")
def approve_refund(refund_id: int, approval: RefundApproval, db: Session = Depends(get_db)):
    """
    Approves or rejects a refund request.
    Creates a refund transaction and updates invoice if approved.
    """
    # 🔍 1. Fetch refund record
    refund = db.query(RefundRequest).filter(RefundRequest.id == refund_id).first()
    if not refund:
        raise HTTPException(status_code=404, detail="Refund request not found")

    # 🚫 Already processed
    if refund.status not in ["initiated", "processing"]:
        raise HTTPException(status_code=400, detail=f"Refund already {refund.status}")

    try:
        if approval.approve:
            # 🧾 Generate transaction ID safely
            txn_id = (
                PaymentService.generate_transaction_id()
                if hasattr(PaymentService, "generate_transaction_id")
                else f"TXN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
            )

            # 💸 Create refund transaction
            txn = Transaction(
                transaction_id=txn_id,
                invoice_id=refund.invoice_id,
                transaction_type=TransactionType.REFUND.value,
                amount=-abs(refund.refund_amount),
                payment_method="refund",
                notes=f"Refund processed: {refund.reason}",
                status="success",
                processed_by=approval.approved_by,
                created_at=datetime.utcnow()
            )
            db.add(txn)

            # 🧾 Fetch invoice and update totals
            invoice = db.query(Invoice).filter(Invoice.id == refund.invoice_id).first()
            if not invoice:
                raise HTTPException(status_code=404, detail="Invoice linked to refund not found")

            invoice.paid_amount = max(invoice.paid_amount - refund.refund_amount, 0)
            invoice.due_amount += refund.refund_amount

            if invoice.paid_amount <= 0:
                invoice.status = PaymentStatus.PENDING.value
            elif invoice.due_amount > 0:
                invoice.status = PaymentStatus.PENDING.value
            else:
                invoice.status = PaymentStatus.SUCCESS.value

            # ✅ Update refund record
            refund.status = "completed"
            refund.approved_by = approval.approved_by
            refund.processed_at = datetime.utcnow()
            refund.completed_at = datetime.utcnow()

            message = "Refund approved successfully"

        else:
            # ❌ Refund rejected
            refund.status = "rejected"
            refund.rejection_reason = approval.rejection_reason
            refund.approved_by = approval.approved_by
            refund.processed_at = datetime.utcnow()
            message = "Refund request rejected"

        # 💾 Commit all changes
        db.commit()
        db.refresh(refund)

        return {
            "success": True,
            "message": message,
            "refund": {
                "refund_id": refund.refund_id,
                "status": refund.status,
                "refund_amount": refund.refund_amount,
                "approved_by": refund.approved_by,
                "processed_at": refund.processed_at,
                "completed_at": refund.completed_at,
            },
        }

    except Exception as e:
        db.rollback()
        print("❌ Refund approval error:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Refund approval failed: {str(e)}")

# from app.services.payment_services import RefundService
# from app.schemas.payment_schemas import RefundApproval
# @router.post("/{refund_id}/approve")
# def approve_refund(refund_id: int, approval: RefundApproval, db: Session = Depends(get_db)):
#     """Approves or rejects a refund request"""
#     try:
#         service = RefundService(db)
#         if approval.approve:
#             result = service.approve_refund(refund_id, approval)
#         else:
#             result = service.reject_refund(refund_id, approval)
#         return result
#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))
#     except Exception as e:
#         print("❌ Refund approval error:", e)
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Refund processing failed: {str(e)}")
