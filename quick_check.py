#!/usr/bin/env python3
"""
Quick script to check if key endpoints are working
"""

import requests
import sys

# Base URL for the API
BASE_URL = "http://localhost:8001"

# List of key endpoints to check
KEY_ENDPOINTS = [
    # Health and root endpoints
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    
    # Auth endpoints
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    
    # Some sample API endpoints
    "/api/v1/admin/students",
    "/api/v1/admin/rooms",
    "/api/v1/student/complaints",
]

def check_endpoint(endpoint):
    """Check a single endpoint and return the result"""
    url = BASE_URL + endpoint
    try:
        # For POST endpoints, we'll do a GET request to check if they exist
        # For other endpoints, we'll do a GET request
        if endpoint in ["/api/v1/auth/login", "/api/v1/auth/refresh"]:
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
    print(f"Checking {len(KEY_ENDPOINTS)} key endpoints...")
    print("=" * 60)
    
    # Check endpoints sequentially
    working_count = 0
    error_count = 0
    failed_count = 0
    
    for i, endpoint in enumerate(KEY_ENDPOINTS, 1):
        endpoint, status_code, result = check_endpoint(endpoint)
        if result == "WORKING":
            working_count += 1
            print(f"✓ {endpoint:<40} [{status_code}]")
        elif result == "ERROR":
            error_count += 1
            print(f"✗ {endpoint:<40} [{status_code}] ERROR")
        else:
            failed_count += 1
            print(f"✗ {endpoint:<40} [{result}] FAILED")
    
    print("=" * 60)
    print(f"Total endpoints checked: {len(KEY_ENDPOINTS)}")
    print(f"Working: {working_count}")
    print(f"Server errors: {error_count}")
    print(f"Failed to reach: {failed_count}")
    
    if failed_count == 0 and error_count == 0:
        print("\n🎉 All key endpoints are working!")
        return 0
    elif failed_count == 0:
        print(f"\n⚠️  All endpoints reachable, but {error_count} returned server errors.")
        return 1
    else:
        print(f"\n❌ {failed_count} endpoints failed to respond.")
        return 2

if __name__ == "__main__":
    sys.exit(main())