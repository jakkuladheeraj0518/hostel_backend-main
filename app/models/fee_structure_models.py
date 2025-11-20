from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class FeeFrequency(str, enum.Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    annual = "annual"

# class Hostel(Base):
#     __tablename__ = "hostels"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), nullable=False)
#     address = Column(Text, nullable=True)
#     capacity = Column(Integer, default=0)

#     fee_plans = relationship("FeePlan", back_populates="hostel", cascade="all, delete")
#     deposits = relationship("SecurityDeposit", back_populates="hostel", cascade="all, delete")
#     mess_charges = relationship("MessCharge", back_populates="hostel", cascade="all, delete")
#     services = relationship("AdditionalService", back_populates="hostel", cascade="all, delete")

#     # ✅ Add this line
#     payments = relationship("Payment", back_populates="hostel", cascade="all, delete")
#     invoices = relationship("Invoice", back_populates="hostel")
#     reminder_config = relationship(
#         "ReminderConfiguration",
#         back_populates="hostel",
#         uselist=False,
#         cascade="all, delete-orphan"
#     )



class FeePlan(Base):
    __tablename__ = "fee_plans"
    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"))
    plan_name = Column(String(100), nullable=False)
    frequency = Column(Enum(FeeFrequency), nullable=False)
    amount = Column(Float, nullable=False)
    room_type = Column(String(50))
    description = Column(Text, nullable=True)

    hostel = relationship("Hostel", back_populates="fee_plans")

class SecurityDeposit(Base):
    __tablename__ = "security_deposits"
    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"))
    name = Column(String(100))
    amount = Column(Float, nullable=False)
    refundable = Column(Boolean, default=True)
    hostel = relationship("Hostel", back_populates="deposits")

class MessCharge(Base):
    __tablename__ = "mess_charges"
    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"))
    meal_type = Column(String(50))
    frequency = Column(Enum(FeeFrequency))
    amount = Column(Float, nullable=False)
    is_mandatory = Column(Boolean, default=True)
    hostel = relationship("Hostel", back_populates="mess_charges")

class AdditionalService(Base):
    __tablename__ = "additional_services"
    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"))
    service_name = Column(String(100))
    amount = Column(Float, nullable=False)
    frequency = Column(Enum(FeeFrequency))
    description = Column(Text, nullable=True)
    hostel = relationship("Hostel", back_populates="services")
