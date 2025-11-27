# 🧪 Testing Checklist - All Features

## Quick Start
```bash
# Start the server
python -m uvicorn app.main:app --reload

# Open Swagger UI
http://localhost:8000/docs
```

---

## ✅ Feature Testing Checklist

### 1. Review Submission APIs (Student Reviews)
- [ ] POST `/api/v1/student/reviews/{hostel_id}` - Submit a review
- [ ] GET `/api/v1/student/reviews/my` - Get my reviews
- [ ] POST `/api/v1/student/reviews/{review_id}/helpful` - Mark helpful
- [ ] PUT `/api/v1/student/reviews/{review_id}` - Update review
- [ ] DELETE `/api/v1/student/reviews/{review_id}` - Delete review

**Expected**: Rating 1-5, text, photo upload, spam detection

---

### 2. Review Moderation APIs (Admin Reviews)
- [ ] GET `/api/v1/admin/reviews/reviews` - List all reviews
- [ ] GET `/api/v1/admin/reviews/reviews/pending` - Get pending reviews
- [ ] PUT `/api/v1/admin/reviews/reviews/{id}/moderate` - Approve/reject
- [ ] GET `/api/v1/admin/reviews/reviews/spam` - Get spam reviews
- [ ] GET `/api/v1/admin/reviews/reviews/analytics` - Get analytics

**Expected**: Approval/rejection, spam detection, content filtering

---

### 3. Review Display & Sorting (Admin Reviews)
- [ ] GET `/api/v1/admin/reviews/reviews?sort_by=newest`
- [ ] GET `/api/v1/admin/reviews/reviews?sort_by=highest_rating`
- [ ] GET `/api/v1/admin/reviews/reviews?sort_by=most_helpful`
- [ ] GET `/api/v1/admin/reviews/reviews/analytics` - Rating aggregation

**Expected**: Sorting works, helpful count, rating distribution

---

### 4. Maintenance Request APIs (Admin Maintenance)
- [ ] POST `/api/v1/admin/maintenance/requests` - Create request
- [ ] GET `/api/v1/admin/maintenance/requests` - List requests
- [ ] GET `/api/v1/admin/maintenance/requests/{id}` - Get specific
- [ ] PUT `/api/v1/admin/maintenance/requests/{id}` - Update
- [ ] DELETE `/api/v1/admin/maintenance/requests/{id}` - Delete
- [ ] GET `/api/v1/admin/maintenance/requests/stats/summary` - Stats

**Expected**: Categorization, priority, status, photo, cost estimation

---

### 5. Preventive Maintenance (Admin Preventive Maintenance)
- [ ] POST `/api/v1/admin/preventive-maintenance/preventive-maintenance/schedules`
- [ ] GET `/api/v1/admin/preventive-maintenance/preventive-maintenance/schedules`
- [ ] GET `/api/v1/admin/preventive-maintenance/preventive-maintenance/due`
- [ ] POST `/api/v1/admin/preventive-maintenance/preventive-maintenance/tasks`
- [ ] PUT `/api/v1/admin/preventive-maintenance/preventive-maintenance/tasks/{id}`

**Expected**: Recurring schedules, calendar, equipment tracking

---

### 6. Maintenance Cost Tracking (Admin Maintenance Costs)
- [ ] GET `/api/v1/admin/maintenance-costs/maintenance/costs`
- [ ] Filter by hostel_id, category, payment_status
- [ ] Filter by date range (start_date, end_date)

**Expected**: Budget allocation, vendor tracking, invoice URLs

---

### 7. Maintenance Task Assignment (Admin Maintenance Tasks)
- [ ] POST `/api/v1/admin/maintenance/tasks` - Assign task
- [ ] GET `/api/v1/admin/maintenance/tasks` - List tasks
- [ ] GET `/api/v1/admin/maintenance/tasks/{id}` - Get task
- [ ] PUT `/api/v1/admin/maintenance/tasks/{id}/progress` - Update
- [ ] PUT `/api/v1/admin/maintenance/tasks/{id}/verify` - Verify (quality 1-5)
- [ ] PUT `/api/v1/admin/maintenance/tasks/{id}/reassign` - Reassign
- [ ] DELETE `/api/v1/admin/maintenance/tasks/{id}` - Delete

**Expected**: Staff assignment, progress tracking, quality checks

---

### 8. Approval Workflow (Admin Maintenance Approvals)
- [ ] GET `/api/v1/admin/maintenance/approvals/threshold` - Get threshold
- [ ] GET `/api/v1/admin/maintenance/approvals/pending` - Pending approvals
- [ ] POST `/api/v1/admin/maintenance/approvals/submit` - Submit (supervisor)
- [ ] PUT `/api/v1/admin/maintenance/approvals/{id}/approve` - Approve (admin)
- [ ] PUT `/api/v1/admin/maintenance/approvals/{id}/reject` - Reject (admin)
- [ ] GET `/api/v1/admin/maintenance/approvals/history` - History
- [ ] GET `/api/v1/admin/maintenance/approvals/stats` - Statistics

**Expected**: $5000 threshold, supervisor → admin workflow

---

### 9. Leave Application Management (Admin Leave)
- [ ] GET `/api/v1/admin/leave/leave/requests` - Get leave requests
- [ ] PUT `/api/v1/admin/leave/leave/requests/{id}/status` - Update status

**Expected**: Student requests, supervisor approval, filtering

---

## 🔄 Complete Workflow Test

### Maintenance Workflow (End-to-End)
1. [ ] Create maintenance request (cost $6000)
2. [ ] Submit for approval (supervisor)
3. [ ] Approve request (admin)
4. [ ] Assign task to staff
5. [ ] Update task progress
6. [ ] Complete task
7. [ ] Verify with quality rating
8. [ ] Check statistics

### Review Workflow (End-to-End)
1. [ ] Student submits review (rating 4, text)
2. [ ] Admin sees pending review
3. [ ] Admin approves review
4. [ ] Another student marks as helpful
5. [ ] Check analytics (avg rating, distribution)

---

## 🎯 Expected Results

### Swagger UI Should Show:
- ✅ **Student Reviews** tag (6 endpoints)
- ✅ **Admin Reviews** tag (6 endpoints)
- ✅ **Admin Maintenance** tag (6 endpoints)
- ✅ **Admin Maintenance Tasks** tag (7 endpoints)
- ✅ **Admin Maintenance Approvals** tag (7 endpoints)
- ✅ **Admin Preventive Maintenance** tag (5 endpoints)
- ✅ **Admin Maintenance Costs** tag (1 endpoint)
- ✅ **Admin Leave** tag (2 endpoints)

**Total**: 40+ endpoints across 8 tag groups

---

## 🐛 Common Issues to Check

- [ ] Database tables exist (run migrations if needed)
- [ ] Authentication working (JWT tokens)
- [ ] Role-based access (ADMIN, SUPERADMIN roles)
- [ ] Foreign key relationships (hostel_id, user_id)
- [ ] Enum values match (status, priority, category)

---

## ✅ Success Criteria

All features are working if:
1. ✅ All endpoints appear in Swagger UI
2. ✅ No 500 errors when calling endpoints
3. ✅ Authentication/authorization works
4. ✅ Data is saved to database
5. ✅ Filtering and sorting work correctly
6. ✅ Statistics/analytics return correct data
