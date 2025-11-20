"""
Global configuration + Database connection and session management.
This file merges:
 - Pydantic Settings configuration
 - Database engine, session, and initialization
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# ---------------------------------------------------------
# SETTINGS (Loads environment variables from .env)
# ---------------------------------------------------------

env_path = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    # Database
    # NOTE: conflict markers were present here. Using a neutral placeholder value.
    # Replace this via environment variable or .env for your local password.
    DATABASE_URL: str = "postgresql://postgres:12345678@localhost/hostelA"
    COMMISSION_RATE: float = 0.15

    ELASTICSEARCH_URL: Optional[str] = None

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Alembic override
    ALEMBIC_DATABASE_URL: Optional[str] = None

    # Email / SMTP
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: Optional[str] = None
    EMAIL_PASS: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    EMAIL_USE_TLS: bool = True
    EMAIL_USE_SSL: bool = False

    # Twilio SMS
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None

    # OTP / MFA
    OTP_EXPIRY_MINUTES: int = 5
    OTP_EXPIRY_SECONDS: int = OTP_EXPIRY_MINUTES * 60
    OTP_LENGTH: int = 6
    OTP_DELIVERY_METHOD: str = "sms"

    # Password policy
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SYMBOL: bool = False
    PASSWORD_REQUIRE_UPPER: bool = True

    # OAuth providers
    OAUTH_GOOGLE_CLIENT_ID: Optional[str] = None
    OAUTH_GOOGLE_CLIENT_SECRET: Optional[str] = None
    OAUTH_GOOGLE_REDIRECT_URI: Optional[str] = None

    OAUTH_GITHUB_CLIENT_ID: Optional[str] = None
    OAUTH_GITHUB_CLIENT_SECRET: Optional[str] = None
    OAUTH_GITHUB_REDIRECT_URI: Optional[str] = None

    # API Keys
    API_KEY: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None

    # Password reset
    PASSWORD_RESET_TOKEN_EXPIRY_MINUTES: int = 15
    PASSWORD_RESET_CODE_LENGTH: int = 6

    # App Info
    APP_NAME: str = "Hostel Management System"
    APP_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # File uploads
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = str(env_path) if env_path.exists() else ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()


# ---------------------------------------------------------
# DATABASE CONNECTION + SESSION MANAGEMENT
# ---------------------------------------------------------

# Create Engine
engine = create_engine(settings.DATABASE_URL)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Model
Base = declarative_base()


def get_db():
    """FastAPI dependency for DB sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Seed data removed as requested.
    """
    # Import models so metadata can detect them
    from app.models import (
        user, hostel, admin_hostel_mapping,
        session_context, permission, audit_log,
        refresh_token, approval_request, password_reset,
        complaint, reports
    )

    Base.metadata.create_all(bind=engine)
