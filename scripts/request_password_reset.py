"""Trigger a password-reset request from the command line using the app's service.

Usage (PowerShell):

$env:PYTHONPATH = (Get-Location).Path
python scripts/request_password_reset.py --to user@example.com

This script is read-only for the DB (it creates a PasswordResetToken record).
It expects your `.env` to be configured (DB and optionally SMTP) and will use
the project's normal services.
"""
import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path so we can import app package
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal
from app.services.password_reset_service import PasswordResetService


def main():
    parser = argparse.ArgumentParser(description="Request password reset for an email or phone")
    parser.add_argument("--to", required=True, help="Email address or phone number to send reset to")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        svc = PasswordResetService(db)
        result = svc.create_reset_request(args.to)
        print("Result:")
        print(result)
        # If DEBUG and email configured the service will log the reset URL to app logs
    except Exception as e:
        print("Error while creating reset request:", str(e))
    finally:
        db.close()


if __name__ == '__main__':
    main()
