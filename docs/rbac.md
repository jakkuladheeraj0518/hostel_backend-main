
# RBAC Design & Endpoint → Permission Mapping

 Date: 2025-11-20

 This document summarizes the roles and permissions in `app/core/permissions.py` and proposes an endpoint → permission mapping for `app/api/v1` routes discovered in a code scan. This is a proposal: please review and approve before I apply code changes.

## Roles (summary)

**SUPERADMIN**: full access (create/read/update/delete users, hostels, permissions, reporting, payments, etc.)
**ADMIN**: hostel-scoped manager (hostel config, supervisors, announcements, payments, limited reporting)
 **SUPERVISOR**: hostel-scoped operator (attendance, complaints, maintenance, audit viewing/creation)
**STUDENT**: tenant-level access (view own profile, view hostel announcements, initiate bookings, view payments)
**VISITOR**: public-facing actions (search, book, waitlist, registration)
 Key Permissions (from `app/core/permissions.py`)

**User management**: `create_user`, `read_user`, `update_user`, `delete_user`
**Hostel management**: `create_hostel`, `read_hostel`, `update_hostel`, `delete_hostel`
**Audit & reporting**: `view_audit`, `create_audit`, `export_audit`, `export_reports`
**Finance/subscriptions**: `manage_subscriptions`, `view_payments`, `manage_payments`
**Supervisor/hostel ops**: `manage_supervisors`, `manage_hostel_config`, `manage_attendance`, `manage_complaints`, `manage_maintenance`, `manage_announcements`
**Booking/registration**: `initiate_booking`, `create_registration`
**Permissions**: `manage_permissions`, `assign_role`

 Notes: a few granular permissions are recommended but not currently present (e.g. `manage_admins`, `assign_hostels`, `upload_profile_picture`, `create_complaint`). The mapping below re-uses existing permissions where practical and calls out where new fine-grained permissions are suggested.

## Proposed Endpoint → Required Permission (representative subset from scan)

### Auth (public)

POST `/api/v1/auth/forgot-password` → public (no permission required)
POST `/api/v1/auth/verify-reset-code` → public
POST `/api/v1/auth/reset-password` → public

### Admin / User management (`app/api/v1/admin/admins.py`)

POST `/api/v1/admin/admins` → `create_user` (or new `manage_admins`)
GET `/api/v1/admin/admins` → `read_user`
GET `/api/v1/admins/{admin_id}` → `read_user`
PUT `/api/v1/admins/{admin_id}` → `update_user`
DELETE `/api/v1/admins/{admin_id}` → `delete_user`
POST `/api/v1/admins/{admin_id}/profile-picture` → `update_user` (or suggested `upload_profile_picture`)
POST `/api/v1/admins/{admin_id}/assign-hostels` → `manage_hostel_config` (or suggested `assign_hostels`)

### Supervisor / Student management

POST `/api/v1/admin/supervisors` → `manage_supervisors`
PUT `/api/v1/admin/supervisors/{id}` → `manage_supervisors`
 DELETE `/api/v1/admin/supervisors/{id}` → `manage_supervisors`
 -POST `/api/v1/admin/students` → `create_registration` (or `create_user`)
PUT `/api/v1/admin/students/{id}` → `update_user`
DELETE `/api/v1/admin/students/{id}` → `delete_user` (note: currently restricted to SUPERADMIN in code; consider adding `delete_user` permission for Admin if intended)

### Supervisor area (`app/api/v1/supervisor/audit.py`)

 GT `/api/v1/supervisor/audit` → `view_audit`
 GET `/api/v1/supervisor/audit/users/{user_id}` → `view_audit` (scoped to supervisor's hostels)
  GET `/api/v1/supervisor/audit/target/{target_id}` → `view_audit`
  POST `/api/v1/supervisor/audit/logs` → `create_audit`

### Visitor (public-facing)

 -POST `/api/v1/visitor/bookings` → `initiate_booking` (visitor role / public)
 -PUT `/api/v1/visitor/bookings/{id}` → `initiate_booking` (owner/visitor-scoped)
 -DELETE `/api/v1/visitor/bookings/{id}` → `initiate_booking` or `delete_booking` (suggest explicit `delete_booking`)
  GET `/api/v1/visitor/booking_calendar/{hostel_id}` → public read
  POST `/api/v1/visitor/waitlist` → `create_registration` (visitor_required)
  GET `/api/v1/visitor/waitlist` → visitor-only read

### Student features (`app/api/v1/student/*`)

  GET `/api/v1/student/announcement` → `view_hostel_announcements` (students)
  POST `/api/v1/student/announcement/{id}/acknowledge` → `view_hostel_announcements` (or `acknowledge_announcement`)
  GET/POST/PUT `/api/v1/student/mess_menu` endpoints → `view_hostel_announcements` / `manage_hostel_config` depending on action (students reading menus vs staff updating)
  POST `/api/v1/student/complaints` → suggested `create_complaint` (or reuse `manage_complaints` for staff-only endpoints)
  GET `/api/v1/student/complaints` → `manage_complaints` for staff; `view_own_complaints` for students (suggest split)

## Super-admin reporting (`app/api/v1/super_admin/report.py`)

GET `/api/v1/super_admin/dashboard/multi-hostel` → `export_reports` or `view_audit`
Cross-hostel endpoints → `export_reports`
Attendance reports → `export_reports` or `view_audit`

## Recommendations & next steps

 1. Add a small set of granular permissions that are currently missing but used in mapping suggestions:
    - `manage_admins` (or reuse existing `create_user` + `assign_role`)
    - `assign_hostels` (or reuse `manage_hostel_config`)
    - `upload_profile_picture` (or map to `update_user`)
    - `create_complaint` and `delete_booking` (visitor/student-specific)
 2. Implement centralized scoping dependencies in `app/api/deps.py`:
    - `supervisor_scoped(hostel_id_param: str)` — denies access if a supervisor attempts to act outside their assigned hostels.
    - `admin_scoped(hostel_id_param: str)` — similar for Admins.
 3. Apply `permission_required(...)` per-endpoint using the mapping above. Use `role_required(...)` for coarse-grained routes (public vs authenticated).
 4. Add `docs/rbac.md` (this file) to the repo and review with business owners to finalize permission names.

## What I can do next (pick one)

Implement the new granular permissions in `app/core/permissions.py` and update the `PERMISSION_MATRIX` accordingly.
  Implement `supervisor_scoped` and `admin_scoped` dependencies in `app/api/deps.py` and apply them to `admin/admins.py` and `supervisor/audit.py`.
  Continue a full automated pass applying `permission_required(...)` to all scanned endpoints using the proposed mapping.

 If you'd like, I'll apply the approved mapping changes in small patches (one folder at a time) and run syntax checks + tests between patches.
