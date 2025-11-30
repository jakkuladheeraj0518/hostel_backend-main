from datetime import datetime


def is_working_hours(start, end):
    """Check current time in working hours"""
    now = datetime.utcnow()
    if not start or not end:
        return True

    start_h, start_m = map(int, start.split(":"))
    end_h, end_m = map(int, end.split(":"))
    return start_h <= now.hour <= end_h


def build_audit_log(rule, recipients, execution_time):
    return {
        "rule": rule.rule_name if rule else None,
        "recipients": [u.id for u in recipients["primary"]],
        "execution_time_ms": execution_time
    }
