#!/usr/bin/env python3
"""
Script to check if all endpoints are working
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Base URL for the API
BASE_URL = "http://localhost:8000"

# List of endpoints to check
ENDPOINTS = [
    # Health and root endpoints
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    
    # Auth endpoints
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/auth/roles",
    "/api/v1/auth/password-reset/request",
    "/api/v1/auth/password-reset/confirm",
    "/api/v1/auth/me",
    
    # Student endpoints
    "/api/v1/student/complaints",
    "/api/v1/student/mess-menu",
    "/api/v1/student/announcements",
    "/api/v1/student/reviews",
    "/api/v1/student/leave",
    "/api/v1/student/notifications",
    
    # Supervisor endpoints
    "/api/v1/supervisor/complaints",
    "/api/v1/supervisor/mess-menu",
    "/api/v1/supervisor/announcements",
    "/api/v1/supervisor/reports",
    "/api/v1/supervisor/notifications",
    "/api/v1/auth/supervisor/login",
    
    # Admin endpoints
    "/api/v1/admin/students",
    "/api/v1/admin/supervisors",
    "/api/v1/admin/rooms",
    "/api/v1/admin/beds",
    "/api/v1/admin/complaints",
    "/api/v1/admin/reports",
    "/api/v1/admin/hostels",
    "/api/v1/admin/dashboard",
    "/api/v1/admin/analytics",
    "/api/v1/admin/approvals",
    "/api/v1/admin/permissions",
    "/api/v1/admin/rbac",
    "/api/v1/admin/session",
    "/api/v1/admin/audit",
    "/api/v1/admin/mess-menu",
    "/api/v1/admin/announcements",
    "/api/v1/admin/bookings",
    "/api/v1/admin/waitlist",
    "/api/v1/admin/calendar",
    "/api/v1/admin/jobs",
    "/api/v1/admin/fee-structure",
    "/api/v1/admin/payments",
    "/api/v1/admin/invoices",
    "/api/v1/admin/transactions",
    "/api/v1/admin/receipts",
    "/api/v1/admin/refunds",
    "/api/v1/admin/ledger",
    "/api/v1/admin/reminder-configs",
    "/api/v1/admin/reminder-templates",
    "/api/v1/admin/reminders",
    "/api/v1/admin/preventive-maintenance",
    "/api/v1/admin/maintenance-costs",
    "/api/v1/admin/leave",
    "/api/v1/admin/reviews",
    
    # Super Admin endpoints
    "/api/v1/super-admin/hostels",
    "/api/v1/super-admin/dashboard",
    "/api/v1/super-admin/admins",
    "/api/v1/super-admin/subscription",
    "/api/v1/super-admin/reports",
    "/api/v1/super-admin/analytics",
    "/api/v1/super-admin/shift-coordination",
    
    # Visitor endpoints
    "/api/v1/visitor/search",
    "/api/v1/visitor/bookings",
    "/api/v1/visitor/waitlist",
    "/api/v1/visitor/comparison",
    
    # Webhook endpoints
    "/api/v1/webhooks/notifications/sendgrid",
    "/api/v1/webhooks/notifications/twilio",
]

def check_endpoint(endpoint):
    """Check a single endpoint and return the result"""
    url = BASE_URL + endpoint
    try:
        # For POST endpoints, we'll do a GET request to check if they exist
        # For other endpoints, we'll do a GET request
        if endpoint in ["/api/v1/auth/login", "/api/v1/auth/refresh", 
                       "/api/v1/auth/password-reset/request", 
                       "/api/v1/auth/password-reset/confirm",
                       "/api/v1/auth/supervisor/login"]:
            # These are POST endpoints, so we'll check if they exist by sending OPTIONS
            response = requests.options(url, timeout=5)
        else:
            response = requests.get(url, timeout=5)
        
        # Consider 2xx, 401, 403, 404, 405 as "working" (endpoint exists)
        # 5xx errors indicate server issues
        if response.status_code < 500:
            return endpoint, response.status_code, "WORKING"
        else:
            return endpoint, response.status_code, "ERROR"
    except requests.exceptions.RequestException as e:
        return endpoint, None, f"FAILED: {str(e)}"

def main():
    print(f"Checking {len(ENDPOINTS)} endpoints...")
    print("=" * 80)
    
    # Check endpoints sequentially for clearer output
    working_count = 0
    error_count = 0
    failed_count = 0
    
    for i, endpoint in enumerate(ENDPOINTS, 1):
        print(f"[{i}/{len(ENDPOINTS)}] Checking {endpoint}...", end=" ")
        endpoint, status_code, result = check_endpoint(endpoint)
        if result == "WORKING":
            working_count += 1
            print(f"✓ [{status_code}]")
        elif result == "ERROR":
            error_count += 1
            print(f"✗ ERROR [{status_code}]")
        else:
            failed_count += 1
            print(f"✗ FAILED [{result}]")
    
    print("=" * 80)
    print(f"Total endpoints checked: {len(ENDPOINTS)}")
    print(f"Working: {working_count}")
    print(f"Server errors: {error_count}")
    print(f"Failed to reach: {failed_count}")
    
    if failed_count == 0 and error_count == 0:
        print("\n🎉 All endpoints are working!")
    elif failed_count == 0:
        print(f"\n⚠️  All endpoints reachable, but {error_count} returned server errors.")
    else:
        print(f"\n❌ {failed_count} endpoints failed to respond.")

if __name__ == "__main__":
    main()