"""
Booking Expiry Service - Handles automatic expiration of pending bookings
"""

import threading
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.logger import setup_logger
from app.models.booking import Booking, BookingStatus
from app.repositories.booking_repository import BookingRepository

logger = setup_logger()


class BookingExpiryService:
    """
    Service to handle automatic expiration of pending bookings.
    Runs as a background thread to check and expire bookings.
    """

    def __init__(self, db_session_factory):
        """
        Initialize the booking expiry service.
        
        Args:
            db_session_factory: SQLAlchemy SessionLocal factory
        """
        self.db_session_factory = db_session_factory
        self.running = False
        self.thread = None
        self.check_interval = 300  # Check every 5 minutes (300 seconds)

    def start(self):
        """Start the background booking expiry checker thread."""
        if self.running:
            logger.warning("BookingExpiryService is already running")
            return

        self.running = True
        self.thread = threading.Thread(
            target=self._run_expiry_checker,
            daemon=True
        )
        self.thread.start()
        logger.info("BookingExpiryService started")

    def stop(self):
        """Stop the background booking expiry checker thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("BookingExpiryService stopped")

    def _run_expiry_checker(self):
        """Background task to check and expire pending bookings."""
        while self.running:
            try:
                self._check_and_expire_bookings()
            except Exception as e:
                logger.error(f"Error in booking expiry checker: {str(e)}")
            
            # Sleep before next check
            time.sleep(self.check_interval)

    def _check_and_expire_bookings(self):
        """
        Check for pending bookings that should be expired.
        A booking is expired if:
        1. Status is PENDING
        2. Created more than 24 hours ago (configurable)
        """
        try:
            db: Session = self.db_session_factory()
            
            # Calculate expiry threshold (24 hours ago)
            expiry_threshold = datetime.utcnow() - timedelta(hours=24)
            
            # Find pending bookings that are older than 24 hours
            # FIX: Use .value to ensure we compare String to String
            expired_bookings = db.query(Booking).filter(
                Booking.status == BookingStatus.pending.value,
                Booking.created_at < expiry_threshold
            ).all()
            
            if expired_bookings:
                logger.info(f"Found {len(expired_bookings)} bookings to expire")
                
                for booking in expired_bookings:
                    try:
                        # FIX: Use .value for assignment as well
                        booking.status = BookingStatus.cancelled.value
                        db.add(booking)
                        logger.info(f"Expired booking {booking.id}")
                    except Exception as e:
                        logger.error(f"Error expiring booking {booking.id}: {str(e)}")
                        db.rollback()
                        continue
                
                db.commit()
                logger.info(f"Successfully expired {len(expired_bookings)} bookings")
            
            db.close()
        except Exception as e:
            logger.error(f"Error in _check_and_expire_bookings: {str(e)}")

    def manually_expire_booking(self, db: Session, booking_id: int):
        """
        Manually expire a specific booking.
        
        Args:
            db: Database session
            booking_id: ID of booking to expire
            
        Returns:
            Updated booking object or None if not found
        """
        try:
            booking = db.query(Booking).filter(Booking.id == booking_id).first()
            if booking:
                # FIX: Use .value
                booking.status = BookingStatus.cancelled.value
                db.add(booking)
                db.commit()
                db.refresh(booking)
                logger.info(f"Manually expired booking {booking_id}")
                return booking
            return None
        except Exception as e:
            logger.error(f"Error manually expiring booking: {str(e)}")
            db.rollback()
            return None