# app/utils.py
from __future__ import annotations
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Type, TypeVar, Union
from contextlib import contextmanager
from functools import wraps
from datetime import datetime, date, time
import csv
import io
import os
import tempfile

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

T = TypeVar("T")

# -------------------------
# Database / transaction helpers
# -------------------------
def safe_commit(db: Session) -> None:
    """
    Try to commit the session; rollback on error and re-raise.
    Use this for short single-commit operations.
    """
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


@contextmanager
def db_transaction(db: Session):
    """
    Context manager for explicit transactions:
        with db_transaction(db):
            ... multiple repo operations ...
    Will rollback automatically on exception.
    """
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise


def get_or_create(db: Session, model: Type[T], defaults: Optional[Dict[str, Any]] = None, **kwargs) -> Tuple[T, bool]:
    """
    Try to get an instance matching kwargs, otherwise create with defaults merged.
    Returns (instance, created_bool).
    Note: not atomic across processes (no DB lock) but fine for many use-cases.
    """
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    params = dict(kwargs)
    if defaults:
        params.update(defaults)
    instance = model(**params)
    db.add(instance)
    try:
        db.commit()
        db.refresh(instance)
        return instance, True
    except IntegrityError:
        db.rollback()
        # another thread/process created simultaneously — try to fetch again
        instance = db.query(model).filter_by(**kwargs).first()
        if instance:
            return instance, False
        raise


def retry_on_exception(retries: int = 3, exceptions: Tuple[Type[BaseException], ...] = (SQLAlchemyError,)):
    """
    Decorator to retry a function on transient exceptions (useful for flaky DB calls).
    """
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(retries):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
            # no more retries
            raise last_exc
        return wrapper
    return decorator


# -------------------------
# Enum & conversion helpers
# -------------------------
def safe_enum_cast(enum_cls: Type[Enum], value: Any, fallback: Optional[Any] = None):
    """
    Convert a DB/stored string or enum to the enum_cls if possible, otherwise fallback.
    Example: safe_enum_cast(RoomType, "single")
    """
    if value is None:
        return fallback
    try:
        if isinstance(value, enum_cls):
            return value
        return enum_cls(value)
    except Exception:
        return fallback


# -------------------------
# Pagination helpers
# -------------------------
def paginate_list(items: Sequence[T], skip: int = 0, limit: int = 100) -> List[T]:
    if skip < 0:
        skip = 0
    if limit <= 0:
        limit = 100
    return list(items)[skip : skip + limit]


def make_pagination_response(items: Sequence[T], skip: int, limit: int, total: Optional[int] = None) -> Dict[str, Any]:
    return {
        "skip": skip,
        "limit": limit,
        "count": len(items),
        "total": total if total is not None else None,
        "items": items,
    }


# -------------------------
# Model <-> dict / schema helpers
# -------------------------
def model_to_dict(obj: Any, include: Optional[Iterable[str]] = None, exclude: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """
    Convert a SQLAlchemy model instance to dict using attribute access.
    Avoids importing SQLAlchemy internals; assumes simple scalar/enum/date attributes.
    """
    data: Dict[str, Any] = {}
    exclude = set(exclude or [])
    include = set(include) if include is not None else None

    for attr in getattr(obj, "__table__", obj.__class__).__dict__.keys() if hasattr(obj, "__table__") else vars(obj).keys():
        # fallback: iterate public attributes
        pass  # we'll use attributes list below

    # safer: iterate __dict__ for normal attributes, and fallback to dir for properties
    for k in vars(obj).keys():
        if k.startswith("_"):
            continue
        if include is not None and k not in include:
            continue
        if k in exclude:
            continue
        try:
            val = getattr(obj, k)
            # convert datetime/date to isoformat for JSON friendliness
            if isinstance(val, datetime):
                val = val.isoformat()
            elif isinstance(val, date):
                val = val.isoformat()
            data[k] = val
        except Exception:
            continue
    return data


def apply_updates_from_schema(instance: Any, schema_obj: Any, exclude: Optional[Iterable[str]] = None) -> Any:
    """
    Apply attributes from a Pydantic schema (or dict-like) to a SQLAlchemy model instance.
    Only sets attributes present in schema_obj (use .dict(exclude_unset=True) before passing if needed).
    Returns the instance (convenience).
    """
    exclude = set(exclude or [])
    if hasattr(schema_obj, "dict"):
        payload = schema_obj.dict(exclude_unset=True)
    elif isinstance(schema_obj, dict):
        payload = schema_obj
    else:
        # fallback: try to iterate attributes
        payload = {k: getattr(schema_obj, k) for k in dir(schema_obj) if not k.startswith("_")}
    for k, v in payload.items():
        if k in exclude:
            continue
        if hasattr(instance, k):
            setattr(instance, k, v)
    return instance


# -------------------------
# Amenities parsing utilities
# -------------------------
def split_amenities(raw: Optional[str]) -> List[str]:
    """
    Convert a comma-separated amenities string into cleaned list of names.
    """
    if not raw:
        return []
    parts = [p.strip() for p in raw.split(",")]
    return [p for p in parts if p]


def merge_amenities(items: Iterable[str]) -> str:
    """
    Merge an iterable of amenities into a comma-separated canonical string.
    """
    cleaned = [i.strip() for i in items if i and i.strip()]
    # drop duplicates while preserving order
    seen = set()
    out = []
    for a in cleaned:
        if a.lower() not in seen:
            seen.add(a.lower())
            out.append(a)
    return ", ".join(out)


# -------------------------
# CSV import/export helpers (rooms / beds / students)
# -------------------------
def csv_to_dicts(csv_bytes: Union[bytes, str], delimiter: str = ",") -> List[Dict[str, str]]:
    """
    Parse CSV bytes/string to list of row dicts using first row as header.
    Useful for simple bulk imports (rooms/beds/students).
    """
    if isinstance(csv_bytes, bytes):
        csv_str = csv_bytes.decode("utf-8")
    else:
        csv_str = csv_bytes
    f = io.StringIO(csv_str)
    reader = csv.DictReader(f, delimiter=delimiter)
    return [dict(row) for row in reader]


def dicts_to_csv(rows: Iterable[Dict[str, Any]], fieldnames: Optional[List[str]] = None) -> str:
    """
    Convert an iterable of dicts to CSV string. If fieldnames not provided, use keys from first row.
    """
    rows = list(rows)
    if not rows:
        return ""
    if fieldnames is None:
        # preserve insertion order of keys from first dict
        fieldnames = list(rows[0].keys())
    f = io.StringIO()
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        # ensure values are simple types
        writer.writerow({k: (v if v is not None else "") for k, v in r.items()})
    return f.getvalue()


# -------------------------
# File helpers for student documents
# -------------------------
STUDENT_DOCS_DIR = os.getenv("STUDENT_DOCS_DIR", os.path.join(tempfile.gettempdir(), "student_docs"))

def ensure_student_docs_dir():
    os.makedirs(STUDENT_DOCS_DIR, exist_ok=True)


def save_student_document(student_id: str, filename: str, content: bytes) -> str:
    """
    Save a student document to STUDENT_DOCS_DIR/<student_id>/<filename>
    Returns the relative file path.
    """
    ensure_student_docs_dir()
    student_dir = os.path.join(STUDENT_DOCS_DIR, student_id)
    os.makedirs(student_dir, exist_ok=True)
    safe_name = filename.replace("/", "_").replace("\\", "_")
    path = os.path.join(student_dir, safe_name)
    with open(path, "wb") as f:
        f.write(content)
    return path


def remove_student_document(path: str) -> bool:
    try:
        os.remove(path)
        return True
    except FileNotFoundError:
        return False


# -------------------------
# Small helpers used by services
# -------------------------
def calculate_pricing_stats(prices: Iterable[Optional[float]]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Accepts an iterable of numbers / None and returns (min, avg, max) or (None, None, None)
    if no valid numbers present.
    """
    vals = [float(v) for v in prices if v is not None]
    if not vals:
        return None, None, None
    mn = min(vals)
    mx = max(vals)
    avg = sum(vals) / len(vals)
    return mn, avg, mx


def coerce_date(val: Any) -> Optional[date]:
    """
    Try to coerce common inputs into a date object; return None when not possible.
    Accepts date, datetime, ISO string.
    """
    if val is None:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(val, fmt).date()
            except Exception:
                continue
    return None


def coerce_time(val: Any) -> Optional[time]:
    """
    Try to coerce to time object.
    """
    if val is None:
        return None
    if isinstance(val, time):
        return val
    if isinstance(val, datetime):
        return val.time()
    if isinstance(val, str):
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(val, fmt).time()
            except Exception:
                continue
    return None


# -------------------------
# Validation helpers
# -------------------------
def validate_hostel_ids(hostel_ids: Sequence[str], max_items: int = 4) -> None:
    if not hostel_ids:
        raise ValueError("Provide at least one hostel id")
    if len(hostel_ids) > max_items:
        raise ValueError(f"You can compare up to {max_items} hostels")


# -------------------------
# Lightweight notification/email stub (replace with real service)
# -------------------------
def notify_supervisor_assignment(supervisor_email: str, hostel_id: str) -> None:
    """
    Stub for notifying a supervisor — replace with real mailer or messaging.
    """
    # Keep this a no-op in tests; log or hook into actual email sender in production.
    print(f"[notify] would send email to {supervisor_email}: assigned to {hostel_id}")


# -------------------------
# Misc small helpers
# -------------------------
def safe_int(v: Any, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(v)
    except Exception:
        return default


def safe_float(v: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        return float(v)
    except Exception:
        return default
