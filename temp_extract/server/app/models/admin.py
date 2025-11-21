from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from .base import BaseEntity


class Admin(BaseEntity):
    """Admin model - separate from User as per drawio requirements"""
    __tablename__ = "admins"
    
    # Admin identification
    admin_id = Column(String(100), unique=True, nullable=False)
    
    # Personal information
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    
    # Role and permissions
    role = Column(String(100), nullable=False)  # super_admin, admin, manager
    permissions = Column(Text, nullable=True)  # JSON string of permissions
    
    # Hostel assignment
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Status and activity
    status = Column(String(50), nullable=False, default="active")  # active, inactive, suspended
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Link to User account
    
    # Additional admin fields
    employee_id = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)
    joining_date = Column(DateTime(timezone=True), nullable=True)
    reporting_manager_id = Column(String, ForeignKey("admins.id"), nullable=True)
    
    # Contact details
    office_address = Column(String(500), nullable=True)
    emergency_contact = Column(String(20), nullable=True)
    
    # Profile
    profile_photo = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    hostel = relationship("Hostel", foreign_keys=[hostel_id])
    reporting_manager = relationship("Admin", remote_side="Admin.id")
    subordinates = relationship("Admin", back_populates="reporting_manager")
    
    def __repr__(self):
        return f"<Admin(id={self.id}, admin_id={self.admin_id}, name={self.name}, role={self.role})>"
    
    def get_managed_hostels(self):
        """Get list of hostels managed by this admin"""
        # Implementation for getting managed hostels
        if self.role == "super_admin":
            # Super admin manages all hostels
            return []  # Return all hostels query
        else:
            # Regular admin manages assigned hostel
            return [self.hostel] if self.hostel else []
    
    def validate_permissions(self, required_permission):
        """Validate if admin has required permission"""
        if not self.permissions:
            return False
        
        import json
        try:
            perms = json.loads(self.permissions)
            return required_permission in perms
        except:
            return False