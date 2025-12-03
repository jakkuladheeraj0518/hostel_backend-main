

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import traceback

from app.core.database import get_db
from app.schemas.payment_schemas import RefundCreate, RefundApproval
from app.services.payment_services import PaymentService
from app.models.payment_models import RefundRequest, Transaction

# RBAC
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import (
    role_required,
    permission_required,
)
from app.models.user import User


router = APIRouter(prefix="/refunds", tags=["Refunds"])


# -------------------------------------------------------------
# 📌 REQUEST REFUND  
# Roles: Admin, Supervisor, SuperAdmin, Student (ONLY own transaction)
# -------------------------------------------------------------
@router.post("/request")
def request_refund(
    refund: RefundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            Role.SUPERADMIN,
            Role.ADMIN,
            Role.SUPERVISOR,
            Role.STUDENT
        ])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_PAYMENTS)),
):
    # Validate transaction belongs to the student (if student)
    tx = db.query(Transaction).filter(Transaction.id == refund.transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if current_user.role == Role.STUDENT and tx.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        return PaymentService.request_refund(
            db=db,
            transaction_id=refund.transaction_id,
            refund_amount=refund.refund_amount,
            reason=refund.reason,
            requested_by=refund.requested_by
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------
# 📌 APPROVE OR REJECT REFUND  
# Roles: Admin + SuperAdmin ONLY  
# -------------------------------------------------------------
@router.post("/{refund_id}/approve")
def approve_refund(
    refund_id: int,
    approval: RefundApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_PAYMENTS)),
):
    refund = db.query(RefundRequest).filter(RefundRequest.id == refund_id).first()
    if not refund:
        raise HTTPException(status_code=404, detail="Refund request not found")

    # Cannot reprocess
    if refund.status not in ["initiated", "processing"]:
        raise HTTPException(status_code=400, detail=f"Refund already {refund.status}")

    try:
        if approval.approve:
            result = PaymentService.approve_refund(
                db=db,
                refund_id=refund_id,
                approved_by=approval.approved_by
            )

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
