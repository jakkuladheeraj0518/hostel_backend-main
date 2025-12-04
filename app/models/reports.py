from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, Boolean, Text, ForeignKey
from datetime import datetime
from app.core.database import Base

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, nullable=False, index=True)
    student_id = Column(Integer, nullable=False, index=True)  # Keep original field name
    student_name = Column(String(255))
    date = Column(Date, nullable=False, index=True)  # Keep original field name
    is_present = Column(Boolean, default=True)
    marked_by = Column(String(255))
    marked_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Add properties for compatibility with supervisor routes
    @property
    def user_id(self):
        return self.student_id
    
    @property
    def attendance_date(self):
        return self.date
    
    @property
    def attendance_status(self):
        return 'present' if self.is_present else 'absent'
    
    @property
    def check_in_time(self):
        return self.marked_at
    
    @property
    def check_out_time(self):
        return None

class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, nullable=False, index=True)
    student_id = Column(Integer, index=True)
    transaction_type = Column(String(50), nullable=False)  # fee, expense, booking
    category = Column(String(100))
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(Text)
    transaction_date = Column(Date, nullable=False, index=True)
    payment_status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)

class HostelBooking(Base):
    __tablename__ = "hostel_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, nullable=False, index=True)
    student_name = Column(String(255))
    student_email = Column(String(255))
    student_phone = Column(String(20))
    room_type = Column(String(100))
    booking_date = Column(DateTime, default=datetime.utcnow, index=True)
    check_in_date = Column(Date)
    status = Column(String(50), default='pending')  # pending, confirmed, cancelled
    source = Column(String(100))  # website, referral, social_media, etc.
    converted = Column(Boolean, default=False)

class HostelProfileView(Base):
    __tablename__ = "hostel_profile_views"
    
    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, nullable=False, index=True)
    viewed_at = Column(DateTime, default=datetime.utcnow, index=True)
    visitor_ip = Column(String(50))
    source = Column(String(100))  # search, direct, social, etc.
    session_id = Column(String(255))

