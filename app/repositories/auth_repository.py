from sqlalchemy.orm import Session
from datetime import datetime
from app.models.user import User, OTP

# ----------- Users ----------
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone(db: Session, phone: str):
    # FIX: Use phone_number instead of phone
    return db.query(User).filter(User.phone_number == phone).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, *, name: str, email: str = None, phone: str = None, hashed_password: str = None):
    # FIX: Map 'phone' arg to 'phone_number' column
    # Also ensure 'username' is set (it's nullable=False in model)
    # We'll use email or phone as username fallback if not provided, or generate one
    username = email.split('@')[0] if email else phone
    
    user = User(
        name=name, 
        email=email, 
        phone_number=phone,  # Changed from phone=phone
        username=username,   # Added required username field
        hashed_password=hashed_password,
        is_active=True       # Activate by default for registration
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ----------- OTP ----------
def create_otp(db: Session, user_id: int, otp_code: str, expires_at: datetime, email: str = None, phone: str = None):
    otp = OTP(user_id=user_id, otp_code=otp_code, expires_at=expires_at, email=email, phone=phone)
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp

def get_valid_otp(db: Session, otp_code: str, email: str = None, phone: str = None):
    query = db.query(OTP).filter(
        OTP.otp_code == otp_code,
        OTP.is_used == False,
        OTP.expires_at >= datetime.utcnow()
    )
    if email:
        query = query.filter(OTP.email == email)
    if phone:
        query = query.filter(OTP.phone == phone)
    return query.first()

def invalidate_user_otps(db: Session, user_id: int):
    db.query(OTP).filter(OTP.user_id == user_id, OTP.is_used == False).update({"is_used": True})
    db.commit()