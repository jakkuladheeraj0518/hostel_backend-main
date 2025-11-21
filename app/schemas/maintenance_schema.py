from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Maintenance Request Schemas
class MaintenanceCreate(BaseModel):
    category: str = Field(..., description="PLUMBING, ELECTRICAL, HVAC, CLEANING, etc.")
    priority: str = Field("MEDIUM", description="LOW, MEDIUM, HIGH, URGENT")
    description: str = Field(..., min_length=10, max_length=1000)
    photo_url: Optional[str] = Field(None, description="Photo evidence URL")
    est_cost: Optional[float] = Field(None, ge=0, description="Estimated cost")
    scheduled_date: Optional[datetime] = Field(None, description="Preferred completion date")

class MaintenanceUpdate(BaseModel):
    status: Optional[str] = Field(None, description="PENDING, IN_PROGRESS, COMPLETED, APPROVED")
    priority: Optional[str] = Field(None, description="LOW, MEDIUM, HIGH, URGENT")
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    est_cost: Optional[float] = Field(None, ge=0)
    actual_cost: Optional[float] = Field(None, ge=0)
    assigned_to_id: Optional[int] = Field(None, description="Staff member ID")
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None

class MaintenanceOut(BaseModel):
    id: int
    hostel_id: int
    created_by_id: int
    category: str
    priority: str
    status: str
    description: str
    photo_url: Optional[str]
    est_cost: Optional[float]
    actual_cost: Optional[float]
    approved: bool
    assigned_to_id: Optional[int]
    scheduled_date: Optional[datetime]
    completed_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

# Complaint Schemas
class ComplaintCreate(BaseModel):
    category: str = Field(..., description="Issue category")
    priority: str = Field("MEDIUM", description="LOW, MEDIUM, HIGH, URGENT")
    description: str = Field(..., min_length=10, max_length=1000)
    photo_url: Optional[str] = Field(None, description="Photo evidence URL")

class ComplaintOut(BaseModel):
    id: int
    hostel_id: int
    student_id: Optional[int]
    category: str
    priority: str
    status: str
    description: str
    photo_url: Optional[str]
    created_at: datetime
    updated_at: datetime

# Maintenance Cost Schemas
class MaintenanceCostCreate(BaseModel):
    maintenance_request_id: int
    category: str = Field(..., description="LABOR, MATERIALS, EQUIPMENT, VENDOR")
    vendor_name: Optional[str] = Field(None, max_length=128)
    description: str = Field(..., min_length=5, max_length=500)
    amount: float = Field(..., gt=0, description="Cost amount")
    invoice_url: Optional[str] = Field(None, description="Invoice document URL")
    payment_method: Optional[str] = Field(None, description="Payment method used")

class MaintenanceCostOut(BaseModel):
    id: int
    maintenance_request_id: int
    hostel_id: int
    category: str
    vendor_name: Optional[str]
    description: str
    amount: float
    invoice_url: Optional[str]
    payment_status: str
    payment_method: Optional[str]
    paid_date: Optional[datetime]
    created_at: datetime

# Maintenance Task Schemas
class MaintenanceTaskCreate(BaseModel):
    maintenance_request_id: int
    assigned_to_id: int
    task_title: str = Field(..., min_length=5, max_length=200)
    task_description: str = Field(..., min_length=10, max_length=1000)
    priority: str = Field("MEDIUM", description="LOW, MEDIUM, HIGH, URGENT")
    estimated_hours: Optional[float] = Field(None, gt=0)
    scheduled_date: Optional[datetime] = None

class MaintenanceTaskUpdate(BaseModel):
    status: Optional[str] = Field(None, description="ASSIGNED, IN_PROGRESS, COMPLETED, VERIFIED")
    actual_hours: Optional[float] = Field(None, gt=0)
    quality_rating: Optional[int] = Field(None, ge=1, le=5, description="Quality rating 1-5")
    completion_notes: Optional[str] = Field(None, max_length=1000)
    verification_notes: Optional[str] = Field(None, max_length=1000)
    started_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None

class MaintenanceTaskOut(BaseModel):
    id: int
    maintenance_request_id: int
    assigned_to_id: int
    task_title: str
    task_description: str
    status: str
    priority: str
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    quality_rating: Optional[int]
    completion_notes: Optional[str]
    verification_notes: Optional[str]
    verified_by_id: Optional[int]
    scheduled_date: Optional[datetime]
    started_date: Optional[datetime]
    completed_date: Optional[datetime]
    verified_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

# Analytics Schemas
class MaintenanceAnalytics(BaseModel):
    total_requests: int
    pending_requests: int
    in_progress_requests: int
    completed_requests: int
    total_cost: float
    avg_completion_time_hours: float
    category_breakdown: dict
    priority_breakdown: dict
    monthly_trends: List[dict]

class MaintenanceBudget(BaseModel):
    hostel_id: int
    category: str
    allocated_budget: float
    spent_amount: float
    remaining_budget: float
    utilization_percentage: float
