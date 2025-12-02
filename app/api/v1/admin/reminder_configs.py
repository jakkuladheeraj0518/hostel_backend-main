# # app/api/v1/routers/configs.py

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.core.database import SessionLocal,get_db
# from app.schemas.payment_schemas import ReminderConfigCreate, ReminderConfigResponse
# from app.models.payment_models import ReminderConfiguration
# import json

# router = APIRouter(prefix="/reminders/config", tags=["Reminder Config"])


# # def get_db():
# #     db = SessionLocal()
# #     try:
# #         yield db
# #     finally:
# #         db.close()


# # -----------------------------------------------------------
# # Create or update config
# # -----------------------------------------------------------

# @router.post("/", response_model=ReminderConfigResponse)
# def save_config(config: ReminderConfigCreate, db: Session = Depends(get_db)):

#     existing = db.query(ReminderConfiguration).filter(
#         ReminderConfiguration.hostel_id == config.hostel_id
#     ).first()

#     data = config.dict()
#     if data.get("escalation_emails"):
#         data["escalation_emails"] = json.dumps(data["escalation_emails"])

#     if data.get("escalation_cc"):
#         data["escalation_cc"] = json.dumps(data["escalation_cc"])

#     if existing:
#         for key, val in data.items():
#             setattr(existing, key, val)
#         db.commit()
#         db.refresh(existing)
#         return existing

#     new_config = ReminderConfiguration(**data)
#     db.add(new_config)
#     db.commit()
#     db.refresh(new_config)
#     return new_config


# # -----------------------------------------------------------
# # Fetch config
# # -----------------------------------------------------------

# @router.get("/{hostel_id}", response_model=ReminderConfigResponse)
# def get_config(hostel_id: int, db: Session = Depends(get_db)):
#     config = db.query(ReminderConfiguration).filter(
#         ReminderConfiguration.hostel_id == hostel_id
#     ).first()

#     if not config:
#         raise HTTPException(404, "Config not found")

#     return config
# app/api/v1/routers/refunds.py

# app/api/v1/routers/configs.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from app.core.database import get_db
from app.schemas.payment_schemas import ReminderConfigCreate, ReminderConfigResponse
from app.models.payment_models import ReminderConfiguration

# RBAC imports
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required


router = APIRouter(
    prefix="/reminders/config",
    tags=["Reminder Config"]
)


# -----------------------------------------------------------
# Create or Update Reminder Config
# -----------------------------------------------------------
@router.post(
    "/",
    response_model=ReminderConfigResponse,
    dependencies=[
        Depends(role_required([Role.SUPERADMIN, Role.ADMIN])),
        Depends(permission_required(Permission.MANAGE_REMINDERS))
    ]
)
def save_config(config: ReminderConfigCreate, db: Session = Depends(get_db)):

    existing = db.query(ReminderConfiguration).filter(
        ReminderConfiguration.hostel_id == config.hostel_id
    ).first()

    data = config.dict()

    if data.get("escalation_emails"):
        data["escalation_emails"] = json.dumps(data["escalation_emails"])

    if data.get("escalation_cc"):
        data["escalation_cc"] = json.dumps(data["escalation_cc"])

    if existing:
        for key, val in data.items():
            setattr(existing, key, val)
        db.commit()
        db.refresh(existing)
        return existing

    new_config = ReminderConfiguration(**data)
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    return new_config


# -----------------------------------------------------------
# Fetch Reminder Config
# -----------------------------------------------------------
@router.get(
    "/{hostel_id}",
    response_model=ReminderConfigResponse,
    dependencies=[
        Depends(role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])),
        Depends(permission_required(Permission.READ_REMINDERS))
    ]
)
def get_config(hostel_id: int, db: Session = Depends(get_db)):
    config = db.query(ReminderConfiguration).filter(
        ReminderConfiguration.hostel_id == hostel_id
    ).first()

    if not config:
        raise HTTPException(404, "Config not found")

    return config
