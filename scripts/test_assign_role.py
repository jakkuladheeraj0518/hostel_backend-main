"""Test assign-role endpoint helper.

Usage (PowerShell):
    $env:API_URL='http://127.0.0.1:8000'
    $env:SA_EMAIL='admin@example.com'  # or SA_PHONE
    $env:SA_PASSWORD='secret'
    python .\scripts\test_assign_role.py --user-id 3 --role admin

The script will:
 - log in to /api/v1/auth/login
 - decode and print the access token payload
 - call /api/v1/auth/assign-role with the access token
"""
import os
import sys
import argparse
import json
import base64
from typing import Optional

import requests

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")


def decode_jwt_no_verify(token: str) -> Optional[dict]:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        # pad
        payload_b64 += '=' * (-len(payload_b64) % 4)
        decoded = base64.urlsafe_b64decode(payload_b64.encode())
        return json.loads(decoded)
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', help='superadmin email (or set SA_EMAIL env var)')
    parser.add_argument('--phone', help='superadmin phone (or set SA_PHONE env var)')
    parser.add_argument('--password', help='superadmin password (or set SA_PASSWORD env var)')
    parser.add_argument('--user-id', type=int, required=True, help='ID of user to assign role to')
    parser.add_argument('--role', required=True, help='Role to assign (e.g. admin)')
    args = parser.parse_args()

    email = args.email or os.environ.get('SA_EMAIL')
    phone = args.phone or os.environ.get('SA_PHONE')
    password = args.password or os.environ.get('SA_PASSWORD')
    if not password or (not email and not phone):
        print('Missing superadmin credentials. Provide --email/--phone and --password or set SA_EMAIL/SA_PHONE and SA_PASSWORD')
        sys.exit(1)

    # Login
    login_url = f"{API_URL}/api/v1/auth/login"
    login_json = {"password": password}
    if email:
        login_json["email"] = email
    else:
        login_json["phone"] = phone
    resp = requests.post(login_url, json=login_json)
    if resp.status_code != 200:
        print('Login failed:', resp.status_code, resp.text)
        sys.exit(1)

    data = resp.json()
    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')
    print('Login successful. Access token length:', len(access_token) if access_token else 0)

    # Decode payload
    payload = decode_jwt_no_verify(access_token) if access_token else None
    print('\nAccess token payload:')
    print(json.dumps(payload, indent=2))

    # Call assign-role
    assign_url = f"{API_URL}/api/v1/auth/assign-role"
    headers = {'Authorization': f'Bearer {access_token}'}
    payload = {"user_id": args.user_id, "role": args.role}
    resp = requests.post(assign_url, json=payload, headers=headers)
    print('\nassign-role response:', resp.status_code)
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text)


if __name__ == '__main__':
    main()
