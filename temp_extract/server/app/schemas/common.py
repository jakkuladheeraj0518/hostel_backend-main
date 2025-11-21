from pydantic import BaseModel
from typing import List, Optional, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    class Config:
        from_attributes = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MessageResponse(BaseSchema):
    """Standard message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseSchema):
    """Standard error response"""
    error: bool = True
    message: str
    details: Optional[Any] = None
    status_code: int


class PaginationParams(BaseSchema):
    """Pagination parameters"""
    page: int = 1
    size: int = 20
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 20
            }
        }


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response wrapper"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, size: int):
        """Create paginated response"""
        pages = (total + size - 1) // size
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )


class FilterParams(BaseSchema):
    """Base filter parameters"""
    search: Optional[str] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"  # asc or desc
    
    class Config:
        json_schema_extra = {
            "example": {
                "search": "search term",
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }