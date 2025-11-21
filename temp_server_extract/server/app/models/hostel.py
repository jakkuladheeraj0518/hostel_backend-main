from sqlalchemy import Column, String, Boolean, Float, Integer, Text, Time, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .base import BaseEntityWithIntId
from .enums import HostelType


class Hostel(BaseEntityWithIntId):
    """Hostel model - Updated to match drawio requirements"""
    __tablename__ = "hostels"
    
    # Basic information (as per drawio)
    hostel_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(500), nullable=False)
    hostel_type = Column(SQLEnum(HostelType), nullable=False)
    
    # Contact information (as per drawio)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    
    # Facilities and amenities (as per drawio)
    amenities = Column(Text, nullable=True)  # JSON string of amenities
    rules = Column(Text, nullable=True)
    
    # Timing (as per drawio)
    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)
    
    # Capacity and occupancy (as per drawio)
    total_beds = Column(Integer, nullable=False, default=0)
    occupancy = Column(Integer, nullable=False, default=0)
    
    # Financial (as per drawio)
    revenue = Column(Float, nullable=False, default=0.0)
    
    # Status and visibility (as per drawio)
    status = Column(String(50), nullable=False, default="active")
    visibility = Column(String(50), nullable=False, default="public")  # public, private, hidden
    featured = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    
    # Activity tracking (as per drawio)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    
    # Metrics (as per drawio)
    booking_requests = Column(Integer, default=0)
    complaints = Column(Integer, default=0)
    maintenance_requests = Column(Integer, default=0)
    
    # Legacy fields for backward compatibility (minimal set)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships (only drawio-specified entities)
    users = relationship("User", back_populates="hostel")
    rooms = relationship("Room", back_populates="hostel")
    beds = relationship("Bed", back_populates="hostel")
    students = relationship("Student", back_populates="hostel")
    admins = relationship("Admin", back_populates="hostel")
    supervisors = relationship("Supervisor", back_populates="hostel")
    payments = relationship("Payment", back_populates="hostel")
    complaints = relationship("Complaint", back_populates="hostel")
    notices = relationship("Notice", back_populates="hostel")
    bookings = relationship("Booking", back_populates="hostel")
    reviews = relationship("Review", back_populates="hostel")
    attendance_records = relationship("Attendance", back_populates="hostel")  # Required for Supervisor Attendance Operations
    leave_applications = relationship("LeaveApplication", back_populates="hostel")  # Required for Supervisor Leave Management
    
    def __repr__(self):
        return f"<Hostel(id={self.id}, name={self.hostel_name}, city={self.city})>"