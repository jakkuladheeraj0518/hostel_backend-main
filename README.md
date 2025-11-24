# Hostel Backend

**Project**: Hostel Backend

**Purpose**: FastAPI backend for hostel management (auth, bookings, payments, permissions).

**Quick Start (dev)**:

-   Create and activate a Python virtualenv (Windows PowerShell):
    
    -   conda create --prefix ./venv python=3.10 -y
    -   conda activate ./venv
-   Install dependencies:
    
    -   `pip install -r requirements.txt``- pip install -r requirements.txt`
        
    -   python -m scripts.create_super_admin
        
    -   python -m scripts.seed_all
        
    -   python -m uvicorn app.main:app --reload
        
-   Create an `.env` file in the project root with at minimum:
    
    -   `DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname`
    -   `SECRET_KEY=replace-with-a-long-random-string`
    -   Optional email settings: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PASS`, `EMAIL_FROM`
-   Run the app (development):
    
    -   `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

**Dev helper scripts**:

-   `scripts/seed_permissions.py` — populate `permissions` table (run once after DB is ready).
    
-   `scripts/create_super_admin.py` — create/promote a superadmin user.
    
-   `scripts/send_test_email.py` — preview and optionally send an email (requires email settings).
    

**Migrations (Alembic)**:

1.  I added a minimal `alembic.ini` and `alembic/env.py` that reference your app metadata.
    
2.  To autogenerate the initial migration and apply it (after `DATABASE_URL` is set in `.env`):
    
    -   `alembic revision --autogenerate -m "initial"`
        
    -   `alembic upgrade head`
        

Note: Alembic uses `app.core.database.Base.metadata` as the target metadata. If you keep the project layout, the provided `env.py` will import it.

**Auth & Passwords**:

-   Passwords are hashed with a safe bcrypt wrapper that pre-hashes inputs longer than 72 bytes.
    
-   JWTs are created with the `SECRET_KEY` and `ALGORITHM` from `app.config.get_settings()`.
    

**Troubleshooting**:

-   If you get 401 on protected endpoints, ensure you send `Authorization: Bearer <access_token>` header and the token is valid (not expired).
    
-   If emails are not sent, verify the email settings in `.env` and then run `python scripts/send_test_email.py --send`.
    

If you'd like, I can also generate and apply an initial migration here (I will need DB access or you can run the final `alembic` commands locally).