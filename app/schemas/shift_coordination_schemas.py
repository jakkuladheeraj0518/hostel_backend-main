from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class ShiftCreate(BaseModel):
    name: str
    start_time: str
    end_time: str
    hostel_id: int

class ShiftScheduleCreate(BaseModel):
    admin_id: int
    shift_id: int
    hostel_id: int
    scheduled_date: date
    notes: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    hostel_id: int
    assigned_to: int
    category: str
    priority: str = "medium"
    due_date: Optional[datetime] = None
    estimated_duration: Optional[int] = None

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    description: Optional[str] = None

class TaskDelegationCreate(BaseModel):
    task_id: int
    from_admin_id: int
    to_admin_id: int
    reason: str

class HandoverCreate(BaseModel):
    from_schedule_id: int
    to_schedule_id: int
    hostel_id: int
    occupancy_status: Optional[str] = None
    pending_checkouts: int = 0
    expected_checkins: int = 0
    urgent_issues: Optional[str] = None
    maintenance_required: Optional[str] = None
    guest_concerns: Optional[str] = None
    pending_tasks: Optional[str] = None
    completed_tasks: Optional[str] = None
    inventory_status: Optional[str] = None
    cash_handover: Optional[float] = None
    keys_status: Optional[str] = None
    notes: Optional[str] = None
    special_instructions: Optional[str] = None

class HandoverItemCreate(BaseModel):
    handover_id: int
    item_type: str
    title: str
    description: Optional[str] = None
    priority: str = "medium"

class CoordinationMeetingCreate(BaseModel):
    hostel_id: int
    coordination_date: date
    meeting_type: str
    participants: str
    agenda: Optional[str] = None
    discussion_points: Optional[str] = None
    decisions_made: Optional[str] = None
    action_items: Optional[str] = None
    next_meeting: Optional[datetime] = None
