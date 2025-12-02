# # app/api/v1/routers/invoices.py
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from app.core.database import SessionLocal, Base, engine, get_db
# from app.schemas.payment_schemas import InvoiceCreate, InvoiceResponse
# from app.services.payment_services import PaymentService


# router = APIRouter()

# @router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
# def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
#     try:
#         created = PaymentService.create_invoice(
#             db=db,
#             user_id=invoice.user_id,
#             hostel_id=invoice.hostel_id,
#             items=[it.dict() for it in invoice.items],
#             description=invoice.description,
#             due_date=invoice.due_date
#         )
#         return created
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/{invoice_id}", response_model=InvoiceResponse)
# def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
#     inv = db.query(__import__("app").models.payment_models.Invoice).filter(__import__("app").models.payment_models.Invoice.id == invoice_id).first()
#     if not inv:
#         raise HTTPException(status_code=404, detail="Invoice not found")
#     return inv

# @router.get("/user/{user_id}", response_model=list[InvoiceResponse])
# def get_user_invoices(user_id: int, db: Session = Depends(get_db)):
#     invoices = db.query(__import__("app").models.payment_models.Invoice).filter(__import__("app").models.payment_models.Invoice.user_id == user_id).order_by(__import__("app").models.payment_models.Invoice.created_at.desc()).all()
#     return invoices
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.payment_schemas import InvoiceCreate, InvoiceResponse
from app.services.payment_services import PaymentService

from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import (
    role_required,
    permission_required,
)
from app.models.user import User
from app.models.payment_models import Invoice


router = APIRouter(prefix="/invoices", tags=["Invoices"])


# -------------------------------------------------
# CREATE INVOICE - ONLY ROLE CHECK (NO PERMISSION)
# -------------------------------------------------
@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN,Role.STUDENT])
    ),
    
):
    try:
        return PaymentService.create_invoice(
            db=db,
            user_id=invoice.user_id,
            hostel_id=invoice.hostel_id,
            items=[it.dict() for it in invoice.items],
            description=invoice.description,
            due_date=invoice.due_date,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------
# GET INVOICE BY ID - Includes permissions
# -------------------------------------------------
@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            Role.SUPERADMIN,
            Role.ADMIN,
            Role.SUPERVISOR,
            Role.STUDENT,
        ])
    ),
    _: None = Depends(permission_required(Permission.VIEW_INVOICES)),
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Student can access only their own invoice
    if current_user.role == Role.STUDENT and inv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return inv


# -------------------------------------------------
# GET USER INVOICES - Includes permissions
# -------------------------------------------------
@router.get("/user/{user_id}", response_model=list[InvoiceResponse])
def get_user_invoices(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            Role.SUPERADMIN,
            Role.ADMIN,
            Role.SUPERVISOR,
            Role.STUDENT,
        ])
    ),
    _: None = Depends(permission_required(Permission.VIEW_INVOICES)),
):
    # Students can only fetch their own invoices
    if current_user.role == Role.STUDENT and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return (
        db.query(Invoice)
        .filter(Invoice.user_id == user_id)
        .order_by(Invoice.created_at.desc())
        .all()
    )
