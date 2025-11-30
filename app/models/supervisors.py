from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SAEnum
from sqlalchemy.schema import Identity

from app.core.database import Base


class SupervisorRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SUPERVISOR = "supervisor"


class Department(str, Enum):
    OPERATIONS = "operations"
    MAINTENANCE = "maintenance"
    ADMISSIONS = "admissions"
    FINANCE = "finance"
    OTHER = "other"


class AccessLevel(str, Enum):
    FULL = "full"
    LIMITED = "limited"
    READ_ONLY = "read_only"


class Supervisor(Base):
    __tablename__ = "supervisors"

    employee_id = Column(String, primary_key=True, index=True)
    supervisor_name = Column(String, nullable=False)
    supervisor_email = Column(String, unique=True, nullable=False)
    supervisor_phone = Column(String, nullable=False)
    role = Column(SAEnum(SupervisorRole, name="supervisor_role_enum"), nullable=False)
    department = Column(SAEnum(Department, name="department_enum"), nullable=True)
    access_level = Column(SAEnum(AccessLevel, name="access_level_enum"), nullable=True)
    permissions = Column(String, nullable=True)
    status = Column(String, nullable=True)
    invitation_status = Column(String, nullable=True)
    # 🔥 NEW FIELD: link to User table
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    user = relationship("User", back_populates="supervisor_data")


class SupervisorHostel(Base):
    """Many-to-many relationship between supervisors and hostels."""
    __tablename__ = "supervisor_hostels"

    id = Column(Integer, Identity(start=1), primary_key=True)
    employee_id = Column(String, ForeignKey("supervisors.employee_id"), nullable=False, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # relationships
    supervisor = relationship("Supervisor", back_populates="hostels")
    hostel = relationship("Hostel", back_populates="supervisor_assignments")


class SupervisorActivity(Base):
    """Activity log for supervisor actions."""
    __tablename__ = "supervisor_activity"

    id = Column(Integer, Identity(start=1), primary_key=True)
    employee_id = Column(String, ForeignKey("supervisors.employee_id"), nullable=False, index=True)
    action = Column(String, nullable=False)
    details = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AdminOverride(Base):
    __tablename__ = "admin_overrides"

    id = Column(Integer, Identity(start=1), primary_key=True)
    admin_employee_id = Column(String, ForeignKey("supervisors.employee_id"), nullable=False)
    target_supervisor_id = Column(String, ForeignKey("supervisors.employee_id"), nullable=True)
    action = Column(String, nullable=False)
    details = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# relationships (connected using SupervisorHostel table)
Supervisor.hostels = relationship("SupervisorHostel", back_populates="supervisor")
SupervisorActivity.supervisor = relationship("Supervisor", backref="activity_log")
