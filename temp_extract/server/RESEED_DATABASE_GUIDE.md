# 🔄 Database Reseed Required

## Issue
Leave applications endpoint returns 404 because there are no leave applications in the database.

**Current Status:**
- ✅ Complaints: 15 records
- ❌ Leave Applications: 0 records

## Solution: Reseed the Database

### Option 1: Quick Reseed (Recommended)
```bash
python seed.py
```

This will:
- Clear existing data
- Create fresh test data
- Add 15 leave applications
- Add all other test data

### Option 2: Reset and Reseed
```bash
# Reset database
python reset_database.py

# Seed fresh data
python seed.py
```

---

## After Reseeding

### 1. Verify Leave Applications
```bash
python -c "from app.core.database import SessionLocal; from app.models.leave_application import LeaveApplication; db = SessionLocal(); count = db.query(LeaveApplication).count(); print(f'Leave applications: {count}'); db.close()"
```

**Expected Output:** `Leave applications: 15`

### 2. Get Leave Application IDs
```bash
python -c "from app.core.database import SessionLocal; from app.models.leave_application import LeaveApplication; db = SessionLocal(); leaves = db.query(LeaveApplication).limit(5).all(); print('First 5 Leave Application IDs:'); [print(f'  ID: {l.id}') for l in leaves]; db.close()"
```

### 3. Test in Swagger

#### Step 1: Login
```http
POST /api/v1/auth/supervisor/login
{
  "email": "warden@test.com",
  "password": "warden123"
}
```

#### Step 2: List Leave Applications
```http
GET /api/v1/supervisor/leave-applications?page=1&size=20
Authorization: Bearer YOUR_TOKEN
```

**Response will include:**
```json
{
  "items": [
    {
      "id": 1,  // Use this ID!
      "student_name": "Rahul Sharma",
      "leave_status": "pending",
      "leave_start_date": "2025-11-16",
      "leave_end_date": "2025-11-18"
    }
  ]
}
```

#### Step 3: Approve Leave Application
```http
PUT /api/v1/supervisor/leave-applications/1/approve
Authorization: Bearer YOUR_TOKEN
```

**Note:** Use the actual ID from the list response!

---

## Complete Test Data After Reseeding

### Leave Applications (15 Total)

| ID | Student | Type | Status | Start Date | End Date |
|----|---------|------|--------|------------|----------|
| 1 | Rahul Sharma | Casual | Pending | +2 days | +4 days |
| 2 | Priya Patel | Medical | Pending | +1 day | +1 day |
| 3 | Amit Kumar | Casual | Approved | -5 days | -3 days |
| 4 | Sneha Reddy | Vacation | Pending | +7 days | +14 days |
| 5 | Vikram Singh | Medical | Approved | -2 days | -1 day |
| 6 | Anjali Verma | Academic | Pending | +3 days | +5 days |
| 7 | Karan Mehta | Casual | Rejected | -10 days | -8 days |
| 8 | Pooja Desai | Emergency | Approved | +1 day | +2 days |
| 9 | Rohan Joshi | Casual | Pending | +5 days | +7 days |
| 10 | Neha Kapoor | Casual | Pending | +10 days | +12 days |
| 11 | Arjun Nair | Medical | Approved | -7 days | -5 days |
| 12 | Divya Iyer | Academic | Pending | +15 days | +20 days |
| 13 | Siddharth Rao | Emergency | Approved | +4 days | +6 days |
| 14 | Kavya Menon | Casual | Rejected | -15 days | -13 days |
| 15 | Aditya Gupta | Academic | Pending | +8 days | +10 days |

### Other Test Data

- **Users:** 22 (15 students, 4 supervisors, 3 admins)
- **Complaints:** 15
- **Attendance Records:** 105 (7 days × 15 students)
- **Notices:** 5
- **Mess Menus:** 21 (7 days × 3 meals)
- **Payments:** 12
- **Bookings:** 8
- **Visitors:** 8
- **Reviews:** 10
- **Maintenance:** 8

---

## Why This Happened

The database might have been:
1. Partially seeded
2. Reset without reseeding
3. Leave applications table was cleared

**Solution:** Always run `python seed.py` after any database changes.

---

## Quick Commands

### Check Data Status
```bash
# Check all tables
python -c "from app.core.database import SessionLocal; from app.models.user import User; from app.models.complaint import Complaint; from app.models.leave_application import LeaveApplication; from app.models.attendance import Attendance; db = SessionLocal(); print(f'Users: {db.query(User).count()}'); print(f'Complaints: {db.query(Complaint).count()}'); print(f'Leave Apps: {db.query(LeaveApplication).count()}'); print(f'Attendance: {db.query(Attendance).count()}'); db.close()"
```

### Reseed Database
```bash
python seed.py
```

### Start Server
```bash
python run_server.py
```

---

## Expected Results After Reseeding

✅ **Users:** 22  
✅ **Complaints:** 15  
✅ **Leave Applications:** 15  
✅ **Attendance Records:** 105  
✅ **All endpoints working**

---

**Run `python seed.py` now to fix the issue!** 🚀
