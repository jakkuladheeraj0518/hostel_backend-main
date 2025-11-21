# Route Registration Code Snippets

Copy and paste these code snippets into your respective route files to activate the new features.

---

## 1. Admin Routes

**File: `app/api/v1/admin/routes.py`** (or wherever your admin routes are defined)

Add these imports at the top of the file:
```python
from app.api.v1.admin import (
    maintenance_costs,
    preventive_maintenance,
    reviews,
    leave
)
```

Add these router registrations (usually after existing router.include_router calls):
```python
# Maintenance Management Routes
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

# Review Management Routes
router.include_router(
    reviews.router,
    prefix="/reviews",
    tags=["Admin - Reviews"]
)

# Leave Management Routes
router.include_router(
    leave.router,
    prefix="/leave",
    tags=["Admin - Leave Management"]
)
```

---

## 2. Supervisor Routes

**File: `app/api/v1/supervisor/routes.py`**

Add these imports at the top:
```python
from app.api.v1.supervisor import (
    maintenance,
    approvals
)
```

Add these router registrations:
```python
# Maintenance Management Routes
router.include_router(
    maintenance.router,
    prefix="/maintenance",
    tags=["Supervisor - Maintenance"]
)

# Approval Workflow Routes
router.include_router(
    approvals.router,
    prefix="/approvals",
    tags=["Supervisor - Approvals"]
)
```

---

## 3. Student Routes

**File: `app/api/v1/student/routes.py`**

Add this import at the top:
```python
from app.api.v1.student import leave
```

Add this router registration:
```python
# Leave Management Routes
router.include_router(
    leave.router,
    prefix="/leave",
    tags=["Student - Leave Management"]
)
```

---

## 4. Visitor Routes

**File: `app/api/v1/visitor/routes.py`**

Add this import at the top:
```python
from app.api.v1.visitor import reviews
```

Add this router registration:
```python
# Review & Rating Routes
router.include_router(
    reviews.router,
    prefix="/reviews",
    tags=["Visitor - Reviews"]
)
```

---

## Complete Example: Admin Routes File

Here's what your complete admin routes file might look like:

```python
from fastapi import APIRouter
from app.api.v1.admin import (
    # Your existing imports
    hostels,
    students,
    # ... other existing imports ...
    
    # NEW IMPORTS - Add these
    maintenance_costs,
    preventive_maintenance,
    reviews,
    leave
)

router = APIRouter()

# Your existing route registrations
router.include_router(hostels.router, prefix="/hostels", tags=["Admin - Hostels"])
router.include_router(students.router, prefix="/students", tags=["Admin - Students"])
# ... other existing routes ...

# NEW ROUTE REGISTRATIONS - Add these
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

---

## Verification

After adding the routes, restart your server and check:

```bash
# Start server
uvicorn app.main:app --reload

# Open browser
http://localhost:8000/docs
```

You should see these new sections in the API documentation:
- **Admin - Maintenance Costs**
- **Admin - Preventive Maintenance**
- **Admin - Reviews**
- **Admin - Leave Management**
- **Supervisor - Maintenance**
- **Supervisor - Approvals**
- **Student - Leave Management**
- **Visitor - Reviews**

---

## Troubleshooting

### Import Error
If you get an import error like `ModuleNotFoundError`:
1. Make sure the files were copied correctly
2. Check that `__init__.py` exists in each directory
3. Restart your Python server

### Route Not Showing
If routes don't appear in `/docs`:
1. Check for syntax errors in the route registration
2. Make sure the router variable name matches (usually `router`)
3. Verify the prefix doesn't conflict with existing routes

### Database Error
If you get database errors:
```bash
# Run migrations first
alembic revision --autogenerate -m "Add new tables"
alembic upgrade head
```

---

## Quick Copy-Paste Summary

**Admin Routes:**
```python
from app.api.v1.admin import maintenance_costs, preventive_maintenance, reviews, leave
router.include_router(maintenance_costs.router, prefix="/maintenance/costs", tags=["Admin - Maintenance Costs"])
router.include_router(preventive_maintenance.router, prefix="/preventive-maintenance", tags=["Admin - Preventive Maintenance"])
router.include_router(reviews.router, prefix="/reviews", tags=["Admin - Reviews"])
router.include_router(leave.router, prefix="/leave", tags=["Admin - Leave Management"])
```

**Supervisor Routes:**
```python
from app.api.v1.supervisor import maintenance, approvals
router.include_router(maintenance.router, prefix="/maintenance", tags=["Supervisor - Maintenance"])
router.include_router(approvals.router, prefix="/approvals", tags=["Supervisor - Approvals"])
```

**Student Routes:**
```python
from app.api.v1.student import leave
router.include_router(leave.router, prefix="/leave", tags=["Student - Leave Management"])
```

**Visitor Routes:**
```python
from app.api.v1.visitor import reviews
router.include_router(reviews.router, prefix="/reviews", tags=["Visitor - Reviews"])
```

---

**That's it!** Copy these snippets into your route files and you're ready to go! 🚀
