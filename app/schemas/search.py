from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

class HostelSearchFilters(BaseModel):
    query: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    pincode: Optional[str] = None
    gender: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    amenities: Optional[List[str]] = None
    min_rating: Optional[float] = None
    available_only: bool = True
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = 5.0
    
class HostelSearchSort(BaseModel):
    sort_by: str = Field(default="rating", pattern="^(price_asc|price_desc|rating|distance|newest|popularity)$")
    
class HostelSearchRequest(BaseModel):
    filters: HostelSearchFilters
    sort: Optional[HostelSearchSort] = HostelSearchSort()
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class HostelSearchResult(BaseModel):
    id: int
    name: str
    description: str
    location: str
    city: str
    area: str
    pincode: str
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    gender: str
    contact_phone: str
    contact_email: str
    available_beds: int
    total_beds: int
    price_range_min: Decimal
    price_range_max: Decimal
    rating: float
    review_count: int
    amenities: List[str]
    photos: List[str]
    distance_km: Optional[float] = None
    
    class Config:
        from_attributes = True

class HostelSearchResponse(BaseModel):
    results: List[HostelSearchResult]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    facets: Optional[dict] = None  # Faceted search aggregations