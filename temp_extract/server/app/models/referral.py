from sqlalchemy import Column, String, ForeignKey, Float, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from .base import BaseEntity


class Referral(BaseEntity):
    """Referral model"""
    __tablename__ = "referrals"
    
    # Referral details (as per drawio)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Fixed foreign key
    referred_email = Column(String(255), nullable=True)
    referred_phone = Column(String(20), nullable=True)
    referral_code = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # Added from drawio
    reward_amount = Column(Float, nullable=False, default=0.0)  # Added from drawio
    completed_at = Column(String, nullable=True)  # Added from drawio (using string as per drawio)
    
    # Legacy fields for backward compatibility (minimal set)
    referred_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    referred_name = Column(String(255), nullable=True)
    
    # Relationships
    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_made")
    referred = relationship("User", foreign_keys=[referred_id], back_populates="referrals_received")
    
    def __repr__(self):
        return f"<Referral(id={self.id}, code={self.referral_code}, successful={self.is_successful})>"