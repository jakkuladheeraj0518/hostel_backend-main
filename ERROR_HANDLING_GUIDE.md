# Error Handling Guide

## Common Errors and Solutions

### 1. Foreign Key Violation Error

**Error Message:**
```
sqlalchemy.exc.IntegrityError: (psycopg2.errors.ForeignKeyViolation) 
insert or update on table "preventive_maintenance_schedules" violates 
foreign key constraint "preventive_maintenance_schedules_hostel_id_fkey"
DETAIL: Key (hostel_id)=(0) is not present in table "hostels".
```

**Cause:** Trying to create a record with a reference to a non-existent hostel.

**Solution:** 
- Ensure the hostel_id exists in the hostels table before creating related records
- Use a valid hostel_id (not 0 or null)
- The system now validates hostel existence before creating records

**Fixed Endpoints:**
- ✅ POST /preventive-maintenance/schedules - Now validates hostel exists
- ✅ POST /maintenance/requests - Now validates hostel exists
- ✅ POST /maintenance/tasks - Now validates user exists

---

### 2. Authentication Errors

#### 401 Unauthorized

**Error Message:**
```json
{
  "detail": "Missing token. Provide Authorization header or access_token cookie."
}
```

**Cause:** No authentication token provided

**Solution:**
1. Login to get a token:
   ```bash
   POST /api/v1/auth/login
   Body: {"email": "user@example.com", "password": "password"}
   ```
2. Include token in requests:
   ```
   Authorization: Bearer YOUR_ACCESS_TOKEN
   ```

#### 403 Forbidden

**Error Message:**
```json
{
  "detail": "Access denied. Required roles: admin, superadmin"
}
```

**Cause:** User doesn't have the required role

**Solution:**
- Use an account with the correct role
- Student endpoints require STUDENT role
- Admin endpoints require ADMIN or SUPERADMIN role

---

### 3. Validation Errors

#### 404 Not Found - Hostel

**Error Message:**
```json
{
  "detail": "Hostel with id 0 not found"
}
```

**Solution:**
- Use a valid hostel_id from your database
- Query available hostels: `GET /api/v1/admin/hostels`
- Create a hostel first if none exist

#### 404 Not Found - User

**Error Message:**
```json
{
  "detail": "User with id 123 not found"
}
```

**Solution:**
- Use a valid user_id for task assignment
- Query available users: `GET /api/v1/admin/users`
- Ensure the user exists in the system

#### 404 Not Found - Schedule

**Error Message:**
```json
{
  "detail": "Preventive maintenance schedule with id 123 not found"
}
```

**Solution:**
- Create a schedule first before creating tasks
- Use valid schedule_id from existing schedules
- Query schedules: `GET /preventive-maintenance/schedules`

#### 400 Bad Request - Invalid Frequency

**Error Message:**
```json
{
  "detail": "Frequency days must be greater than 0"
}
```

**Solution:**
- Use a positive number for frequency_days
- Example: 7 (weekly), 30 (monthly), 90 (quarterly)

---

### 4. Database Errors

#### Connection Error

**Error Message:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
1. Check DATABASE_URL in .env file
2. Ensure PostgreSQL is running
3. Verify database credentials
4. Check network connectivity

#### Migration Error

**Error Message:**
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution:**
```bash
alembic upgrade head
```

---

## Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Some errors include additional context:

```json
{
  "detail": "Hostel with id 0 not found",
  "status_code": 404,
  "error_type": "NotFoundError"
}
```

---

## HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid input data, validation failed |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions/wrong role |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Request body validation failed |
| 500 | Internal Server Error | Database error, unexpected exception |

---

## Validation Rules

### Preventive Maintenance Schedule

**Required Fields:**
- `hostel_id` (integer, must exist in hostels table)
- `equipment_type` (string)
- `maintenance_type` (string)
- `frequency_days` (integer, must be > 0)
- `next_due` (date)

**Example Valid Request:**
```json
{
  "hostel_id": 1,
  "equipment_type": "HVAC",
  "maintenance_type": "Filter Replacement",
  "frequency_days": 30,
  "next_due": "2025-12-31"
}
```

### Maintenance Request

**Required Fields:**
- `hostel_id` (integer, must exist)
- `category` (string: PLUMBING, ELECTRICAL, HVAC, etc.)
- `priority` (string: LOW, MEDIUM, HIGH, URGENT)
- `description` (string)

**Optional Fields:**
- `photo_url` (string)
- `est_cost` (decimal)
- `scheduled_date` (date)

**Example Valid Request:**
```json
{
  "category": "PLUMBING",
  "priority": "HIGH",
  "description": "Leaking pipe in room 101",
  "est_cost": 500.00
}
```

### Maintenance Task

**Required Fields:**
- `maintenance_request_id` (integer, must exist)
- `assigned_to_id` (integer, user must exist)
- `task_title` (string)
- `task_description` (string)
- `priority` (string)

**Example Valid Request:**
```json
{
  "maintenance_request_id": 1,
  "assigned_to_id": 5,
  "task_title": "Fix leaking pipe",
  "task_description": "Replace damaged pipe section in room 101",
  "priority": "HIGH",
  "estimated_hours": 2,
  "scheduled_date": "2025-12-05"
}
```

---

## Testing Checklist

Before making requests, ensure:

1. **Authentication**
   - [ ] You have a valid JWT token
   - [ ] Token is not expired
   - [ ] Token is included in Authorization header

2. **Data Validation**
   - [ ] All required fields are provided
   - [ ] Field values are in correct format
   - [ ] Referenced IDs exist in database

3. **Permissions**
   - [ ] Your user has the required role
   - [ ] You're accessing the correct endpoint for your role

4. **Database State**
   - [ ] Database is running
   - [ ] Migrations are up to date
   - [ ] Required reference data exists (hostels, users, etc.)

---

## Debugging Steps

### Step 1: Check Authentication
```bash
# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'
```

### Step 2: Verify Token
```bash
# Use token in request
curl -X GET http://localhost:8000/api/v1/admin/hostels \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 3: Check Database
```sql
-- Check if hostel exists
SELECT id, name FROM hostels;

-- Check if user exists
SELECT id, email, role FROM users;

-- Check maintenance schedules
SELECT * FROM preventive_maintenance_schedules;
```

### Step 4: Review Logs
Check application logs for detailed error messages:
```bash
# View recent logs
tail -f logs/app.log
```

---

## Quick Fixes

### Fix 1: Create Test Hostel
```bash
POST /api/v1/admin/hostels
{
  "name": "Test Hostel",
  "address": "123 Test St",
  "capacity": 100
}
```

### Fix 2: Get Valid Hostel ID
```bash
GET /api/v1/admin/hostels
# Use the 'id' from response in subsequent requests
```

### Fix 3: Refresh Token
```bash
POST /api/v1/auth/refresh
{
  "refresh_token": "YOUR_REFRESH_TOKEN"
}
```

---

## Support

If you encounter an error not covered here:

1. Check the full error traceback in logs
2. Verify all validation rules are met
3. Ensure database is in correct state
4. Review the API documentation
5. Check that all migrations are applied

---

## Updated Endpoints with Validation

All these endpoints now have proper validation:

✅ **Preventive Maintenance**
- POST /preventive-maintenance/schedules
  - Validates hostel exists
  - Validates frequency_days > 0

✅ **Maintenance Requests**
- POST /maintenance/requests
  - Validates hostel exists

✅ **Maintenance Tasks**
- POST /maintenance/tasks
  - Validates maintenance request exists
  - Validates assigned user exists

✅ **Preventive Tasks**
- POST /preventive-maintenance/tasks
  - Validates schedule exists
  - Validates assigned user exists

---

**Last Updated:** December 3, 2025  
**Status:** ✅ All validation implemented
