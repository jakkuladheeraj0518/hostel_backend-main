from sqlalchemy import Column, String, ForeignKey, Float, Text, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .base import BaseEntity
from .enums import MaintenanceStatus, Priority


class Maintenance(BaseEntity):
    """Maintenance model for facility upkeep and repair tracking"""
    __tablename__ = "maintenance"
    
    # Basic information
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    room_number = Column(String(50), nullable=True)
    location_details = Column(String(500), nullable=True)
    
    # Issue details
    issue_category = Column(String(100), nullable=False)  # electrical, plumbing, carpentry, cleaning, appliance, structural
    issue_description = Column(Text, nullable=False)
    priority_level = Column(SQLEnum(Priority), nullable=False, default=Priority.MEDIUM)
    
    # Cost tracking
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    
    # Status and workflow
    status = Column(SQLEnum(MaintenanceStatus), nullable=False, default=MaintenanceStatus.GOOD)
    
    # Assignment and approval
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Integer FK
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)  # Integer FK
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Integer FK
    
    # Dates
    reported_date = Column(DateTime(timezone=True), nullable=False)
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Documentation
    photos = Column(Text, nullable=True)  # JSON string of photo URLs
    materials_used = Column(Text, nullable=True)
    labor_hours = Column(Float, nullable=True)
    
    # Vendor details
    vendor_name = Column(String(255), nullable=True)
    vendor_contact = Column(String(20), nullable=True)
    
    # Notes
    supervisor_notes = Column(Text, nullable=True)
    technician_notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # Approval workflow
    requires_approval = Column(String(1), default='N')  # Y/N
    approval_status = Column(String(50), nullable=True)  # pending, approved, rejected
    rejection_reason = Column(Text, nullable=True)
    
    # Preventive maintenance
    is_preventive = Column(String(1), default='N')  # Y/N
    next_scheduled_date = Column(DateTime(timezone=True), nullable=True)
    maintenance_frequency = Column(String(50), nullable=True)  # weekly, monthly, quarterly, annual
    
    # Relationships
    hostel = relationship("Hostel", foreign_keys=[hostel_id])
    creator = relationship("User", foreign_keys=[created_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<Maintenance(id={self.id}, category={self.issue_category}, status={self.status}, priority={self.priority_level})>"
    
    @property
    def is_overdue(self):
        """Check if maintenance is overdue"""
        if self.scheduled_date and self.status != MaintenanceStatus.GOOD:
            from datetime import datetime
            return datetime.now() > self.scheduled_date
        return False
    
    @property
    def requires_admin_approval(self):
        """Check if maintenance requires admin approval based on cost threshold"""
        # Threshold can be configured per hostel, default is 5000
        threshold = 5000.0
        if self.estimated_cost and self.estimated_cost > threshold:
            return True
        return False
