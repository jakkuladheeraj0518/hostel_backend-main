# from sqlalchemy.orm import Session
# from sqlalchemy import text
# from sqlalchemy.exc import SQLAlchemyError, IntegrityError
# from typing import Optional, List, Dict, Any
# from app.schemas.super_admin_schemas import HostelUpsert
# from app.models.hostel import Hostel
# import logging

# logger = logging.getLogger(__name__)

# class HostelRepository:
#     @staticmethod
#     def upsert_hostel(db: Session, hostel: HostelUpsert) -> Optional[Dict[str, Any]]:
#         """
#         Insert or update a hostel using ORM (avoids DB function dependency).
#         Returns the upserted hostel as a dict.
#         """
#         try:
#             if hostel.id:
#                 # Update existing hostel
#                 existing = db.query(Hostel).filter(Hostel.id == hostel.id).first()
#                 if existing:
#                     for key, value in hostel.dict(exclude_unset=True).items():
#                         if key != 'id':
#                             setattr(existing, key, value)
#                     db.commit()
#                     db.refresh(existing)
#                     result = existing
#                 else:
#                     # ID provided but hostel doesn't exist; treat as insert
#                     result = Hostel(**hostel.dict(exclude_unset=True, exclude={'id'}))
#                     db.add(result)
#                     db.commit()
#                     db.refresh(result)
#             else:
#                 # Insert new hostel
#                 result = Hostel(**hostel.dict(exclude_unset=True, exclude={'id'}))
#                 db.add(result)
#                 db.commit()
#                 db.refresh(result)
            
#             # Return as dict matching the schema
#             return {
#                 'id': result.id,
#                 'hostel_name': result.hostel_name,
#                 'description': result.description,
#                 'full_address': result.full_address,
#                 'hostel_type': result.hostel_type,
#                 'contact_email': result.contact_email,
#                 'contact_phone': result.contact_phone,
#                 'amenities': result.amenities,
#                 'rules': result.rules,
#                 'check_in': result.check_in,
#                 'check_out': result.check_out,
#                 'total_beds': result.total_beds,
#                 'current_occupancy': result.current_occupancy,
#                 'monthly_revenue': result.monthly_revenue,
#                 'visibility': result.visibility,
#                 'is_featured': result.is_featured,
#                 'created_at': result.created_at,
#                 'location_id': result.location_id,
#             }
#         except IntegrityError as e:
#             db.rollback()
#             logger.error(f'Integrity error during upsert: {e}')
#             raise ValueError('Integrity error during upsert')
#         except SQLAlchemyError as e:
#             db.rollback()
#             logger.error(f'Database error during upsert: {e}')
#             raise

#     @staticmethod
#     def get_all_hostels(db: Session, skip: int = 0, limit: int = 100):
#         q = text('SELECT * FROM hostels ORDER BY id DESC LIMIT :limit OFFSET :skip;')
#         r = db.execute(q, {'limit': limit, 'skip': skip})
#         return r.mappings().all()

#     @staticmethod
#     def get_total_hostels_count(db: Session) -> int:
#         r = db.execute(text('SELECT COUNT(*) FROM hostels;'))
#         return r.scalar() or 0

#     @staticmethod
#     def get_hostel_by_id(db: Session, hostel_id: int):
#         r = db.execute(text('SELECT * FROM hostels WHERE id = :id;'), {'id': hostel_id})
#         return r.mappings().first()

#     @staticmethod
#     def delete_hostel(db: Session, hostel_id: int):
#         try:
#             r = db.execute(text('DELETE FROM hostels WHERE id = :id RETURNING id;'), {'id': hostel_id})
#             deleted = r.scalar()
#             if deleted:
#                 db.commit()
#             else:
#                 db.rollback()
#             return deleted
#         except IntegrityError:
#             db.rollback()
#             raise ValueError('Cannot delete hostel with related records')
#         except SQLAlchemyError:
#             db.rollback()
#             raise

#     @staticmethod
#     def search_hostels(db: Session, search_term: str, skip: int = 0, limit: int = 100):
#         q = text("""
#             SELECT h.*, l.city FROM hostels h
#             LEFT JOIN locations l ON h.location_id = l.id
#             WHERE h.hostel_name ILIKE :s OR h.full_address ILIKE :s OR l.city ILIKE :s
#             ORDER BY h.id DESC LIMIT :limit OFFSET :skip;
#         """)
#         r = db.execute(q, {'s': f'%{search_term}%', 'limit': limit, 'skip': skip})
#         return r.mappings().all()
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional, List, Dict, Any
from app.schemas.super_admin_schemas import HostelUpsert
from app.models.hostel import Hostel
from app.models.admin_hostel_mapping import AdminHostelMapping
import logging

logger = logging.getLogger(__name__)

class HostelRepository:
    def __init__(self, db: Session):
        """Store DB session for use in repository methods."""
        self.db = db

    def upsert_hostel(self, hostel: HostelUpsert) -> Optional[Dict[str, Any]]:
        """Insert or update hostel (ORM-based)."""
        db = self.db
        try:
            if hostel.id:
                existing = db.query(Hostel).filter(Hostel.id == hostel.id).first()
                if existing:
                    for key, value in hostel.dict(exclude_unset=True).items():
                        if key != 'id':
                            setattr(existing, key, value)
                    db.commit()
                    db.refresh(existing)
                    result = existing
                else:
                    result = Hostel(**hostel.dict(exclude_unset=True, exclude={'id'}))
                    db.add(result)
                    db.commit()
                    db.refresh(result)
            else:
                result = Hostel(**hostel.dict(exclude_unset=True, exclude={'id'}))
                db.add(result)
                db.commit()
                db.refresh(result)

            return result.__dict__

        except IntegrityError as e:
            db.rollback()
            # Provide a clearer message for common FK violations (e.g., invalid location_id)
            msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            logger.error(f'Integrity error during upsert: {msg}')
            if 'foreign key' in msg.lower() or 'violates foreign key constraint' in msg.lower():
                raise ValueError('Integrity error during upsert: invalid foreign key (check location_id)')
            raise ValueError(f'Integrity error during upsert: {msg}')
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Database error during upsert: {e}')
            raise

    def get_all_hostels(self, skip: int = 0, limit: int = 100):
        db = self.db
        q = text('SELECT * FROM hostels ORDER BY id DESC LIMIT :limit OFFSET :skip;')
        r = db.execute(q, {'limit': limit, 'skip': skip})
        return r.mappings().all()

    # Compatibility method expected by services: return ORM objects
    def get_all(self, skip: int = 0, limit: int = 100):
        db = self.db
        return db.query(Hostel).order_by(Hostel.id.desc()).offset(skip).limit(limit).all()

    def get_total_hostels_count(self) -> int:
        db = self.db
        r = db.execute(text('SELECT COUNT(*) FROM hostels;'))
        return r.scalar() or 0

    def get_hostel_by_id(self, hostel_id: int):
        db = self.db
        r = db.execute(text('SELECT * FROM hostels WHERE id = :id;'), {'id': hostel_id})
        return r.mappings().first()

    # Compatibility: return ORM object
    def get_by_id(self, hostel_id: int):
        db = self.db
        return db.query(Hostel).filter(Hostel.id == hostel_id).first()

    def delete_hostel(self, hostel_id: int):
        db = self.db
        try:
            r = db.execute(text('DELETE FROM hostels WHERE id = :id RETURNING id;'), {'id': hostel_id})
            deleted = r.scalar()
            if deleted:
                db.commit()
            else:
                db.rollback()
            return deleted
        except IntegrityError:
            db.rollback()
            raise ValueError('Cannot delete hostel with related records')
        except SQLAlchemyError:
            db.rollback()
            raise

    def search_hostels(self, search_term: str, skip: int = 0, limit: int = 100):
        db = self.db
        q = text("""
            SELECT h.*, l.city FROM hostels h
            LEFT JOIN locations l ON h.location_id = l.id
            WHERE h.hostel_name ILIKE :s OR h.full_address ILIKE :s OR l.city ILIKE :s
            ORDER BY h.id DESC LIMIT :limit OFFSET :skip;
        """)
        r = db.execute(q, {'s': f'%{search_term}%', 'limit': limit, 'skip': skip})
        return r.mappings().all()

    def get_by_admin(self, admin_id: int):
        db = self.db
        # Join AdminHostelMapping to fetch Hostel ORM objects for given admin
        return db.query(Hostel).join(AdminHostelMapping, Hostel.id == AdminHostelMapping.hostel_id).filter(AdminHostelMapping.admin_id == admin_id).all()

    def assign_admin(self, admin_id: int, hostel_id: int):
        db = self.db
        # Idempotent assign: do nothing if mapping exists
        existing = db.query(AdminHostelMapping).filter(AdminHostelMapping.admin_id == admin_id, AdminHostelMapping.hostel_id == hostel_id).first()
        if existing:
            return existing
        mapping = AdminHostelMapping(admin_id=admin_id, hostel_id=hostel_id)
        db.add(mapping)
        try:
            db.commit()
            db.refresh(mapping)
            return mapping
        except IntegrityError:
            db.rollback()
            # Race or constraint: try to return existing mapping
            return db.query(AdminHostelMapping).filter(AdminHostelMapping.admin_id == admin_id, AdminHostelMapping.hostel_id == hostel_id).first()
