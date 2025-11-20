# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.schemas.payment_schemas import PaymentCreate, RazorpayOrderResponse
# from app.services.payment_services import PaymentService
# from app.database import get_db
# from app.config import settings

# router = APIRouter(prefix="/payments", tags=["Payments"])

# @router.post("/razorpay/create-order", response_model=RazorpayOrderResponse)
# def create_order(payment: PaymentCreate, db: Session = Depends(get_db)):
#     record = PaymentService.create_razorpay_order(payment, db)
#     return RazorpayOrderResponse(
#         order_id=record.order_id,
#         gateway_order_id=record.gateway_order_id,
#         amount=record.amount,
#         currency=record.currency,
#         key_id=settings.RAZORPAY_KEY_ID,
#         payment_record_id=record.id
#     )
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.payment_schemas import CreateOrderRequest
from app.services.payment_services import RazorpayService

router = APIRouter(prefix="/payments/razorpay", tags=["Razorpay Payments"])

@router.post("/create-order")
def create_razorpay_order(request: CreateOrderRequest):
    db: Session = SessionLocal()
    try:
        result = RazorpayService.create_order(db=db, request=request)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment creation failed: {str(e)}")
    finally:
        db.close()
