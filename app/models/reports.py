from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, Boolean, Text, ForeignKey
from datetime import datetime
from app.core.database import Base

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, nullable=False, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    student_name = Column(String(255))
    date = Column(Date, nullable=False, index=True)
    is_present = Column(Boolean, default=True)
    marked_by = Column(String(255))
    marked_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)

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

class SearchQuery(Base):
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String(500))
    city = Column(String(100), index=True)
    filters = Column(Text)  # JSON string of applied filters
    results_count = Column(Integer)
    searched_at = Column(DateTime, default=datetime.utcnow, index=True)