from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import date, datetime
from decimal import Decimal

class DateRangeFilter(BaseModel):
    start_date: date
    end_date: date
    hostel_ids: Optional[List[int]] = None

class KPISummary(BaseModel):
    total_revenue: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    occupancy_rate: float
    total_complaints: int
    resolved_complaints: int
    average_resolution_time: float
    student_count: int
    
class HostelKPI(BaseModel):
    hostel_id: int
    hostel_name: str
    revenue: Decimal
    expenses: Decimal
    profit: Decimal
    occupancy_rate: float
    total_beds: int
    occupied_beds: int
    complaint_count: int
    resolved_complaints: int
    average_rating: float

class MultiHostelDashboard(BaseModel):
    summary: KPISummary
    hostels: List[HostelKPI]
    period: str
    generated_at: datetime

class RevenueComparison(BaseModel):
    hostel_id: int
    hostel_name: str
    current_period_revenue: Decimal
    previous_period_revenue: Decimal
    growth_rate: float
    monthly_breakdown: List[Dict[str, Any]]

class OccupancyTrend(BaseModel):
    hostel_id: int
    hostel_name: str
    date: date
    occupancy_rate: float
    occupied_beds: int
    total_beds: int

class ComplaintMetrics(BaseModel):
    hostel_id: int
    hostel_name: str
    total_complaints: int
    by_category: Dict[str, int]
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
    average_resolution_time: float
    satisfaction_rating: float

class MarketingAnalytics(BaseModel):
    hostel_id: int
    hostel_name: str
    profile_views: int
    search_appearances: int
    inquiries: int
    bookings: int
    conversion_rate: float
    top_sources: List[Dict[str, Any]]

class AttendanceReport(BaseModel):
    hostel_id: int
    hostel_name: str
    date: date
    total_students: int
    present_count: int
    absent_count: int
    attendance_rate: float
    absent_students: List[Dict[str, str]]

class AttendanceTrend(BaseModel):
    hostel_id: int
    hostel_name: str
    period: str
    daily_trends: List[Dict[str, Any]]
    average_attendance_rate: float
    patterns: Dict[str, Any]

class StudentAttendanceHistory(BaseModel):
    student_id: int
    student_name: str
    hostel_id: int
    total_days: int
    present_days: int
    absent_days: int
    attendance_percentage: float
    recent_absences: List[date]

class ConsolidatedAttendanceReport(BaseModel):
    period: DateRangeFilter
    summary: Dict[str, Any]
    hostel_wise: List[AttendanceReport]
    trends: List[AttendanceTrend]
    generated_at: datetime