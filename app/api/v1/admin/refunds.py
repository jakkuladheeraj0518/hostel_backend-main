# app/api/v1/routers/refunds.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.payment_schemas import RefundCreate, RefundApproval
# FIXED import: use singular module name (the file that contains the working PaymentService)
from app.services.payment_services import PaymentService
from app.models.payment_models import RefundRequest, Invoice, Transaction, PaymentStatus
from app.models.payment_models import TransactionType
from datetime import datetime
import uuid
import traceback

router = APIRouter()


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
    Delegates to PaymentService.approve_refund for approve flow so payment_id linking,
    invoice updates and receipt generation are handled centrally.
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
            # Delegate approve logic to PaymentService which will:
            # - validate original transaction/payment
            # - create refund transaction with payment_id
            # - update invoice and refund request
            # - create refund receipt
            result = PaymentService.approve_refund(db=db, refund_id=refund_id, approved_by=approval.approved_by)

            return {
                "success": True,
                "message": "Refund approved successfully",
                "refund": {
                    "refund_id": refund.refund_id,
                    "status": refund.status,
                    "refund_amount": refund.refund_amount,
                    "approved_by": refund.approved_by,
                    "processed_at": refund.processed_at,
                    "completed_at": refund.completed_at,
                },
                "detail": result
            }
        else:
            # Delegate rejection handling: keep inline (simple)
            refund.status = "rejected"
            refund.rejection_reason = approval.rejection_reason
            refund.approved_by = approval.approved_by
            refund.processed_at = datetime.utcnow()
            refund.completed_at = datetime.utcnow()

            db.commit()
            db.refresh(refund)

            return {
                "success": True,
                "message": "Refund request rejected",
                "refund": {
                    "refund_id": refund.refund_id,
                    "status": refund.status,
                    "refund_amount": refund.refund_amount,
                    "approved_by": refund.approved_by,
                    "processed_at": refund.processed_at,
                    "completed_at": refund.completed_at,
                },
            }

    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Refund approval failed: {str(e)}")
