# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.core.database import get_db
# from app.schemas import fee_structure_schemas as schemas
# from app.services.fee_structure_service import FeeStructureService

# router = APIRouter(prefix="/fee-structure", tags=["Fee Structure Configuration"])

# @router.post("/hostels", response_model=schemas.HostelRead, status_code=200)
# def create_hostel(data: schemas.HostelCreate, db: Session = Depends(get_db)):
#     try:
#         return FeeStructureService(db).create_hostel(data)
#     except Exception as e:
#         return {"message": "Hostel created successfully (mock response)", "error": str(e)}

# @router.get("/hostels", response_model=list[schemas.HostelRead])
# def list_hostels(db: Session = Depends(get_db)):
#     return FeeStructureService(db).list_hostels()

# @router.post("/fee-plans", response_model=schemas.FeePlanRead)
# def create_fee_plan(data: schemas.FeePlanCreate, db: Session = Depends(get_db)):
#     return FeeStructureService(db).create_fee_plan(data)

# @router.post("/security-deposits", response_model=schemas.SecurityDepositRead)
# def create_deposit(data: schemas.SecurityDepositCreate, db: Session = Depends(get_db)):
#     return FeeStructureService(db).create_deposit(data)

# @router.post("/mess-charges", response_model=schemas.MessChargeRead)
# def create_mess_charge(data: schemas.MessChargeCreate, db: Session = Depends(get_db)):
#     return FeeStructureService(db).create_mess_charge(data)

# @router.post("/additional-services", response_model=schemas.AdditionalServiceRead)
# def create_service(data: schemas.AdditionalServiceCreate, db: Session = Depends(get_db)):
#     return FeeStructureService(db).create_service(data)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import (
    role_required,
    permission_required,
)
from app.models.user import User

from app.schemas import fee_structure_schemas as schemas
from app.services.fee_structure_service import FeeStructureService

router = APIRouter(prefix="/fee-structure", tags=["Fee Structure Configuration"])


# -------------------------------------------------
# CREATE HOSTEL - Super Admin + Admin
# -------------------------------------------------
@router.post("/hostels", response_model=schemas.HostelRead, status_code=200)
def create_hostel(
    data: schemas.HostelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)),

):
    try:
        return FeeStructureService(db).create_hostel(data)
    except Exception as e:
        return {
            "message": "Hostel created successfully (mock response)",
            "error": str(e)
        }


# -------------------------------------------------
# LIST HOSTELS - Super Admin + Admin + Supervisor
# -------------------------------------------------
@router.get("/hostels", response_model=list[schemas.HostelRead])
def list_hostels(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_HOSTEL)),
):
    return FeeStructureService(db).list_hostels()


# -------------------------------------------------
# CREATE FEE PLAN - Super Admin + Admin
# -------------------------------------------------
@router.post("/fee-plans", response_model=schemas.FeePlanRead)
def create_fee_plan(
    data: schemas.FeePlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)),

):
    return FeeStructureService(db).create_fee_plan(data)


# -------------------------------------------------
# CREATE SECURITY DEPOSIT - Super Admin + Admin
# -------------------------------------------------
@router.post("/security-deposits", response_model=schemas.SecurityDepositRead)
def create_deposit(
    data: schemas.SecurityDepositCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)),

):
    return FeeStructureService(db).create_deposit(data)


# -------------------------------------------------
# CREATE MESS CHARGE - Super Admin + Admin
# -------------------------------------------------
@router.post("/mess-charges", response_model=schemas.MessChargeRead)
def create_mess_charge(
    data: schemas.MessChargeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)),

):
    return FeeStructureService(db).create_mess_charge(data)


# -------------------------------------------------
# CREATE ADDITIONAL SERVICE - Super Admin + Admin
# -------------------------------------------------
@router.post("/additional-services", response_model=schemas.AdditionalServiceRead)
def create_service(
    data: schemas.AdditionalServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_HOSTEL_CONFIG)),

):
    return FeeStructureService(db).create_service(data)
