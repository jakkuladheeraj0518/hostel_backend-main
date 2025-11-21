from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class PreventiveMaintenanceScheduleCreate(BaseModel):
    hostel_id: int
    equipment_type: str
    maintenance_type: str
    frequency_days: int
    next_due: date

class PreventiveMaintenanceScheduleOut(BaseModel):
    id: int
    hostel_id: int
    equipment_type: str
    maintenance_type: str
    frequency_days: int
    last_maintenance: Optional[date]
    next_due: date
    is_active: bool
    created_at: datetime

class PreventiveMaintenanceTaskCreate(BaseModel):
    schedule_id: int
    assigned_to_id: Optional[int] = None
    scheduled_date: date

class PreventiveMaintenanceTaskUpdate(BaseModel):
    status: str
    completed_date: Optional[date] = None
    notes: Optional[str] = None
    cost: Optional[int] = None