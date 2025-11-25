from pydantic import BaseModel, validator
from typing import List, Union


class HostelComparisonRequest(BaseModel):
    hostel_ids: List[Union[int, str]]

    @validator('hostel_ids')
    def validate_and_normalize(cls, v):
        if not v:
            raise ValueError('hostel_ids must be a non-empty list')
        if len(v) > 4:
            raise ValueError('Cannot compare more than 4 hostels')
        # Normalize all IDs to ints for DB queries and API consistency
        normalized = []
        for x in v:
            try:
                normalized.append(int(x))
            except Exception:
                raise ValueError("hostel_ids must be numeric or numeric strings")
        return normalized


class HostelComparisonItem(BaseModel):
    hostel_id: Union[int, str]
    pricing: dict
    amenities: List[str]
    location: Union[str, None]
    rooms_count: int
    beds_count: int
    available_beds: int
