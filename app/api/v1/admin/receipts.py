# # app/api/v1/routers/receipts.py
# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session
# from app.core.database import SessionLocal, get_db
# from app.models.payment_models import Receipt
# from app.utils.receipt_generatorss import generate_receipt_pdf

# router = APIRouter()

# # def get_db():
# #     db = SessionLocal()
# #     try:
# #         yield db
# #     finally:
# #         db.close()

# @router.get("/transaction/{transaction_id}")
# def get_receipt_by_transaction(transaction_id: int, db: Session = Depends(get_db)):
#     receipt = db.query(Receipt).filter(Receipt.transaction_id == transaction_id).first()
#     if not receipt:
#         raise HTTPException(status_code=404, detail="Receipt not found")
#     return {
#         "id": receipt.id,
#         "receipt_number": receipt.receipt_number,
#         "pdf_path": receipt.pdf_path
#     }

# @router.get("/{receipt_id}/download")
# def download_receipt(receipt_id: int, db: Session = Depends(get_db)):
#     receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
#     if not receipt:
#         raise HTTPException(status_code=404, detail="Receipt not found")
#     if not receipt.pdf_path or not __import__("os").path.exists(receipt.pdf_path):
#         # regenerate
#         tx = receipt.transaction
#         inv = receipt.invoice
#         path = generate_receipt_pdf(receipt, inv, tx)
#         receipt.pdf_path = path
#         db.commit()
#     return FileResponse(receipt.pdf_path, media_type="application/pdf", filename=f"receipt_{receipt.receipt_number}.pdf")
# app/api/v1/routers/receipts.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.models.payment_models import Receipt
from app.utils.receipt_generatorss import generate_receipt_pdf

# RBAC imports
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import (
    role_required,
    permission_required,
)
from app.models.user import User

router = APIRouter(prefix="/receipts", tags=["Receipts"])


# -------------------------------------------------------------
# 📌 GET RECEIPT DETAILS BY TRANSACTION ID  
# Roles: Admin, Supervisor, SuperAdmin, Student (own only)
# -------------------------------------------------------------
@router.get("/transaction/{transaction_id}")
def get_receipt_by_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            Role.SUPERADMIN,
            Role.ADMIN,
            Role.SUPERVISOR,
            Role.STUDENT
        ])
    ),
    _: None = Depends(permission_required(Permission.VIEW_PAYMENTS)),
):
    receipt = db.query(Receipt).filter(Receipt.transaction_id == transaction_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    tx = receipt.transaction

    # Students can only access their own transactions
    # Transaction doesn't store user_id directly — use the related invoice's user_id
    if current_user.role == Role.STUDENT and (not tx.invoice or tx.invoice.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "id": receipt.id,
        "receipt_number": receipt.receipt_number,
        "pdf_path": receipt.pdf_path
    }


# -------------------------------------------------------------
# 📌 DOWNLOAD RECEIPT PDF  
# Roles: Admin, Supervisor, SuperAdmin, Student (own only)
# -------------------------------------------------------------
@router.get("/{receipt_id}/download")
def download_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            Role.SUPERADMIN,
            Role.ADMIN,
            Role.SUPERVISOR,
            Role.STUDENT
        ])
    ),
    _: None = Depends(permission_required(Permission.VIEW_PAYMENTS)),
):
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    tx = receipt.transaction

    # Students can ONLY download their own receipts
    # Transaction doesn't store user_id directly — use the related invoice's user_id
    if current_user.role == Role.STUDENT and (not tx.invoice or tx.invoice.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Regenerate PDF if missing
    if not receipt.pdf_path or not os.path.exists(receipt.pdf_path):
        inv = receipt.invoice
        path = generate_receipt_pdf(receipt, inv, tx)
        receipt.pdf_path = path
        db.commit()

    return FileResponse(
        receipt.pdf_path,
        media_type="application/pdf",
        filename=f"receipt_{receipt.receipt_number}.pdf"
    )
