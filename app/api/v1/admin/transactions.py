
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
