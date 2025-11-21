"""
Create the PostgreSQL database defined in settings.DATABASE_URL if it does not exist.

Run:
    python -m scripts.create_database
"""

import psycopg2
from sqlalchemy.engine.url import make_url

from app.config import settings


def create_database_if_not_exists():
    # Parse the DATABASE_URL from settings
    url = make_url(settings.DATABASE_URL)

    dbname = url.database         # e.g. "hostelB"
    user = url.username           # e.g. "postgres"
    password = url.password
    host = url.host or "localhost"
    port = url.port or 5432

    print(f"🔍 Target database name from DATABASE_URL: {dbname}")

    # Connect to the default 'postgres' database on the same server
    conn = psycopg2.connect(
        dbname="postgres",
        user=user,
        password=password,
        host=host,
        port=port,
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Check if the database already exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
    exists = cur.fetchone()

    if exists:
        print(f"✅ Database '{dbname}' already exists, nothing to do.")
    else:
        # Create the database
        cur.execute(f'CREATE DATABASE "{dbname}"')
        print(f"🎉 Database '{dbname}' has been created.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    create_database_if_not_exists()