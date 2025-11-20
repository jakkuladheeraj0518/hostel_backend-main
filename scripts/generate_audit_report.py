"""
Export audit logs
"""
import sys
import os
import csv
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.repositories.audit_repository import AuditRepository


def generate_audit_report(output_file: str = "audit_report.csv"):
    """Generate audit report as CSV"""
    db = SessionLocal()
    try:
        audit_repo = AuditRepository(db)
        logs = audit_repo.get_all(skip=0, limit=10000)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'user_id', 'hostel_id', 'action', 'resource', 'ip_address', 'created_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for log in logs:
                writer.writerow({
                    'id': log.id,
                    'user_id': log.user_id,
                    'hostel_id': log.hostel_id,
                    'action': log.action,
                    'resource': log.resource,
                    'ip_address': log.ip_address,
                    'created_at': log.created_at.isoformat() if log.created_at else None
                })
        
        print(f"Audit report generated: {output_file}")
        print(f"Total records: {len(logs)}")
        
    except Exception as e:
        print(f"Error generating report: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate audit report")
    parser.add_argument("--output", "-o", default="audit_report.csv", help="Output file name")
    args = parser.parse_args()
    generate_audit_report(args.output)

