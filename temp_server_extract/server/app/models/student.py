from sqlalchemy import Column, String, ForeignKey, Date, Integer
from sqlalchemy.orm import relationship
from .base import BaseEntity


class Student(BaseEntity):
    """Student model - separate from User as per drawio requirements"""
    __tablename__ = "students"
    
    # Student identification
    student_id = Column(String(100), unique=True, nullable=False)
    hostel_code = Column(String(50), nullable=False)
    
    # Personal information
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    
    # Accommodation details
    room_number = Column(String(50), nullable=True)
    bed_number = Column(String(50), nullable=True)
    check_in_date = Column(Date, nullable=True)
    
    # Personal details
    blood_group = Column(String(10), nullable=True)
    
    # Guardian information
    guardian_name = Column(String(255), nullable=True)
    guardian_phone = Column(String(20), nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="active")  # active, inactive, graduated, suspended
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Link to User account
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    
    # Additional student fields
    course = Column(String(255), nullable=True)
    year_of_study = Column(String(10), nullable=True)
    college_name = Column(String(255), nullable=True)
    student_photo = Column(String(500), nullable=True)
    
    # Emergency contact
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relation = Column(String(100), nullable=True)
    
    # Documents
    id_proof_type = Column(String(50), nullable=True)
    id_proof_number = Column(String(100), nullable=True)
    id_proof_document = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    hostel = relationship("Hostel", foreign_keys=[hostel_id])
    
    def __repr__(self):
        return f"<Student(id={self.id}, student_id={self.student_id}, name={self.name})>"