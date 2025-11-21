from sqlalchemy import Column, String, DateTime, Integer, func
from sqlalchemy.ext.declarative import declared_attr
from app.core.database import Base
import uuid


class BaseEntity(Base):
    """Base entity with common fields"""
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __init__(self, **kwargs):
        # Set the type before calling super().__init__
        if 'type' not in kwargs:
            kwargs['type'] = self.__class__.__name__.lower()
        super().__init__(**kwargs)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


class BaseEntityWithIntId(Base):
    """Base entity with integer ID for simpler entities"""
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __init__(self, **kwargs):
        # Set the type before calling super().__init__
        if 'type' not in kwargs:
            kwargs['type'] = self.__class__.__name__.lower()
        super().__init__(**kwargs)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
