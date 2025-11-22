from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# -------------------- ENUMS --------------------

class ComplaintCategory(str, Enum):
    room_maintenance = "room_maintenance"
    mess_quality = "mess_quality"
    cleanliness = "cleanliness"
    security = "security"
    wifi= "wifi"
    other = "other"


class ComplaintPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class ComplaintStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    escalated = "escalated"
    resolved = "resolved"
    closed = "closed"
    reopened = "reopened"


# -------------------- BASE SCHEMAS --------------------

class ComplaintBase(BaseModel):
    title: str
    description: str
    category: ComplaintCategory
    priority: Optional[ComplaintPriority] = ComplaintPriority.medium
    hostel_name: str
    room_number: Optional[str] = None


class ComplaintCreate(ComplaintBase):
    student_name: str
    student_email: str


class ComplaintUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    status: Optional[ComplaintStatus]
    priority: Optional[ComplaintPriority]
    assigned_to_name: Optional[str]
    assigned_to_email: Optional[str]
    resolution_notes: Optional[str]
    is_escalated: Optional[bool]
    escalation_reason: Optional[str]


class ComplaintAssignment(BaseModel):
    assigned_to_name: str
    assigned_to_email: str


class ComplaintResolution(BaseModel):
    resolution_notes: str
    resources_used: Optional[str] = None
    actual_cost: Optional[float] = None


class ComplaintFeedback(BaseModel):
    student_feedback: str
    student_rating: int = Field(..., ge=1, le=5)


class ComplaintReopen(BaseModel):
    reopen_reason: str


class ComplaintNoteCreate(BaseModel):
    note: str
    user_name: str
    user_email: str
    is_internal: bool = False


class ComplaintFilter(BaseModel):
    student_email: Optional[str] = None
    hostel_id: Optional[int] = None
    hostel_name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to_email: Optional[str] = None
    is_escalated: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    page_size: int = 10


# -------------------- RESPONSE SCHEMAS --------------------

class ComplaintResponse(BaseModel):
    id: int
    title: str
    description: str
    category: ComplaintCategory
    priority: ComplaintPriority
    status: ComplaintStatus
    student_name: str
    student_email: str
    hostel_name: str
    assigned_to_name: Optional[str]
    assigned_to_email: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True  # Replaces from_attributes in Pydantic v2


class ComplaintAttachmentResponse(BaseModel):
    id: int
    file_name: str
    file_type: str
    file_size: int
    uploaded_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class ComplaintNoteResponse(BaseModel):
    id: int
    note: str
    user_name: str
    user_email: str
    is_internal: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ComplaintDetailResponse(ComplaintResponse):
    attachments: List[ComplaintAttachmentResponse] = []
    notes: List[ComplaintNoteResponse] = []


class ComplaintListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    complaints: List[ComplaintResponse]


# -------------------- ANALYTICS / PERFORMANCE --------------------

class SupervisorPerformance(BaseModel):
    supervisor_email: str
    total_complaints: int
    resolved_complaints: int
    average_resolution_time_hours: Optional[float]


class ComplaintAnalytics(BaseModel):
    total_complaints: int
    open_complaints: int
    resolved_complaints: int
    average_resolution_time_hours: Optional[float]
    category_distribution: dict
