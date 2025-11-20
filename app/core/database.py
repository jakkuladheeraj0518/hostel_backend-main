"""Compatibility shim for database objects.

This module re-exports the engine, SessionLocal, Base, and helper
functions from `app.config` so the rest of the codebase can continue
to import from `app.core.database` while sharing a single Declarative
Base and engine used by the models.
"""

from app.config import engine, SessionLocal, Base, get_db, init_db  # re-export

__all__ = ["engine", "SessionLocal", "Base", "get_db", "init_db"]
