# Create Super Admin

This document describes how to create (or ensure) a Super Administrator account
for the Hostel Management backend. It documents the existing helper script
`scripts/create_super_admin.py` and shows safe ways to run or customize it.

## Purpose

- Quickly bootstrap a Super Admin account for local development or initial
  deployment.
- The shipped script is idempotent: if a Super Admin with the configured
  email already exists, the script will upgrade that user to the Super Admin
  role (and enable/verify the account) instead of creating a duplicate.

## Where the script lives

`scripts/create_super_admin.py`

The script is a simple standalone script that uses the repository's application
code (database, repositories, services) to perform the operation. It contains
hard-coded default credentials inside the file; to customize values either edit
the file or use the alternative snippets below.

## Prerequisites

- Python 3.11+ recommended (works on 3.10 for most dependencies).
- Project dependencies installed. From project root (PowerShell):

```powershell
python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- Database reachable and `DATABASE_URL` (or other environment variables used by
  your `app.config.Settings`) set in your shell or `.env` file.
- Apply database migrations first if necessary:

```powershell
alembic -c alembic.ini upgrade head
```

## Run the provided script (simple)


From the project root run:

```powershell
python scripts/create_super_admin.py
```

Behavior:

- If a user with the default script email exists the script will upgrade that
  user to Super Admin (set role, mark active and verified) and exit.
- If no user exists it will create a default `Hostel` row if none exists
  (the project models require a hostel record for user creation), then create
  a new user with the defaults bundled in the script.

The script prints the email/username/password it used. Change those defaults
before running in production.

## Customize the defaults

1) Quick and explicit: edit `scripts/create_super_admin.py` and change the
   `SUPERADMIN_*` constants at the top.

2) Safer programmatic approach: create a small one-off script that calls the
   repository/service to create a user with your chosen values. Example (run
   from project root while your virtualenv is active):

```powershell
python - <<'PY'
from app.core.database import SessionLocal
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from app.core.roles import Role

db = SessionLocal()
try:
    svc = AuthService(db)
    user_create = UserCreate(
        email="admin@example.com",
        phone_number="9876543210",
        username="superadmin",
        password="Secur3P@ssw0rd",
        full_name="Super Admin",
        role=Role.SUPERADMIN.value,
    )
    created = svc.user_repo.create(user_create)
    created.is_active = True
    created.is_email_verified = True
    created.is_phone_verified = True
    db.commit()
    print('Created:', created.email)
finally:
    db.close()
PY
```

This lets you supply secure credentials without editing repository files or
committing secrets to source control.

## Verify the created user

- Inspect the database `users` table using your preferred SQL client.
- Or call the API login endpoint (e.g., POST `/api/v1/auth/login`) with the
  created credentials to obtain tokens.

## Troubleshooting

- "Database connection" errors: confirm `DATABASE_URL` and that the DB server
  is reachable from your environment.
- "Import" errors when running the script: ensure you're running the script
  from the project root with the virtualenv activated so Python finds the
  `app` package.
- If you changed models and see constraint errors, ensure migrations are
  current and the database schema matches the models.

## Security notes

- Do not commit production credentials to source control.
- Rotate default passwords used for initial bootstrapping.
- Remove or secure development accounts on production systems.

## Automation

- You can include this script in deployment workflows, CI pipelines, or as
  a post-deploy task, but prefer a secure, parameterized approach rather than
  relying on hard-coded credentials.

---

If you'd like, I can:

- update `scripts/create_super_admin.py` to accept CLI flags (email/username/etc.)
- or create a safe helper that reads values from environment variables.
  Tell me which option you prefer and I will implement it.
