# Step-by-Step Integration Guide

## Overview
This guide will help you integrate the supervisor module from server.zip into your hostel_backend-main project.

## Prerequisites
- ✅ server.zip extracted to `temp_server_extract/`
- ✅ Backup of existing code
- ✅ Python environment activated

## Phase 1: Add Missing Models

### Step 1.1: Create Attendance Model

**File:** `app/models/attendance.py`

Copy the attendance model from server.zip and adapt it to your project structure.

### Step 1.2: Extend Leave Model

**File:** `app/models/leave.py`

Add missing fields like `leave_type`, `emergency_contact`, `approved_by`, etc.

### Step 1.3: Add Missing Enums

Check if you need to add enums for `AttendanceStatus`, `LeaveStatus`, etc.

## Phase 2: Implement Dashboard Endpoints

### Step 2.1: Create Dashboard File

**File:** `app/api/v1/supervisor/dashboard.py`

Copy dashboard logic from `temp_server_extract/server/app/api/v1/supervisor.py`

### Step 2.2: Adapt to Your Models

Update field names to match your existing models (e.g., `complaint_title` → `title`)

## Phase 3: Implement Attendance Endpoints

### Step 3.1: Create Attendance File

**File:** `app/api/v1/supervisor/attendance.py`

Copy attendance logic from server.zip

### Step 3.2: Create Attendance Schemas

**File:** `app/schemas/attendance.py`

Add request/response schemas for attendance operations

## Phase 4: Enhance Complaint Handling

### Step 4.1: Add Role-Based Assignment

Update `app/api/v1/supervisor/complaints.py` to support role-based assignment

## Phase 5: Add Leave Management

### Step 5.1: Create Leave Endpoints

**File:** `app/api/v1/supervisor/leave.py`

Implement approve/reject endpoints

## Phase 6: Add Test Data

### Step 6.1: Create Seed Script

**File:** `scripts/seed_supervisor_data.py`

Add supervisors, students, complaints, attendance records

## Phase 7: Test Everything

Run tests and verify all endpoints work correctly.

---

**Ready to start?** Let me know which phase you'd like to begin with!
