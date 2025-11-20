"""
Fetch/create/update users
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.repositories.base_repository import BaseRepository
from app.core.roles import Role


class UserRepository(BaseRepository):
    def __init__(self, db: Session, user_role: Optional[str] = None, active_hostel_id: Optional[int] = None, user_hostel_ids: Optional[List[int]] = None):
        super().__init__(db, user_role, active_hostel_id, user_hostel_ids)
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        """Get user by phone_number"""
        return self.db.query(User).filter(User.phone_number == phone_number).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, hostel_id: Optional[int] = None) -> List[User]:
        """Get all users, automatically filtered by hostel access"""
        query = self.db.query(User)
        
        # If explicit hostel_id provided, use it (after validation)
        if hostel_id:
            if not self._validate_hostel_access(hostel_id):
                return []  # No access to this hostel
            query = query.filter(User.hostel_id == hostel_id)
        else:
            # Apply automatic filtering based on user role and access
            query = self._apply_hostel_filter(query, User.hostel_id)
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, user_data: UserCreate) -> User:
        """Create new user"""
        hashed_password = None
        if user_data.password:
            hashed_password = get_password_hash(user_data.password)
        # Normalize hostel_id: treat 0 or other falsy values as None to avoid FK violations
        raw_hostel_id = getattr(user_data, 'hostel_id', None)
        try:
            hostel_id = int(raw_hostel_id) if raw_hostel_id is not None else None
            if hostel_id is not None and hostel_id <= 0:
                hostel_id = None
        except Exception:
            hostel_id = None

        db_user = User(
            email=user_data.email,
            phone_number=getattr(user_data, 'phone_number', None),
            country_code=getattr(user_data, 'country_code', None),
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
            hostel_id=hostel_id
        )
        self.db.add(db_user)
        try:
            self.db.commit()
            self.db.refresh(db_user)
        except Exception:
            # surface a clearer error for foreign-key/constraint issues
            self.db.rollback()
            raise
        return db_user
    
    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def delete(self, user_id: int) -> bool:
        """Delete user"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False
        self.db.delete(db_user)
        self.db.commit()
        return True

