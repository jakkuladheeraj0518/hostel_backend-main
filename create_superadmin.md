# Create Super Admin

This document explains how to create a Super Administrator account for the
Hostel Management API. The repository includes utility scripts to create an
idempotent Super Admin user for development or initial deployment.

## Purpose

- Quickly bootstrap a Super Admin account for local development or initial
  deployment.
- The script is idempotent: running it multiple times will not create duplicate
  accounts if an account with the same email or username already exists.

## Prerequisites

- A working Python environment (the project uses the same environment as the
  app).
- The project's dependencies installed (see `requirements.txt` or
  `pyproject.toml`).
- A reachable database and correct environment variables (e.g. `DATABASE_URL`).
- The project root set as the current working directory when running the
  scripts.

## Script location

`scripts/create_super_admin.py`

This script accepts CLI options for email, phone, username, password, and full
name.

## Recommended usage (PowerShell)

Run from the project root (Windows PowerShell):

```powershell
python -m scripts.create_super_admin `
  '--email' 'you@example.com' `
  '--phone' '9876543210' `
  '--username' 'superadmin' `
  '--password' 'Admin@123' `
  '--full-name' 'Super Admin'
```

Notes:

- Use a secure password in production; the example password is for local/dev
  convenience only.
- If your DB requires environment variables (e.g., `DATABASE_URL`), ensure
  those are set in your shell before running the script.

## Verify the user

- After the script completes you can verify the Super Admin exists by querying
  the database (users table) or by authenticating using the API login endpoint.

Example (login via API):

1. POST to `/api/v1/auth/login` with email/username and password (or
   `email_or_phone` as supported).
2. If successful you'll receive access and refresh tokens. Use them to call
   protected endpoints (SuperAdmin-only routes).

## Troubleshooting

- "Database connection" errors: check your env vars and that the DB server is
  reachable.
- "User already exists" behavior: the script is idempotent — it will not fail
  if a user with the same email/username exists; it will print a message and
  keep the existing user.
- If you changed the User model, ensure Alembic migrations are applied:

```powershell
alembic -c alembic.ini upgrade head
```

## Security

- Do not store plaintext credentials in source control.
- Remove or protect development accounts in production.

## Automation

- You can run the script as part of deployment automation to ensure a Super
  Admin account exists.

---
