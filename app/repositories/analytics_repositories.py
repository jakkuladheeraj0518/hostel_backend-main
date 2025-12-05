from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
 
 
def get_hostel_occupancy_and_revenue(db: Session, hostel_id: int):
    """Try calling PostgreSQL stored procedure get_hostel_occupancy_and_revenue.
 
    If the function does not exist in the connected database (UndefinedFunction),
    fall back to a direct query that returns the latest occupancy and revenue
    for the given hostel. This prevents the ASGI app from crashing when the
    migration or function creation hasn't been applied.
    """
    query = text("SELECT * FROM get_hostel_occupancy_and_revenue(:hostel_id)")
    try:
        result = db.execute(query, {"hostel_id": hostel_id}).fetchall()
    except ProgrammingError:
        # The DB function likely doesn't exist. The failed execution leaves the
        # current transaction in an aborted state — roll back the session so we
        # can safely run the fallback query in a clean transaction.
        try:
            db.rollback()
        except Exception:
            # If rollback itself fails, ignore and attempt fallback (caller will
            # see any remaining DB errors). We don't want to mask the original
            # error details here.
            pass
 
        # Fallback to a direct query.
        fallback_query = text(
            """
            SELECT o.occupancy_rate, r.revenue, h.hostel_name
            FROM hostels h
            LEFT JOIN (
                SELECT occupancy_rate, hostel_id
                FROM occupancies
                WHERE hostel_id = :hostel_id
                ORDER BY month DESC
                LIMIT 1
            ) o ON h.id = o.hostel_id
            LEFT JOIN (
                SELECT revenue, hostel_id
                FROM revenues
                WHERE hostel_id = :hostel_id
                ORDER BY month DESC
                LIMIT 1
            ) r ON h.id = r.hostel_id
            WHERE h.id = :hostel_id
            """
        )
        result = db.execute(fallback_query, {"hostel_id": hostel_id}).fetchall()
 
    # Fetch hostel canonical values once to use as fallback when proc/fallback
    # returns NULLs.
    hostel_row = db.execute(
        text("SELECT hostel_name, current_occupancy, monthly_revenue FROM hostels WHERE id = :hostel_id"),
        {"hostel_id": hostel_id}
    ).fetchone()
 
    hostel_name = hostel_row[0] if hostel_row is not None else None
    hostel_current = hostel_row[1] if hostel_row is not None else None
    hostel_revenue = hostel_row[2] if hostel_row is not None else None
 
    # Convert to list of dictionaries for easy JSON serialization
    out = []
    for row in result:
        # Stored proc may return (occupancy, revenue) or (occupancy, revenue, hostel_name)
        occ = row[0] if len(row) > 0 else None
        rev = row[1] if len(row) > 1 else None
        name = row[2] if len(row) > 2 else None
 
        # Fill missing values from hostels table
        if occ is None:
            occ = hostel_current
        if rev is None:
            rev = hostel_revenue
        if not name:
            name = hostel_name
 
        out.append({
            "current_occupancy": occ,
            "monthly_revenue": rev,
            "hostel_name": name,
        })
 
    return out
 