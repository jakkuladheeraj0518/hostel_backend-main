#!/usr/bin/env python3
"""
Database initialization script
Creates initial data including super admin user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, create_tables
from app.core.security import get_password_hash
from app.models.user import User
from app.models.enums import UserType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_super_admin():
    """Create initial super admin user"""
    db: Session = SessionLocal()
    
    try:
        # Check if super admin already exists
        existing_admin = db.query(User).filter(
            User.user_type == UserType.SUPER_ADMIN
        ).first()
        
        if existing_admin:
            logger.info("Super admin already exists")
            return
        
        # Create super admin
        super_admin = User(
            name="Super Admin",
            email="admin@hostelmanagement.com",
            phone="+1234567890",
            user_type=UserType.SUPER_ADMIN,
            password_hash=get_password_hash("admin123"),
            is_active=True,
            is_verified=True
        )
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        logger.info(f"Super admin created with ID: {super_admin.id}")
        logger.info("Login credentials:")
        logger.info("Email: admin@hostelmanagement.com")
        logger.info("Password: admin123")
        logger.info("Please change the password after first login!")
        
    except Exception as e:
        logger.error(f"Error creating super admin: {e}")
        db.rollback()
    finally:
        db.close()


def create_sample_data():
    """Create sample data for development"""
    db: Session = SessionLocal()
    
    try:
        # Create sample hostel admin
        admin_exists = db.query(User).filter(
            User.email == "hostel.admin@example.com"
        ).first()
        
        if not admin_exists:
            hostel_admin = User(
                name="Hostel Admin",
                email="hostel.admin@example.com",
                phone="+1234567891",
                user_type=UserType.ADMIN,
                password_hash=get_password_hash("admin123"),
                is_active=True,
                is_verified=True
            )
            db.add(hostel_admin)
            logger.info("Sample hostel admin created")
        
        # Create sample supervisor
        supervisor_exists = db.query(User).filter(
            User.email == "supervisor@example.com"
        ).first()
        
        if not supervisor_exists:
            supervisor = User(
                name="Hostel Supervisor",
                email="supervisor@example.com",
                phone="+1234567892",
                user_type=UserType.SUPERVISOR,
                password_hash=get_password_hash("supervisor123"),
                is_active=True,
                is_verified=True
            )
            db.add(supervisor)
            logger.info("Sample supervisor created")
        
        # Create sample student
        student_exists = db.query(User).filter(
            User.email == "student@example.com"
        ).first()
        
        if not student_exists:
            student = User(
                name="John Student",
                email="student@example.com",
                phone="+1234567893",
                user_type=UserType.STUDENT,
                password_hash=get_password_hash("student123"),
                is_active=True,
                is_verified=True
            )
            db.add(student)
            logger.info("Sample student created")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main initialization function"""
    logger.info("Starting database initialization...")
    
    try:
        # Create tables
        create_tables()
        logger.info("Database tables created/verified")
        
        # Create super admin
        create_super_admin()
        
        # Create sample data (only in development)
        if os.getenv("ENVIRONMENT", "development") == "development":
            create_sample_data()
            logger.info("Sample data created")
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()