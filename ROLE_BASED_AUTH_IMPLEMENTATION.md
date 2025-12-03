# Role-Based Authentication Implementation

## Overview
All specified features now have proper role-based authentication implemented using JWT tokens and the FastAPI dependency injection system.

## Authentication System

### Core Components

1. **JWT Token Authentication** (`app/core/security.py`)
   - Access tokens with configurable expiration
   - Refresh tokens for extended sessions
   - Secure password hashing with bcrypt
   - Token validation and user extraction

2. **Role Hierarchy** (`app/core/roles.py`)
   - SUPERADMIN (Level 5) - Full system access
   - ADMIN (Level 4) - Hostel management
   - SUPERVISOR (Level 3) - Operational tasks
   - STUDENT (Level 2) - Personal features
   - VISITOR (Level 1) - Public access

3. **Permission Matrix** (`app/core/permissions.py`)
   - Granular permissions for each role
   - Permission checking utilities
   - Role-based access control (RBAC)

4. **Authentication Dependencies** (`app/api/deps.py`)
   - `get_current_user()` - Extract authenticated user from JWT
   - `role_required(*roles)` - Enforce role-based access
   - `permission_required(permission)` - Check specific permissions

## Implemented Features

### Student Features

#### 1. Student Reviews (`app/api/v1/student/reviews.py`)
**Role Required:** STUDENT

**Endpoints:**
- `POST /student/reviews/{hostel_id}` - Submit a review
- `GET /student/reviews/my` - Get my reviews
- `PUT /student/reviews/{review_id}` - Update my review
- `DELETE /student/reviews/{review_id}` - Delete my review
- `POST /student/reviews/{review_id}/helpful` - Mark review as helpful
- `GET /student/reviews/can-review/{hostel_id}` - Check review eligibility

**Features:**
- Automatic spam detection
- Content filtering for inappropriate content
- Quality scoring for auto-approval
- One review per hostel per student
- Helpful vote tracking

#### 2. Student Leave Enhanced (`app/api/v1/student/leave_enhanced.py`)
**Role Required:** STUDENT

**Endpoints:**
- `GET /student/leave-enhanced/balance` - Get leave balance
- `POST /student/leave-enhanced/apply` - Apply for leave
- `GET /student/leave-enhanced/my` - Get my leave requests
- `PUT /student/leave-enhanced/{request_id}/cancel` - Cancel leave request

**Features:**
- Annual leave balance tracking (30 days default)
- Leave usage statistics by year
- Pending request tracking
- Leave cancellation for pending requests

### Admin Features

#### 3. Admin Preventive Maintenance (`app/api/v1/admin/preventive_maintenance.py`)
**Roles Required:** ADMIN, SUPERADMIN

**Endpoints:**
- `POST /preventive-maintenance/schedules` - Create maintenance schedule
- `GET /preventive-maintenance/schedules` - Get all schedules
- `GET /preventive-maintenance/due` - Get due maintenance tasks
- `POST /preventive-maintenance/tasks` - Create preventive task
- `PUT /preventive-maintenance/tasks/{task_id}` - Update task status

**Features:**
- Equipment maintenance scheduling
- Frequency-based maintenance tracking
- Due date calculations
- Task assignment and completion tracking
- Automatic schedule updates on completion

#### 4. Admin Maintenance Costs (`app/api/v1/admin/maintenance_costs.py`)
**Roles Required:** ADMIN, SUPERADMIN

**Endpoints:**
- `GET /maintenance-costs/maintenance/costs` - Get all maintenance costs

**Features:**
- Cost tracking by category
- Payment status monitoring
- Vendor management
- Invoice tracking
- Date range filtering

#### 5. Admin Maintenance (`app/api/v1/admin/maintenance.py`)
**Roles Required:** ADMIN, SUPERADMIN

**Endpoints:**
- `POST /maintenance/requests` - Create maintenance request
- `GET /maintenance/requests` - Get all requests with filters
- `GET /maintenance/requests/{request_id}` - Get specific request
- `PUT /maintenance/requests/{request_id}` - Update request
- `DELETE /maintenance/requests/{request_id}` - Delete request
- `GET /maintenance/requests/stats/summary` - Get statistics

**Features:**
- Categorization (Plumbing, Electrical, HVAC, etc.)
- Priority levels (LOW, MEDIUM, HIGH, URGENT)
- Status tracking (PENDING, IN_PROGRESS, COMPLETED)
- Photo upload support
- Cost estimation and tracking
- Assignment to staff/vendors
- Comprehensive analytics

#### 6. Admin Maintenance Tasks (`app/api/v1/admin/maintenance_tasks.py`)
**Roles Required:** ADMIN, SUPERADMIN

**Endpoints:**
- `POST /maintenance/tasks` - Create and assign task
- `GET /maintenance/tasks` - Get all tasks with filters
- `GET /maintenance/tasks/{task_id}` - Get specific task
- `PUT /maintenance/tasks/{task_id}/progress` - Update progress
- `PUT /maintenance/tasks/{task_id}/verify` - Verify completion
- `PUT /maintenance/tasks/{task_id}/reassign` - Reassign task
- `DELETE /maintenance/tasks/{task_id}` - Delete task

**Features:**
- Task assignment to staff/vendors
- Progress tracking with timestamps
- Quality rating (1-5 stars)
- Completion verification
- Task reassignment capability
- Estimated vs actual hours tracking

#### 7. Admin Maintenance Approvals (`app/api/v1/admin/maintenance_approvals.py`)
**Roles Required:** ADMIN, SUPERADMIN (Supervisors can submit)

**Endpoints:**
- `GET /maintenance/approvals/threshold` - Get approval threshold
- `GET /maintenance/approvals/pending` - Get pending approvals
- `POST /maintenance/approvals/submit` - Submit for approval (Supervisor)
- `PUT /maintenance/approvals/{request_id}/approve` - Approve request
- `PUT /maintenance/approvals/{request_id}/reject` - Reject request
- `GET /maintenance/approvals/history` - Get approval history
- `GET /maintenance/approvals/stats` - Get approval statistics

**Features:**
- High-value repair threshold ($5000 default)
- Approval workflow for expensive repairs
- Supervisor submission capability
- Admin-only approval/rejection
- Approval history tracking
- Cost analytics

#### 8. Admin Leave (`app/api/v1/admin/leave.py`)
**Roles Required:** ADMIN, SUPERADMIN

**Endpoints:**
- `GET /leave/requests` - Get all leave requests
- `PUT /leave/requests/{request_id}/status` - Update leave status

**Features:**
- View all student leave requests
- Filter by hostel and status
- Approve/reject leave requests
- Status management

#### 9. Admin Reviews (`app/api/v1/admin/reviews.py`)
**Roles Required:** ADMIN, SUPERADMIN

**Endpoints:**
- `GET /reviews/reviews` - Get all reviews with filters
- `GET /reviews/reviews/pending` - Get pending reviews
- `PUT /reviews/reviews/{review_id}/moderate` - Moderate review
- `GET /reviews/reviews/spam` - Get spam reviews
- `GET /reviews/reviews/analytics` - Get review analytics
- `DELETE /reviews/reviews/{review_id}` - Delete review

**Features:**
- Review moderation (approve/reject/mark spam)
- Spam detection and management
- Rating distribution analytics
- Approval rate tracking
- Multiple sorting options
- Comprehensive filtering

## Security Features

### 1. JWT Token Security
- Tokens expire after configured time (default: 30 minutes for access tokens)
- Refresh tokens for extended sessions (7 days)
- Secure token validation
- Cookie-based token support as fallback

### 2. Password Security
- Bcrypt hashing with salt
- Safe handling of passwords >72 bytes
- SHA256 pre-hashing for long passwords

### 3. Role-Based Access Control
- Automatic role verification on every request
- Clear error messages for unauthorized access
- Role hierarchy enforcement
- Permission-based access control

### 4. User Context
- Authenticated user object available in all endpoints
- User ID tracking for audit trails
- Role-based data filtering

## Usage Examples

### For Frontend Developers

#### 1. Authentication
```javascript
// Login
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'password' })
});
const { access_token } = await response.json();

// Use token in subsequent requests
const data = await fetch('/api/v1/student/reviews/my', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

#### 2. Student Review Submission
```javascript
const review = await fetch('/api/v1/student/reviews/123', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    rating: 5,
    text: 'Great hostel!',
    photo_url: 'https://example.com/photo.jpg'
  })
});
```

#### 3. Admin Maintenance Request
```javascript
const request = await fetch('/api/v1/admin/maintenance/requests?hostel_id=1', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    category: 'PLUMBING',
    priority: 'HIGH',
    description: 'Leaking pipe in room 101',
    est_cost: 500
  })
});
```

### For Backend Developers

#### Adding New Protected Endpoints
```python
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.models.user import User
from app.api.deps import role_required
from app.core.roles import Role

router = APIRouter()

# Single role
@router.get("/admin-only")
def admin_endpoint(user: User = Depends(role_required(Role.ADMIN))):
    return {"message": "Admin access granted"}

# Multiple roles
@router.get("/admin-or-supervisor")
def multi_role_endpoint(
    user: User = Depends(role_required(Role.ADMIN, Role.SUPERADMIN))
):
    return {"message": "Access granted", "user_id": user.id}

# Permission-based
from app.api.deps import permission_required
from app.core.permissions import Permission

@router.get("/with-permission")
def permission_endpoint(
    user: User = Depends(permission_required(Permission.MANAGE_MAINTENANCE))
):
    return {"message": "Permission granted"}
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Missing token. Provide Authorization header or access_token cookie."
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied. Required roles: admin, superadmin"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

## Testing

### Manual Testing with cURL

#### 1. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"password"}'
```

#### 2. Access Protected Endpoint
```bash
curl -X GET http://localhost:8000/api/v1/student/reviews/my \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 3. Admin Endpoint
```bash
curl -X GET http://localhost:8000/api/v1/admin/maintenance/requests \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

## Configuration

### Environment Variables (.env)
```env
# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/hostel_db
```

## Migration Notes

### Changes Made
1. Replaced `app.dependencies.get_current_user` with `app.core.security.get_current_user`
2. Added `role_required()` dependency to all endpoints
3. Removed manual role checking (`if user.get("role") not in [...]`)
4. Changed `user.get("id")` to `user.id` (proper User object)
5. Added proper type hints (`user: User`)

### Benefits
- Cleaner code with less boilerplate
- Automatic role validation
- Better error messages
- Type safety with User objects
- Consistent authentication across all endpoints

## Next Steps

1. **Add Unit Tests**
   - Test role-based access control
   - Test permission validation
   - Test JWT token generation/validation

2. **Add Rate Limiting**
   - Prevent brute force attacks
   - Limit API calls per user/IP

3. **Add Audit Logging**
   - Log all authentication attempts
   - Track user actions for compliance

4. **Add API Documentation**
   - Update Swagger/OpenAPI docs
   - Add authentication examples

## Support

For issues or questions:
1. Check the error logs in `logs/` directory
2. Verify JWT token is valid and not expired
3. Ensure user has correct role assigned
4. Check database for user permissions

## Summary

All 9 features now have proper role-based authentication:
- ✅ Student Reviews (STUDENT role)
- ✅ Student Leave Enhanced (STUDENT role)
- ✅ Admin Preventive Maintenance (ADMIN, SUPERADMIN roles)
- ✅ Admin Maintenance Costs (ADMIN, SUPERADMIN roles)
- ✅ Admin Maintenance (ADMIN, SUPERADMIN roles)
- ✅ Admin Maintenance Tasks (ADMIN, SUPERADMIN roles)
- ✅ Admin Maintenance Approvals (ADMIN, SUPERADMIN roles)
- ✅ Admin Leave (ADMIN, SUPERADMIN roles)
- ✅ Admin Reviews (ADMIN, SUPERADMIN roles)

The system is secure, scalable, and follows FastAPI best practices.
