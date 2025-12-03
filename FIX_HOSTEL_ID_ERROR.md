# Fix: Hostel ID Foreign Key Error

## The Error You Encountered

```
sqlalchemy.exc.IntegrityError: (psycopg2.errors.ForeignKeyViolation) 
insert or update on table "preventive_maintenance_schedules" violates 
foreign key constraint "preventive_maintenance_schedules_hostel_id_fkey"
DETAIL: Key (hostel_id)=(0) is not present in table "hostels".
```

## What Happened

You tried to create a preventive maintenance schedule with `hostel_id=0`, but that hostel doesn't exist in your database.

## ✅ Fixed!

The system now validates that the hostel exists before creating the schedule. You'll get a clear error message:

```json
{
  "detail": "Hostel with id 0 not found"
}
```

## How to Fix Your Request

### Step 1: Get Available Hostels

```bash
GET http://127.0.0.1:8000/api/v1/admin/hostels
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "hostels": [
    {
      "id": 1,
      "name": "Main Campus Hostel",
      "address": "123 University Ave"
    },
    {
      "id": 2,
      "name": "North Wing Hostel",
      "address": "456 College St"
    }
  ]
}
```

### Step 2: Use Valid Hostel ID

Now create your preventive maintenance schedule with a valid hostel_id:

```bash
POST http://127.0.0.1:8000/api/v1/admin/preventive-maintenance/preventive-maintenance/schedules
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "hostel_id": 1,  ← Use valid ID from Step 1
  "equipment_type": "HVAC System",
  "maintenance_type": "Filter Replacement",
  "frequency_days": 30,
  "next_due": "2025-12-31"
}
```

**Success Response:**
```json
{
  "id": 1,
  "message": "Preventive maintenance schedule created successfully"
}
```

## If You Don't Have Any Hostels

### Create a Hostel First

```bash
POST http://127.0.0.1:8000/api/v1/super-admin/hostels
Authorization: Bearer SUPERADMIN_TOKEN
Content-Type: application/json

{
  "name": "Test Hostel",
  "address": "123 Test Street",
  "city": "Test City",
  "state": "Test State",
  "pincode": "123456",
  "capacity": 100,
  "contact_email": "test@hostel.com",
  "contact_phone": "1234567890"
}
```

Then use the returned `id` in your maintenance schedule.

## Validation Rules Now Enforced

### Preventive Maintenance Schedule

✅ **hostel_id** - Must exist in hostels table  
✅ **frequency_days** - Must be greater than 0  
✅ **equipment_type** - Required string  
✅ **maintenance_type** - Required string  
✅ **next_due** - Required date  

### Maintenance Request

✅ **hostel_id** - Must exist in hostels table  
✅ **category** - Required (PLUMBING, ELECTRICAL, etc.)  
✅ **priority** - Required (LOW, MEDIUM, HIGH, URGENT)  
✅ **description** - Required string  

### Maintenance Task

✅ **maintenance_request_id** - Must exist  
✅ **assigned_to_id** - User must exist  
✅ **task_title** - Required string  
✅ **task_description** - Required string  

### Preventive Maintenance Task

✅ **schedule_id** - Schedule must exist  
✅ **assigned_to_id** - User must exist (if provided)  
✅ **scheduled_date** - Required date  

## Testing Your Fix

### 1. Test with Swagger UI

Visit: `http://127.0.0.1:8000/docs`

1. Click on the endpoint
2. Click "Try it out"
3. Fill in valid data
4. Click "Execute"

### 2. Test with cURL

```bash
# Get your token
TOKEN=$(curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}' \
  | jq -r '.access_token')

# Get hostels
curl -X GET http://127.0.0.1:8000/api/v1/admin/hostels \
  -H "Authorization: Bearer $TOKEN"

# Create schedule with valid hostel_id
curl -X POST http://127.0.0.1:8000/api/v1/admin/preventive-maintenance/preventive-maintenance/schedules \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hostel_id": 1,
    "equipment_type": "HVAC",
    "maintenance_type": "Filter Change",
    "frequency_days": 30,
    "next_due": "2025-12-31"
  }'
```

### 3. Test with Postman

1. **Login**
   - Method: POST
   - URL: `http://127.0.0.1:8000/api/v1/auth/login`
   - Body: `{"email":"admin@example.com","password":"password"}`
   - Save the `access_token`

2. **Get Hostels**
   - Method: GET
   - URL: `http://127.0.0.1:8000/api/v1/admin/hostels`
   - Headers: `Authorization: Bearer YOUR_TOKEN`
   - Note a valid hostel ID

3. **Create Schedule**
   - Method: POST
   - URL: `http://127.0.0.1:8000/api/v1/admin/preventive-maintenance/preventive-maintenance/schedules`
   - Headers: `Authorization: Bearer YOUR_TOKEN`
   - Body: Use valid hostel_id from step 2

## Common Mistakes to Avoid

❌ **Don't use hostel_id: 0**
```json
{
  "hostel_id": 0,  ← This will fail
  ...
}
```

❌ **Don't use non-existent hostel_id**
```json
{
  "hostel_id": 999,  ← Check if this exists first
  ...
}
```

❌ **Don't use negative frequency_days**
```json
{
  "frequency_days": -1,  ← Must be positive
  ...
}
```

✅ **Do use valid hostel_id**
```json
{
  "hostel_id": 1,  ← Verified to exist
  "equipment_type": "HVAC",
  "maintenance_type": "Filter Change",
  "frequency_days": 30,
  "next_due": "2025-12-31"
}
```

## Error Messages You'll See Now

### Before Fix (Confusing)
```
sqlalchemy.exc.IntegrityError: (psycopg2.errors.ForeignKeyViolation)...
[Long technical traceback]
```

### After Fix (Clear)
```json
{
  "detail": "Hostel with id 0 not found"
}
```

or

```json
{
  "detail": "Frequency days must be greater than 0"
}
```

## Summary

✅ **Problem:** Foreign key violation when using invalid hostel_id  
✅ **Solution:** Added validation to check hostel exists before creating records  
✅ **Benefit:** Clear error messages instead of database errors  
✅ **Status:** Fixed and deployed  

Now you'll get helpful error messages that tell you exactly what's wrong!

---

**Updated:** December 3, 2025  
**Status:** ✅ Fixed
