# Quick Authentication Reference Card

## ✅ Implementation Status

**All 9 features now have proper role-based authentication!**

| Feature | File | Role(s) | Endpoints | Status |
|---------|------|---------|-----------|--------|
| Student Reviews | `student/reviews.py` | STUDENT | 6 | ✅ |
| Student Leave Enhanced | `student/leave_enhanced.py` | STUDENT | 4 | ✅ |
| Admin Preventive Maintenance | `admin/preventive_maintenance.py` | ADMIN, SUPERADMIN | 5 | ✅ |
| Admin Maintenance Costs | `admin/maintenance_costs.py` | ADMIN, SUPERADMIN | 1 | ✅ |
| Admin Maintenance | `admin/maintenance.py` | ADMIN, SUPERADMIN | 6 | ✅ |
| Admin Maintenance Tasks | `admin/maintenance_tasks.py` | ADMIN, SUPERADMIN | 7 | ✅ |
| Admin Maintenance Approvals | `admin/maintenance_approvals.py` | ADMIN, SUPERADMIN | 7 | ✅ |
| Admin Leave | `admin/leave.py` | ADMIN, SUPERADMIN | 2 | ✅ |
| Admin Reviews | `admin/reviews.py` | ADMIN, SUPERADMIN | 6 | ✅ |

**Total: 44 endpoints secured with role-based authentication**

## Authentication Flow

```
1. User Login → JWT Token Generated
2. Token Sent in Authorization Header
3. FastAPI Validates Token
4. User Object Extracted
5. Role Checked Against Required Roles
6. Access Granted or Denied
```

## Quick Test Commands

### 1. Login as Student
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"password"}'
```

### 2. Access Student Endpoint
```bash
curl -X GET http://localhost:8000/api/v1/student/reviews/my \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Login as Admin
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'
```

### 4. Access Admin Endpoint
```bash
curl -X GET http://localhost:8000/api/v1/admin/maintenance/requests \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## Role Hierarchy

```
SUPERADMIN (Level 5) ← Full system access
    ↓
ADMIN (Level 4) ← Hostel management
    ↓
SUPERVISOR (Level 3) ← Operational tasks
    ↓
STUDENT (Level 2) ← Personal features
    ↓
VISITOR (Level 1) ← Public access
```

## Common Endpoints by Role

### STUDENT Role
- `POST /student/reviews/{hostel_id}` - Submit review
- `GET /student/reviews/my` - Get my reviews
- `GET /student/leave-enhanced/balance` - Check leave balance
- `POST /student/leave-enhanced/apply` - Apply for leave

### ADMIN/SUPERADMIN Roles
- `POST /admin/maintenance/requests` - Create maintenance request
- `GET /admin/maintenance/requests` - View all requests
- `PUT /admin/maintenance/approvals/{id}/approve` - Approve high-value repair
- `GET /admin/reviews/reviews/pending` - View pending reviews
- `PUT /admin/reviews/reviews/{id}/moderate` - Moderate review
- `GET /admin/leave/requests` - View all leave requests

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 401 | Unauthorized - No/Invalid Token | Login to get valid token |
| 403 | Forbidden - Wrong Role | Use account with correct role |
| 404 | Not Found | Check resource exists |
| 422 | Validation Error | Check request body format |

## Security Checklist

- ✅ JWT tokens expire after 30 minutes
- ✅ Refresh tokens valid for 7 days
- ✅ Passwords hashed with bcrypt
- ✅ Role validation on every request
- ✅ User object type-safe (User model)
- ✅ Clear error messages
- ✅ No manual role checking in endpoints
- ✅ Automatic dependency injection

## Key Files

| File | Purpose |
|------|---------|
| `app/core/security.py` | JWT token handling, password hashing |
| `app/core/roles.py` | Role definitions and hierarchy |
| `app/core/permissions.py` | Permission matrix |
| `app/api/deps.py` | Authentication dependencies |
| `app/models/user.py` | User model |

## Environment Setup

Required in `.env`:
```env
SECRET_KEY=your-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/hostel_db
```

## Verification

Run the verification script:
```bash
python verify_auth.py
```

Expected output: ✅ ALL FILES PASSED AUTHENTICATION VERIFICATION

## Documentation

- 📄 `ROLE_BASED_AUTH_IMPLEMENTATION.md` - Full implementation guide
- 📄 `AUTHENTICATION_SUMMARY.md` - Quick summary
- 📄 `QUICK_AUTH_REFERENCE.md` - This reference card
- 🔍 `verify_auth.py` - Verification script

## Support

If authentication fails:
1. Check token is valid and not expired
2. Verify user has correct role in database
3. Check Authorization header format: `Bearer <token>`
4. Review logs for detailed error messages
5. Ensure database connection is working

---

**Status:** ✅ Production Ready
**Last Updated:** December 3, 2025
**Total Endpoints Secured:** 44
