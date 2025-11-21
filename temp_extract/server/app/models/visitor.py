from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from .base import BaseEntity


class Visitor(BaseEntity):
    """Visitor model for physical visitor tracking and security management"""
    __tablename__ = "visitors"
    
    # Basic visitor information
    visitor_name = Column(String(255), nullable=False)
    visitor_email = Column(String(255), nullable=True)
    visitor_phone = Column(String(20), nullable=False)
    
    # Visitor type and purpose
    visitor_type = Column(String(50), nullable=False)  # guest, parent, vendor, official, delivery, maintenance
    purpose_of_visit = Column(Text, nullable=False)
    
    # Visit timing
    check_in_time = Column(DateTime(timezone=True), nullable=False)
    check_out_time = Column(DateTime(timezone=True), nullable=True)
    expected_duration = Column(String(50), nullable=True)  # in hours
    
    # Person to meet
    person_to_meet = Column(Integer, ForeignKey("users.id"), nullable=True)  # Integer FK
    person_name = Column(String(255), nullable=True)
    person_room_number = Column(String(50), nullable=True)
    
    # Identification
    id_proof_type = Column(String(50), nullable=False)  # aadhar, pan, driving_license, passport, voter_id
    id_proof_number = Column(String(100), nullable=False)
    id_proof_photo = Column(String(500), nullable=True)  # Photo URL
    
    # Vehicle details
    vehicle_number = Column(String(50), nullable=True)
    vehicle_type = Column(String(50), nullable=True)  # two_wheeler, four_wheeler, other
    
    # Approval and authorization
    approval_status = Column(String(50), nullable=False, default="pending")  # pending, approved, rejected, checked_in, checked_out
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Integer FK
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Hostel and location
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    entry_gate = Column(String(50), nullable=True)
    
    # Security details
    belongings_deposited = Column(Text, nullable=True)  # JSON string of items
    security_badge_number = Column(String(50), nullable=True)
    
    # Photos
    visitor_photo = Column(String(500), nullable=True)  # Captured at entry
    
    # Emergency contact
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    
    # Visit details
    actual_check_out_time = Column(DateTime(timezone=True), nullable=True)
    visit_duration = Column(String(50), nullable=True)  # Calculated duration
    
    # Notes and remarks
    supervisor_notes = Column(Text, nullable=True)
    security_notes = Column(Text, nullable=True)
    
    # Recurring visitor
    is_recurring = Column(String(1), default='N')  # Y/N
    last_visit_date = Column(DateTime(timezone=True), nullable=True)
    visit_count = Column(String(10), default='1')
    
    # Blacklist/Whitelist
    is_blacklisted = Column(String(1), default='N')  # Y/N
    blacklist_reason = Column(Text, nullable=True)
    is_whitelisted = Column(String(1), default='N')  # Y/N (for frequent visitors)
    
    # Temperature check (COVID-19 or health screening)
    temperature = Column(String(10), nullable=True)
    health_declaration = Column(String(1), default='Y')  # Y/N
    
    # Recorded by
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Integer FK
    checked_out_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Integer FK
    
    # Company/Organization (for official visitors)
    company_name = Column(String(255), nullable=True)
    company_address = Column(String(500), nullable=True)
    
    # Relationships
    hostel = relationship("Hostel", foreign_keys=[hostel_id])
    person_meeting = relationship("User", foreign_keys=[person_to_meet])
    approver = relationship("User", foreign_keys=[approved_by])
    recorder = relationship("User", foreign_keys=[recorded_by])
    checkout_recorder = relationship("User", foreign_keys=[checked_out_by])
    
    def __repr__(self):
        return f"<Visitor(id={self.id}, name={self.visitor_name}, type={self.visitor_type}, status={self.approval_status})>"
    
    @property
    def is_currently_inside(self):
        """Check if visitor is currently inside the hostel"""
        return self.check_in_time is not None and self.check_out_time is None
    
    @property
    def visit_duration_hours(self):
        """Calculate visit duration in hours"""
        if self.check_in_time and self.check_out_time:
            duration = self.check_out_time - self.check_in_time
            return duration.total_seconds() / 3600
        return None
