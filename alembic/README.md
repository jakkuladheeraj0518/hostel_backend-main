# Alembic Migrations

Alembic migration files for this project live in `alembic/versions`.

Usage (development):

- Ensure `DATABASE_URL` is set in your environment or `.env` and that
  `app.config.get_settings()` reads it.

- From the project root, using the project's venv, run:

```powershell
# create migration
\.venv\Scripts\python.exe -m alembic -c alembic.ini revision --autogenerate -m "initial"
# apply migrations
\.venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head
```

Notes:

- `alembic/env.py` is configured to import `app.core.database.Base` as
  `target_metadata` so autogenerate will detect models.

- If autogenerate can't import your settings, ensure `PYTHONPATH` or
  `prepend_sys_path` in `alembic.ini` points to the project root.

Alembic migration files for this project live in `alembic/versions`.

Usage (development):

- Ensure `DATABASE_URL` is set in your environment or `.env` and that `app.config.get_settings()` reads it.

- From the project root, using the project's venv, run:

```powershell
# create migration
\.venv\Scripts\python.exe -m alembic -c alembic.ini revision --autogenerate -m "initial"
# apply migrations
\.venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head
```

Notes:

- `alembic/env.py` is configured to import `app.core.database.Base` as `target_metadata` so autogenerate will detect models.

- If autogenerate can't import your settings, ensure `PYTHONPATH` or `prepend_sys_path` in `alembic.ini` points to the project root.

Alembic migration files for this project live in `alembic/versions`.

Usage (development):

- Ensure `DATABASE_URL` is set in your environment or `.env` and that
`app.config.get_settings()` reads it.

- From the project root, using the project's venv, run:

```powershell
# create migration
\.venv\Scripts\python.exe -m alembic -c alembic.ini revision --autogenerate -m "initial"
# apply migrations
\.venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head
```

Notes:

 `alembic/env.py` is configured to import `app.core.database.Base` as
`target_metadata` so autogenerate will detect models.

 If autogenerate can't import your settings, ensure `PYTHONPATH` or
`prepend_sys_path` in `alembic.ini` points to the project root.

Usage (development):
 Ensure `DATABASE_URL` is set in your environment or `.env` and that
`app.config.get_settings()` reads it.
 From project root, using the project's venv:

```powershell
# create migration
\.venv\Scripts\python.exe -m alembic -c alembic.ini revision --autogenerate -m "initial"
# apply migrations
\.venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head
```

Notes:
`alembic/env.py` is configured to import `app.core.database.Base` as `target_metadata` so autogenerate will detect models.
 If autogenerate can't import your settings, ensure `PYTHONPATH` or `prepend_sys_path` in `alembic.ini` points to the project root.
