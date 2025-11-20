from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class FeeFrequency(str, Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    annual = "annual"

# -------- Hostel --------
class HostelBase(BaseModel):
    hostel_name: str
    full_address: Optional[str] = None
    capacity: Optional[int] = 0

class HostelCreate(HostelBase):
    pass

class HostelRead(HostelBase):
    id: int
    class Config:
        orm_mode = True

# -------- Fee Plan --------
class FeePlanBase(BaseModel):
    hostel_id: int
    plan_name: str
    frequency: FeeFrequency
    amount: float
    room_type: Optional[str] = None
    description: Optional[str] = None

class FeePlanCreate(FeePlanBase):
    pass

class FeePlanRead(FeePlanBase):
    id: int
    class Config:
        orm_mode = True

# -------- Security Deposit --------
class SecurityDepositBase(BaseModel):
    hostel_id: int
    name: str
    amount: float
    refundable: Optional[bool] = True

class SecurityDepositCreate(SecurityDepositBase):
    pass

class SecurityDepositRead(SecurityDepositBase):
    id: int
    class Config:
        orm_mode = True

# -------- Mess Charge --------
class MessChargeBase(BaseModel):
    hostel_id: int
    meal_type: str
    frequency: FeeFrequency
    amount: float
    is_mandatory: Optional[bool] = True

class MessChargeCreate(MessChargeBase):
    pass

class MessChargeRead(MessChargeBase):
    id: int
    class Config:
        orm_mode = True

# -------- Additional Service --------
class AdditionalServiceBase(BaseModel):
    hostel_id: int
    service_name: str
    amount: float
    frequency: FeeFrequency
    description: Optional[str] = None

class AdditionalServiceCreate(AdditionalServiceBase):
    pass

class AdditionalServiceRead(AdditionalServiceBase):
    id: int
    class Config:
        orm_mode = True
