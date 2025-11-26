# 🚀 Supervisor Module - Quick Start Guide

## ✅ Integration Complete!

The Supervisor Module is now live with **18 new endpoints**.

---

## 🎯 Quick Test (3 Steps)

### Step 1: Open Swagger
```
http://localhost:8000/docs
```

### Step 2: Login as Supervisor
Find **POST /api/v1/auth/supervisor/login** and test with:
```json
{
  "email": "your_supervisor@example.com",
  "password": "your_password"
}
```

### Step 3: Authorize & Test
1. Copy `access_token` from response
2. Click **🔓 Authorize** button (top right)
3. Paste token → **Authorize** → **Close**
4. Test any endpoint!

---

## 📡 All 18 Endpoints

### 🔐 Authentication (1)
```
POST /api/v1/auth/supervisor/login
```

### 📊 Dashboard (2)
```
GET /api/v1/supervisor/dashboard/metrics
GET /api/v1/supervisor/dashboard/quick-stats
```

### 🎫 Complaints (4)
```
GET  /api/v1/supervisor/complaints
GET  /api/v1/supervisor/complaints/{id}
PUT  /api/v1/supervisor/complaints/{id}/assign
PUT  /api/v1/supervisor/complaints/{id}/resolve
```

### 📅 Attendance (3)
```
GET  /api/v1/supervisor/attendance
POST /api/v1/supervisor/attendance/{user_id}/approve-leave
POST /api/v1/supervisor/quick-actions/mark-attendance/{user_id}
```

### 🏖️ Leave Applications (3)
```
GET /api/v1/supervisor/leave-applications
PUT /api/v1/supervisor/leave-applications/{id}/approve
PUT /api/v1/supervisor/leave-applications/{id}/reject
```

### 👥 Students (1)
```
GET /api/v1/supervisor/students
```

---

## 💡 Example Requests

### Get Dashboard Metrics
```http
GET /api/v1/supervisor/dashboard/metrics
Authorization: Bearer YOUR_TOKEN
```

### List Complaints
```http
GET /api/v1/supervisor/complaints?status=open&page=1&size=10
Authorization: Bearer YOUR_TOKEN
```

### Assign Complaint
```http
PUT /api/v1/supervisor/complaints/1/assign
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "role": "maintenance",
  "notes": "Urgent repair needed"
}
```

### Mark Attendance
```http
POST /api/v1/supervisor/quick-actions/mark-attendance/123
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "attendance_status": "present"
}
```

### Approve Leave
```http
PUT /api/v1/supervisor/leave-applications/1/approve
Authorization: Bearer YOUR_TOKEN
```

---

## 🔑 User Requirements

Users must have one of these `user_type` values:
- `supervisor`
- `admin`
- `super_admin`

---

## 📝 Query Parameters

### Pagination (all list endpoints)
- `page` - Page number (default: 1)
- `size` - Items per page (default: 20, max: 100)

### Complaints
- `status` - Filter by status (open, in_progress, resolved)
- `priority` - Filter by priority (low, medium, high, critical)
- `assigned_to_me` - Show only assigned to you (true/false)

### Attendance
- `date_from` - Start date (YYYY-MM-DD)
- `date_to` - End date (YYYY-MM-DD)
- `user_id` - Filter by student ID
- `status` - Filter by status (present, absent, late, excused)

### Leave Applications
- `status` - Filter by status (PENDING, APPROVED, REJECTED)
- `pending_only` - Show only pending (true/false)

### Students
- `search` - Search by name, email, or phone

---

## 🎨 Features

✅ **Hostel Context** - Supervisors only see their hostel's data  
✅ **Pagination** - All list endpoints support pagination  
✅ **Filtering** - Advanced filtering on all endpoints  
✅ **Role-Based Assignment** - Assign complaints by role  
✅ **Quick Actions** - Fast attendance marking  

---

## 📚 Full Documentation

- **SUPERVISOR_MODULE_DOCUMENTATION.md** - Complete guide
- **INTEGRATION_SUCCESS.md** - Integration details

---

## 🎉 You're Ready!

Your supervisor module is fully integrated and ready to use!

**API Docs**: http://localhost:8000/docs

Happy supervising! 🚀
