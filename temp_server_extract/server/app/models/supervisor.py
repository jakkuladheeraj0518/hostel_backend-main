from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from .base import BaseEntity


class Supervisor(BaseEntity):
    """Supervisor model - separate from User as per drawio requirements"""
    __tablename__ = "supervisors"
    
    # Supervisor identification
    supervisor_name = Column(String(255), nullable=False)
    supervisor_email = Column(String(255), unique=True, nullable=False)
    supervisor_phone = Column(String(20), nullable=False)
    employee_id = Column(String(100), unique=True, nullable=False)
    
    # Role and department
    role = Column(String(100), nullable=False)  # warden, security, maintenance, housekeeping
    department = Column(String(100), nullable=False)
    
    # Access and permissions
    access_level = Column(String(50), nullable=False)  # basic, intermediate, advanced, full
    permissions = Column(String(1000), nullable=True)  # JSON string of specific permissions
    
    # Status
    status = Column(String(50), nullable=False, default="active")  # active, inactive, on_leave, terminated
    invitation_status = Column(String(50), nullable=False, default="pending")  # pending, accepted, rejected
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Link to User account
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)  # Assigned hostel
    reporting_admin_id = Column(String, ForeignKey("admins.id"), nullable=True)
    
    # Employment details
    joining_date = Column(DateTime(timezone=True), nullable=True)
    contract_end_date = Column(DateTime(timezone=True), nullable=True)
    salary = Column(String(100), nullable=True)  # Encrypted
    
    # Shift and schedule
    shift_timing = Column(String(100), nullable=True)  # morning, evening, night, rotational
    working_days = Column(String(200), nullable=True)  # JSON string of working days
    
    # Contact and emergency
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    
    # Profile
    profile_photo = Column(String(500), nullable=True)
    id_proof_type = Column(String(50), nullable=True)
    id_proof_number = Column(String(100), nullable=True)
    
    # Performance tracking
    last_active = Column(DateTime(timezone=True), nullable=True)
    performance_rating = Column(String(10), nullable=True)  # 1-5 scale
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    hostel = relationship("Hostel", foreign_keys=[hostel_id])
    reporting_admin = relationship("Admin", foreign_keys=[reporting_admin_id])
    
    def __repr__(self):
        return f"<Supervisor(id={self.id}, name={self.supervisor_name}, role={self.role}, department={self.department})>"