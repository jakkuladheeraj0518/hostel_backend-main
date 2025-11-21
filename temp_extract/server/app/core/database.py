from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import settings

# Create database engine
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables"""
    # Import all models to ensure they are registered with Base
    try:
        from app.models import (
            User, Hostel, Room, Bed, Student, Admin, Supervisor,
            LeaveApplication, Payment, Complaint, Notice, Booking,
            Review, Referral, Attendance
        )
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database initialization warning: {e}")
        # Continue anyway - tables might already exist


def drop_tables():
    """Drop all tables"""
    Base.metadata.drop_all(bind=engine)