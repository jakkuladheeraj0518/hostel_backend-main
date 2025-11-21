# Quick Integration Guide

## Step-by-Step Integration Instructions

### Step 1: Register New Routes

You need to add the new route imports to your existing router files. Here's how:

#### 1.1 Admin Routes
Open your admin routes file and add these imports and registrations:

```python
# File: app/api/v1/admin/routes.py (or similar)

# Add these imports at the top
from app.api.v1.admin import (
    maintenance_costs,
    preventive_maintenance,
    reviews,
    leave
)

# Add these router registrations
router.include_router(
    maintenance_costs.router,
    prefix="/maintenance/costs",
    tags=["Admin - Maintenance Costs"]
)

router.include_router(
    preventive_maintenance.router,
    prefix="/preventive-maintenance",
    tags=["Admin - Preventive Maintenance"]
)

router.include_router(
    reviews.router,
    prefix="/reviews",
    tags=["Admin - Reviews"]
)

router.include_router(
    leave.router,
    prefix="/leave",
    tags=["Admin - Leave Management"]
)
```

#### 1.2 Supervisor Routes
```python
# File: app/api/v1/supervisor/routes.py

# Add these imports
from app.api.v1.supervisor import (
    maintenance,
    approvals
)

# Add these router registrations
router.include_router(
    maintenance.router,
    prefix="/maintenance",
    tags=["Supervisor - Maintenance"]
)

router.include_router(
    approvals.router,
    prefix="/approvals",
    tags=["Supervisor - Approvals"]
)
```

#### 1.3 Student Routes
```python
# File: app/api/v1/student/routes.py

# Add this import
from app.api.v1.student import leave

# Add this router registration
router.include_router(
    leave.router,
    prefix="/leave",
    tags=["Student - Leave Management"]
)
```

#### 1.4 Visitor Routes
```python
# File: app/api/v1/visitor/routes.py

# Add this import
from app.api.v1.visitor import reviews

# Add this router registration
router.include_router(
    reviews.router,
    prefix="/reviews",
    tags=["Visitor - Reviews"]
)
```

### Step 2: Create Database Migration

```bash
# Create a new migration for the new tables
alembic revision --autogenerate -m "Add maintenance, review, and leave management tables"

# Review the generated migration file in alembic/versions/
# Then apply the migration
alembic upgrade head
```

### Step 3: Verify Installation

```bash
# Start your development server
uvicorn app.main:app --reload

# Open your browser and check the API docs
# http://localhost:8000/docs

# You should see new endpoint groups:
# - Admin - Maintenance Costs
# - Admin - Preventive Maintenance
# - Admin - Reviews
# - Admin - Leave Management
# - Supervisor - Maintenance
# - Supervisor - Approvals
# - Student - Leave Management
# - Visitor - Reviews
```

### Step 4: Test the New Features

#### Test Maintenance System:
```bash
# Create a maintenance request (as supervisor)
POST /supervisor/maintenance/requests
{
  "hostel_id": 1,
  "category": "PLUMBING",
  "priority": "HIGH",
  "description": "Leaking pipe in room 101",
  "est_cost": 500.00
}

# Get maintenance requests (as admin)
GET /admin/maintenance/requests?hostel_id=1
```

#### Test Review System:
```bash
# Submit a review (as visitor)
POST /visitor/reviews/{hostel_id}
{
  "rating": 5,
  "review_text": "Great hostel with excellent facilities!",
  "photo_url": "https://example.com/photo.jpg"
}

# Moderate review (as admin)
PUT /admin/reviews/{review_id}/moderate
{
  "action": "APPROVE"
}
```

#### Test Leave Management:
```bash
# Apply for leave (as student)
POST /student/leave/apply
{
  "start_date": "2024-12-01",
  "end_date": "2024-12-05",
  "reason": "Family emergency",
  "leave_type": "EMERGENCY"
}

# Approve leave (as supervisor)
PUT /supervisor/leave/requests/{leave_id}/review
{
  "action": "APPROVE",
  "remarks": "Approved"
}
```

## New API Endpoints Available

### Maintenance Management (Admin)
- `GET /admin/maintenance/requests` - List all maintenance requests
- `PUT /admin/maintenance/requests/{id}/assign` - Assign staff to request
- `PUT /admin/maintenance/requests/{id}/approve` - Approve high-value repairs
- `GET /admin/maintenance/budget/summary` - Get budget summary
- `POST /admin/preventive-maintenance/schedules` - Create preventive maintenance schedule
- `GET /admin/preventive-maintenance/due` - Get due maintenance tasks

### Maintenance Management (Supervisor)
- `POST /supervisor/maintenance/requests` - Create maintenance request
- `PUT /supervisor/maintenance/requests/{id}/status` - Update request status
- `POST /supervisor/maintenance/costs` - Add cost tracking
- `PUT /supervisor/maintenance/costs/{id}/payment` - Update payment status
- `GET /supervisor/maintenance/budget/summary` - Get budget summary

### Review System (Admin)
- `GET /admin/reviews` - List all reviews
- `PUT /admin/reviews/{id}/moderate` - Moderate review (approve/reject)
- `GET /admin/reviews/analytics` - Get review analytics

### Review System (Visitor)
- `POST /visitor/reviews/{hostel_id}` - Submit review
- `GET /visitor/hostels/{id}/reviews` - Get hostel reviews
- `POST /visitor/reviews/{id}/helpful` - Mark review as helpful

### Leave Management (Student)
- `POST /student/leave/apply` - Apply for leave
- `GET /student/leave/my` - Get my leave history
- `GET /student/leave/balance` - Get leave balance
- `DELETE /student/leave/{id}` - Cancel leave application

### Leave Management (Admin/Supervisor)
- `GET /admin/leave/requests` - List all leave requests
- `PUT /supervisor/leave/requests/{id}/review` - Approve/reject leave
- `GET /admin/leave/analytics` - Get leave analytics

## Troubleshooting

### Issue: Import errors
**Solution:** Make sure all new files are in the correct directories and Python can find them.

### Issue: Database errors
**Solution:** Run the migration: `alembic upgrade head`

### Issue: Routes not showing in /docs
**Solution:** Check that you've properly registered the routers in the route files.

### Issue: Permission errors
**Solution:** The new routes use the existing RBAC system. Make sure users have the correct roles.

## Need Help?

Check these files for reference:
- `INTEGRATION_SUMMARY.md` - Complete list of added files
- `integrate/README.md` - Original documentation
- `integrate/app/api/v1/*/routes.py` - Example route registrations

---

**You're all set!** The new features are ready to use once you complete these steps.
