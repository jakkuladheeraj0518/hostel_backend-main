from pydantic import BaseModel, Field, validator
from datetime import date, timedelta

class LeaveCreate(BaseModel):
    start: date = Field(..., description="Leave start date")
    end: date = Field(..., description="Leave end date")
    reason: str = Field(..., min_length=10, max_length=500, description="Reason for leave (10-500 characters)")
    emergency_contact: str = Field(None, max_length=20, description="Emergency contact number during leave")
    
    @validator('end')
    def validate_end_date(cls, v, values):
        """Validate that end date is after start date"""
        if 'start' in values and v < values['start']:
            raise ValueError('End date must be after or equal to start date')
        
        if 'start' in values:
            duration = (v - values['start']).days
            if duration > 365:
                raise ValueError('Leave duration cannot exceed 365 days')
        
        return v
    
    @validator('start')
    def validate_start_date(cls, v):
        """Validate that start date is not in the past"""
        today = date.today()
        if v < today - timedelta(days=1):
            raise ValueError('Leave start date cannot be in the past')
        return v
    
    @validator('reason')
    def validate_reason(cls, v):
        """Validate reason is meaningful"""
        if v.strip().lower() in ['leave', 'absent', 'na', 'n/a', 'none']:
            raise ValueError('Please provide a meaningful reason for leave')
        return v.strip()
