# app/api/v1/routers/receipts.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, get_db
from app.models.payment_models import Receipt
from app.utils.receipt_generatorss import generate_receipt_pdf

router = APIRouter()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@router.get("/transaction/{transaction_id}")
def get_receipt_by_transaction(transaction_id: int, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.transaction_id == transaction_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return {
        "id": receipt.id,
        "receipt_number": receipt.receipt_number,
        "pdf_path": receipt.pdf_path
    }

@router.get("/{receipt_id}/download")
def download_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    if not receipt.pdf_path or not __import__("os").path.exists(receipt.pdf_path):
        # regenerate
        tx = receipt.transaction
        inv = receipt.invoice
        path = generate_receipt_pdf(receipt, inv, tx)
        receipt.pdf_path = path
        db.commit()
    return FileResponse(receipt.pdf_path, media_type="application/pdf", filename=f"receipt_{receipt.receipt_number}.pdf")
