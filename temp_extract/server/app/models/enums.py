from enum import Enum


class UserType(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    STUDENT = "student"
    VISITOR = "visitor"
    STAFF = "staff"


class RoomType(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    SHARED = "shared"
    DORMITORY = "dormitory"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"


class FeeType(str, Enum):
    RENT = "rent"
    SECURITY_DEPOSIT = "security_deposit"
    MAINTENANCE = "maintenance"
    ELECTRICITY = "electricity"
    WATER = "water"
    MESS = "mess"
    LAUNDRY = "laundry"
    OTHER = "other"


class ComplaintCategory(str, Enum):
    MAINTENANCE = "maintenance"
    FOOD = "food"
    CLEANLINESS = "cleanliness"
    ELECTRICITY = "electricity"
    ELECTRICAL = "electrical"  # Alias for electricity
    WATER = "water"
    PLUMBING = "plumbing"  # Water-related issues
    INTERNET = "internet"
    SECURITY = "security"
    NOISE = "noise"
    FURNITURE = "furniture"
    HOUSEKEEPING = "housekeeping"
    DISCIPLINE = "discipline"
    OTHER = "other"


class ComplaintStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NoticeType(str, Enum):
    GENERAL = "general"
    MAINTENANCE = "maintenance"
    EVENT = "event"
    EMERGENCY = "emergency"
    PAYMENT = "payment"
    RULE = "rule"


class TargetAudience(str, Enum):
    ALL = "all"
    STUDENTS = "students"
    STAFF = "staff"
    SPECIFIC_ROOM = "specific_room"
    SPECIFIC_FLOOR = "specific_floor"


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


# Removed unnecessary enums not specified in drawio files:
# - SubscriptionStatus, SubscriptionType, MealType, DayOfWeek


class HostelType(str, Enum):
    BOYS = "boys"
    GIRLS = "girls"
    CO_ED = "co_ed"
    PG = "pg"
    HOSTEL = "hostel"


class BedStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"


class MaintenanceStatus(str, Enum):
    GOOD = "good"
    NEEDS_REPAIR = "needs_repair"
    UNDER_MAINTENANCE = "under_maintenance"
    OUT_OF_ORDER = "out_of_order"


class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveType(str, Enum):
    CASUAL = "casual"
    MEDICAL = "medical"
    EMERGENCY = "emergency"
    ACADEMIC = "academic"
    VACATION = "vacation"
    OTHER = "other"


class ReviewCategory(str, Enum):
    ACCOMMODATION = "accommodation"
    FOOD = "food"
    STAFF = "staff"
    FACILITIES = "facilities"
    CLEANLINESS = "cleanliness"
    OVERALL = "overall"


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    SNACKS = "snacks"
    DINNER = "dinner"