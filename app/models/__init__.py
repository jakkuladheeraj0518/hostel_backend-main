"""
Database models
"""

# Core Models
from app.models.user import User, OTP
from app.models.rooms import Room
from app.models.admin import Admin, AdminHostelAssignment
from app.models.hostel import Hostel
from app.models.admin_hostel_mapping import AdminHostelMapping
from app.models.session_context import SessionContext
from app.models.permission import Permission, RolePermission
from app.models.audit_log import AuditLog
from app.models.refresh_token import RefreshToken
from app.models.approval_request import ApprovalRequest
from app.models.password_reset import PasswordResetToken

# Booking Models (Ensure BookingRequest is here)
from app.models.booking import Booking, BookingRequest

# Complaint Models
from app.models.complaint import Complaint, ComplaintNote

# Report & Analytics Models
from app.models.reports import (
    Attendance,
    FinancialTransaction,
    HostelBooking,
    HostelProfileView,
    SearchQuery,
)

# Fee & Payment Models
from app.models.fee_structure_models import (
    FeePlan,
    SecurityDeposit,
    MessCharge,
    AdditionalService,
    FeeFrequency,
)
from app.models.payment_models import Invoice, Transaction, Receipt, RefundRequest
from app.models.payment_models import Customer, PaymentWebhook, Refund
from app.models.subscription import Payment

# Supervisors
from app.models.supervisors import Supervisor, SupervisorHostel, SupervisorActivity, AdminOverride

__all__ = [
    "User",
    "OTP",
    "Hostel",
    "Room",
    "Admin",
    "AdminHostelAssignment",
    "AdminHostelMapping",
    "SessionContext",
    "Permission",
    "RolePermission",
    "AuditLog",
    "RefreshToken",
    "ApprovalRequest",
    "PasswordResetToken",
    "Booking",
    "BookingRequest",  # Added
    "Complaint",
    "ComplaintNote",
    "Attendance",
    "FinancialTransaction",
    "HostelBooking",
    "HostelProfileView",
    "SearchQuery",
    "FeePlan",
    "SecurityDeposit",
    "MessCharge",
    "AdditionalService",
    "FeeFrequency",
    "Invoice",
    "Transaction",
    "Receipt",
    "RefundRequest",
    "Customer",
    "Payment",
    "PaymentWebhook",
    "Refund",
    "Supervisor",
    "SupervisorHostel",
    "SupervisorActivity",
    "AdminOverride"
]