# app/api/v1/routers/invoices.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine, get_db
from app.schemas.payment_schemas import InvoiceCreate, InvoiceResponse
from app.services.payment_services import PaymentService


router = APIRouter()
# ensure tables created (safe)
# Base.metadata.create_all(bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    try:
        created = PaymentService.create_invoice(
            db=db,
            user_id=invoice.user_id,
            hostel_id=invoice.hostel_id,
            items=[it.dict() for it in invoice.items],
            description=invoice.description,
            due_date=invoice.due_date
        )
        return created
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.query(__import__("app").models.payment_models.Invoice).filter(__import__("app").models.payment_models.Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv

@router.get("/user/{user_id}", response_model=list[InvoiceResponse])
def get_user_invoices(user_id: int, db: Session = Depends(get_db)):
    invoices = db.query(__import__("app").models.payment_models.Invoice).filter(__import__("app").models.payment_models.Invoice.user_id == user_id).order_by(__import__("app").models.payment_models.Invoice.created_at.desc()).all()
    return invoices
