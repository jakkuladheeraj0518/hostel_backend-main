from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum, JSON, Float, ForeignKey
from datetime import datetime
import enum
from app.config import Base
from sqlalchemy.orm import relationship


# ---------------- ENUMS ----------------

class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    hostel_admin = "hostel_admin"
    hostel_supervisor = "hostel_supervisor"
    student = "student"
    visitor = "visitor"

class NotificationCategory(str, enum.Enum):
    complaint = "complaint"
    maintenance = "maintenance"
    attendance = "attendance"
    payment = "payment"
    booking = "booking"
    announcement = "announcement"
    emergency = "emergency"
    leave_request = "leave_request"
    mess_menu = "mess_menu"
    room_allocation = "room_allocation"
    security = "security"
    general = "general"


class NotificationPriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"
    critical = "critical"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    routed = "routed"
    delivered = "delivered"
    read = "read"
    escalated = "escalated"
    acknowledged = "acknowledged"
    resolved = "resolved"
    failed = "failed"


class EscalationLevel(str, enum.Enum):
    level_0 = "level_0"
    level_1 = "level_1"
    level_2 = "level_2"
    level_3 = "level_3"


class RoutingStrategy(str, enum.Enum):
    direct = "direct"
    hierarchical = "hierarchical"
    broadcast = "broadcast"
    round_robin = "round_robin"


# ---------------- MODELS ----------------


# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String)
#     email = Column(String, unique=True, index=True)
#     phone = Column(String)
#     role = Column(SQLEnum(UserRole))
#     hostel_id = Column(Integer, nullable=True, index=True)
#     supervisor_id = Column(Integer, nullable=True)
#     admin_id = Column(Integer, nullable=True)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=datetime.utcnow)


class RoutingRule(Base):
    __tablename__ = "routing_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String, unique=True, index=True)
    notification_category = Column(SQLEnum(NotificationCategory))
    source_role = Column(SQLEnum(UserRole))
    target_role = Column(SQLEnum(UserRole))
    priority_threshold = Column(SQLEnum(NotificationPriority))
    routing_strategy = Column(SQLEnum(RoutingStrategy))

    route_to_supervisor = Column(Boolean, default=False)
    route_to_admin = Column(Boolean, default=False)
    route_to_super_admin = Column(Boolean, default=False)
    cc_admin = Column(Boolean, default=False)
    cc_supervisor = Column(Boolean, default=False)

    enable_escalation = Column(Boolean, default=False)
    escalation_time_minutes = Column(Integer, nullable=True)
    escalation_target_role = Column(SQLEnum(UserRole), nullable=True)

    hostel_specific = Column(Boolean, default=True)
    working_hours_only = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True)
    priority_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    source_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    source_role = Column(SQLEnum(UserRole))
    hostel_id = Column(Integer, nullable=True, index=True)

    category = Column(SQLEnum(NotificationCategory))
    priority = Column(SQLEnum(NotificationPriority))
    title = Column(String)
    message = Column(Text)
    extra_metadata = Column(JSON, nullable=True)

    reference_type = Column(String, nullable=True)
    reference_id = Column(Integer, nullable=True)

    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.pending)

    routing_rule_id = Column(Integer, nullable=True)
    routing_strategy = Column(SQLEnum(RoutingStrategy))

    created_at = Column(DateTime, default=datetime.utcnow)
    routed_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    




class NotificationRecipient(Base):
    __tablename__ = "notification_recipients"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, index=True)

    user_id = Column(Integer, index=True)
    user_role = Column(SQLEnum(UserRole))
    recipient_type = Column(String)

    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.pending)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)

    email_sent = Column(Boolean, default=False)
    sms_sent = Column(Boolean, default=False)
    push_sent = Column(Boolean, default=False)
    in_app_sent = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    #source_user = relationship("User", back_populates="sent_notifications")



class EscalationLog(Base):
    __tablename__ = "escalation_logs"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, index=True)

    escalation_level = Column(SQLEnum(EscalationLevel))
    from_user_id = Column(Integer, nullable=True)
    from_role = Column(SQLEnum(UserRole), nullable=True)
    to_user_id = Column(Integer)
    to_role = Column(SQLEnum(UserRole))

    reason = Column(String)
    auto_escalated = Column(Boolean, default=False)
    escalation_time_elapsed = Column(Integer)

    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)


class RoutingAuditLog(Base):
    __tablename__ = "routing_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, index=True)

    rule_applied = Column(String)
    routing_strategy = Column(SQLEnum(RoutingStrategy))
    source_user_id = Column(Integer)
    target_user_ids = Column(JSON)
    decision_factors = Column(JSON)
    execution_time_ms = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)


class SupervisorAssignment(Base):
    __tablename__ = "supervisor_assignments"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, index=True)
    supervisor_id = Column(Integer, index=True)
    hostel_id = Column(Integer, index=True)

    responsibilities = Column(JSON)
    can_escalate = Column(Boolean, default=True)
    max_priority_level = Column(SQLEnum(NotificationPriority))

    working_hours_start = Column(String)
    working_hours_end = Column(String)
    working_days = Column(JSON)

    is_active = Column(Boolean, default=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
