import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import LeaveApplication

db = SessionLocal()

print("\n=== LEAVE APPLICATIONS STATUS ===\n")

leaves = db.query(LeaveApplication).all()

for leave in leaves:
    print(f"ID: {leave.id}")
    print(f"  Student ID: {leave.student_id}")
    print(f"  Status: {leave.leave_status}")
    print(f"  Dates: {leave.leave_start_date} to {leave.leave_end_date}")
    print(f"  Reason: {leave.leave_reason}")
    print()

# Show pending ones specifically
pending = db.query(LeaveApplication).filter(LeaveApplication.leave_status == 'PENDING').all()
print(f"\n=== PENDING LEAVE APPLICATIONS ({len(pending)}) ===\n")
for leave in pending:
    print(f"✅ ID: {leave.id} | Student: {leave.student_id} | Dates: {leave.leave_start_date} to {leave.leave_end_date}")

db.close()
