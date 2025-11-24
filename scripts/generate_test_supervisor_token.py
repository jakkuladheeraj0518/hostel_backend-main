"""Generate a test supervisor user and print an access token.

Usage:
  python scripts/generate_test_supervisor_token.py

This will:
 - Look for a user with email `test.supervisor@example.com`.
 - Create the user (role=supervisor) if missing.
 - Ensure the user is active.
 - Print a valid access token and a curl example to call the audit endpoint.
"""
from app.core.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import create_access_token


DEFAULT_EMAIL = "test.supervisor@example.com"
DEFAULT_USERNAME = "test_supervisor"
DEFAULT_PASSWORD = "Password123!"


def main():
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        user = repo.get_by_email(DEFAULT_EMAIL)
        if not user:
            print("Creating test supervisor user...")
            user_in = UserCreate(
                email=DEFAULT_EMAIL,
                username=DEFAULT_USERNAME,
                password=DEFAULT_PASSWORD,
                role="supervisor",
                full_name="Test Supervisor",
                hostel_id=1,
            )
            user = repo.create(user_in)
        else:
            print(f"Found existing user id={user.id} email={user.email}")

        # Ensure user is active
        if not user.is_active:
            print("Activating user...")
            updated = repo.update(user.id, UserUpdate(is_active=True))
            user = updated

        # Build token payload
        payload = {
            "sub": str(user.id),
            "role": user.role,
            "hostel_id": user.hostel_id,
            "email": user.email,
        }

        token = create_access_token(payload)

        print("\nACCESS TOKEN:\n")
        print(token)

        print("\nSample curl (Windows cmd.exe):\n")
        print(
            f'curl -X POST "http://127.0.0.1:8000/api/v1/supervisor/audit/logs" ^\n'
            f'  -H "accept: application/json" ^\n'
            f'  -H "Authorization: Bearer {token}" ^\n'
            f'  -H "Content-Type: application/json" ^\n'
            f'  -d "{{"action":"LOGIN_SUCCESS","resource":"SUPERVISOR","hostel_id":{user.hostel_id or 1},"ip_address":"172.20.10.11","user_agent":"Mozilla/5.0","details":"Supervisor logged in successfully"}}"'
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()
