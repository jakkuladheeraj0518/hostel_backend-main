# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from app.core.database import get_db
# from app.schemas.payment_schemas import CreateOrderRequest
# from app.services.payment_services import RazorpayService
# from app.core.security import get_current_user
# from app.models.user import User

# router = APIRouter(prefix="/payments/razorpay", tags=["Razorpay Payments"])


# @router.post("/create-order")
# def create_razorpay_order(
#     request: CreateOrderRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)    # 🔥 FIXED
# ):
#     try:
#         return RazorpayService.create_order(
#             db=db,
#             request=request,
#             current_user=current_user                  # 🔥 passes real user
#         )
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Payment creation failed: {str(e)}")
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.payment_schemas import CreateOrderRequest
from app.services.payment_services import RazorpayService

from app.models.user import User
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required

router = APIRouter(prefix="/payments/razorpay", tags=["Razorpay Payments"])


@router.post("/create-order")
def create_razorpay_order(
    request: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.STUDENT])
    ),
    _: None = Depends(permission_required(Permission.VIEW_PAYMENTS)),
):
    try:
        return RazorpayService.create_order(
            db=db,
            request=request,
            current_user=current_user,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Payment creation failed: {str(e)}",
        )
