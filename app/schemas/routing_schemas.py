from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

from app.models.routing_models import (
    UserRole,
    NotificationCategory,
    NotificationPriority,
    NotificationStatus,
    RoutingStrategy
)


# ---------- USER ----------

class UserCreate(BaseModel):
    name: str
    username: str 
    email: str
    phone_number: str
    role: UserRole
    hostel_id: Optional[int] = None
    supervisor_id: Optional[int] = None
    admin_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    hostel_id: Optional[int]
    is_active: bool

    class Config:
        from_attributes = True


# ---------- ROUTING RULE ----------

class RoutingRuleCreate(BaseModel):
    rule_name: str
    notification_category: NotificationCategory
    source_role: UserRole
    target_role: UserRole
    priority_threshold: NotificationPriority
    routing_strategy: RoutingStrategy

    route_to_supervisor: bool = False
    route_to_admin: bool = False
    route_to_super_admin: bool = False
    cc_admin: bool = False
    cc_supervisor: bool = False

    enable_escalation: bool = False
    escalation_time_minutes: Optional[int] = None
    escalation_target_role: Optional[UserRole] = None

    hostel_specific: bool = True
    working_hours_only: bool = False
    priority_order: int = 0


class RoutingRuleResponse(BaseModel):
    id: int
    rule_name: str
    notification_category: NotificationCategory
    source_role: UserRole
    target_role: UserRole
    routing_strategy: RoutingStrategy
    enable_escalation: bool
    escalation_time_minutes: Optional[int]
    is_active: bool

    class Config:
        from_attributes = True


# ---------- NOTIFICATION ----------

class NotificationCreate(BaseModel):
    source_user_id: int
    source_role: UserRole
    hostel_id: Optional[int]
    category: NotificationCategory
    priority: NotificationPriority
    title: str
    message: str
    extra_metadata: Optional[Dict] = {}
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None


class NotificationResponse(BaseModel):
    id: int
    source_user_id: int
    source_role: UserRole
    category: NotificationCategory
    priority: NotificationPriority
    title: str
    message: str
    status: NotificationStatus
    routing_strategy: RoutingStrategy
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- ESCALATION ----------

class EscalateNotificationRequest(BaseModel):
    notification_id: int
    reason: str
    escalate_to_user_id: Optional[int] = None
    escalate_to_role: Optional[UserRole] = None


# ---------- SUPERVISOR ASSIGNMENT ----------

class SupervisorAssignmentCreate(BaseModel):
    admin_id: int
    supervisor_id: int
    hostel_id: int
    responsibilities: List[str]
    can_escalate: bool = True
    max_priority_level: NotificationPriority
    working_hours_start: Optional[str] = None
    working_hours_end: Optional[str] = None
    working_days: Optional[List[int]] = None
