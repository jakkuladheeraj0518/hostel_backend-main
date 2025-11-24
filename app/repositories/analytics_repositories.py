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
            SELECT o.occupancy_rate, r.revenue
            FROM (
                SELECT occupancy_rate, hostel_id
                FROM occupancies
                WHERE hostel_id = :hostel_id
                ORDER BY month DESC
                LIMIT 1
            ) o
            FULL JOIN (
                SELECT revenue, hostel_id
                FROM revenues
                WHERE hostel_id = :hostel_id
                ORDER BY month DESC
                LIMIT 1
            ) r ON o.hostel_id = r.hostel_id
            """
        )
        result = db.execute(fallback_query, {"hostel_id": hostel_id}).fetchall()
 
    # Convert to list of dictionaries for easy JSON serialization
    return [{"occupancy_rate": row[0], "revenue": row[1]} for row in result]