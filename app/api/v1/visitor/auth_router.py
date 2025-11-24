from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from app.schemas.auth_schemas import UserRegister, UserResponse, OTPVerify, OTPResend, UserLogin, Token
from app.repositories import auth_repository as repo
from app.services import auth_service as service
from app.utils.helpers import otp_expiry_time
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import OTP

router = APIRouter()
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth_schemas import UserRegister, OTPVerify, OTPResend, Token
from app.schemas.auth_schemas import UserRegister, UserResponse, OTPVerify, OTPResend, Token

from app.repositories import auth_repository as repo
from app.services import auth_service as service
from app.core.database import get_db

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED, operation_id="visitor_register_user")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    if not user_data.email and not user_data.phone:
        raise HTTPException(400, "Email or phone required")
    if user_data.email and repo.get_user_by_email(db, user_data.email):
        raise HTTPException(400, "Email already registered")
    if user_data.phone and repo.get_user_by_phone(db, user_data.phone):
        raise HTTPException(400, "Phone already registered")

    hashed = service.get_password_hash(user_data.password)
    user = repo.create_user(db, name=user_data.name, email=user_data.email, phone=user_data.phone, hashed_password=hashed)

    otp_code = service.generate_otp()
    expires_at = service.otp_expiry_time()
    repo.create_otp(db, user_id=user.id, otp_code=otp_code, expires_at=expires_at, email=user.email, phone=user.phone_number)

    if user.email:
        await service.send_otp_email(user.email, otp_code)
    if user.phone_number:
        await service.send_otp_sms(user.phone_number, otp_code)

    return {"message": "User registered. OTP sent."}

@router.post("/verify-otp", response_model=Token, operation_id="visitor_verify_otp")
async def verify_otp(otp_data: OTPVerify, db: Session = Depends(get_db)):
    otp_record = repo.get_valid_otp(db, otp_data.otp_code, email=otp_data.email, phone=otp_data.phone)
    if not otp_record:
        raise HTTPException(400, "Invalid or expired OTP")

    otp_record.is_used = True
    user = repo.get_user_by_id(db, otp_record.user_id)
    user.is_verified = True
    db.add_all([otp_record, user])
    db.commit()

    token = service.create_access_token({"sub": str(user.id), "email": user.email, "phone": user.phone_number})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/resend-otp", operation_id="visitor_resend_otp")
async def resend_otp(otp_data: OTPResend, db: Session = Depends(get_db)):
    user = None
    if otp_data.email:
        user = repo.get_user_by_email(db, otp_data.email)
    elif otp_data.phone:
        user = repo.get_user_by_phone(db, otp_data.phone)
    if not user:
        raise HTTPException(404, "User not found")

    repo.invalidate_user_otps(db, user.id)
    otp_code = service.generate_otp()
    expires_at = service.otp_expiry_time()
    repo.create_otp(db, user_id=user.id, otp_code=otp_code, expires_at=expires_at, email=user.email, phone=user.phone_number)

    if user.email:
        await service.send_otp_email(user.email, otp_code)
    if user.phone_number:
        await service.send_otp_sms(user.phone_number, otp_code)

    return {"message": "OTP resent successfully"}

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, operation_id="visitor_register_user_response")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    if not user_data.email and not user_data.phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either email or phone must be provided")

    if user_data.email:
        existing = repo.get_user_by_email(db, user_data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if user_data.phone:
        existing = repo.get_user_by_phone(db, user_data.phone)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already registered")

    hashed = service.get_password_hash(user_data.password)
    user = repo.create_user(db, name=user_data.name, email=user_data.email, phone=user_data.phone, hashed_password=hashed)

    otp_code = service.generate_otp()
    expires_at = otp_expiry_time()
    repo.create_otp(db, user_id=user.id, otp_code=otp_code, expires_at=expires_at, email=user.email, phone=user.phone_number)

    if user_data.email:
        await service.send_otp_email(user_data.email, otp_code)
    if user_data.phone:
        await service.send_otp_sms(user_data.phone, otp_code)

    return user

@router.post("/verify-otp", response_model=Token, operation_id="visitor_verify_otp_response")
async def verify_otp(otp_data: OTPVerify, db: Session = Depends(get_db)):
    if not otp_data.email and not otp_data.phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either email or phone must be provided")
    
    print(f"\nVerifying OTP: {otp_data.otp_code} for email: {otp_data.email}, phone: {otp_data.phone}")
    
    otp_record = repo.get_valid_otp(db, otp_data.otp_code, email=otp_data.email, phone=otp_data.phone)
    if not otp_record:
        # Let's check if we can find the OTP regardless of usage status
        all_otps = db.query(OTP).filter(OTP.otp_code == otp_data.otp_code).all()
        if all_otps:
            print(f"Found OTPs but they were invalid:")
            for otp in all_otps:
                print(f"OTP: {otp.otp_code}, Used: {otp.is_used}, Expires: {otp.expires_at}, Email: {otp.email}, Phone: {otp.phone}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
    
    print(f"Found valid OTP record: {otp_record.otp_code}, Expires: {otp_record.expires_at}")
    
    if datetime.utcnow() > otp_record.expires_at:
        print(f"OTP expired at {otp_record.expires_at}, current time: {datetime.utcnow()}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired")

    # mark used
    otp_record.is_used = True
    db.add(otp_record)
    db.commit()

    # set user verified
    user = repo.get_user_by_id(db, otp_record.user_id)
    user.is_verified = True
    db.add(user)
    db.commit()

    access_token = service.create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/resend-otp", operation_id="visitor_resend_otp_response")
async def resend_otp(otp_data: OTPResend, db: Session = Depends(get_db)):
    if not otp_data.email and not otp_data.phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either email or phone must be provided")
    user = None
    if otp_data.email:
        user = repo.get_user_by_email(db, otp_data.email)
    if otp_data.phone:
        user = repo.get_user_by_phone(db, otp_data.phone)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    otp_code = service.generate_otp()
    expires_at = otp_expiry_time()
    repo.create_otp(db, user_id=user.id, otp_code=otp_code, expires_at=expires_at, email=user.email, phone=user.phone_number)

    if otp_data.email:
        await service.send_otp_email(otp_data.email, otp_code)
    if otp_data.phone:
        await service.send_otp_sms(otp_data.phone, otp_code)
    return {"message": "OTP sent successfully"}
