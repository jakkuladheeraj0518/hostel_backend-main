from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.core.database import Base


class Waitlist(Base):
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True)
    hostel_id = Column(Integer, nullable=False)
    room_type = Column(String, nullable=False)
    visitor_id = Column(Integer, nullable=False)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
