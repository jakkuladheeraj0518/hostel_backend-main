from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional
from datetime import datetime, timedelta, date
from decimal import Decimal
from app.schemas.reports import *
from app.repositories.complaint_repository import ComplaintRepository

class AnalyticsService:
    
    @staticmethod
    def get_multi_hostel_dashboard(db: Session, hostel_ids: List[int], 
                                   start_date: date, end_date: date) -> MultiHostelDashboard:
        """Get unified dashboard for multiple hostels"""
        
        hostel_kpis = []
        
        for hostel_id in hostel_ids:
            kpi = AnalyticsService._get_hostel_kpi(db, hostel_id, start_date, end_date)
            if kpi:
                hostel_kpis.append(kpi)
            # if hostel not found, skip it silently
        
        # Calculate summary
        if not hostel_kpis:
            # No valid hostels found — return empty summary
            summary = KPISummary(
                total_revenue=Decimal(0),
                total_expenses=Decimal(0),
                net_profit=Decimal(0),
                occupancy_rate=0,
                total_complaints=0,
                resolved_complaints=0,
                average_resolution_time=0.0,
                student_count=0
            )
            return MultiHostelDashboard(
                summary=summary,
                hostels=[],
                period=f"{start_date} to {end_date}",
                generated_at=datetime.utcnow()
            )

        # Calculate summary from available hostels
        summary = KPISummary(
            total_revenue=sum((h.revenue for h in hostel_kpis), Decimal(0)),
            total_expenses=sum((h.expenses for h in hostel_kpis), Decimal(0)),
            net_profit=sum((h.profit for h in hostel_kpis), Decimal(0)),
            occupancy_rate=sum(h.occupancy_rate for h in hostel_kpis) / len(hostel_kpis),
            total_complaints=sum(h.complaint_count for h in hostel_kpis),
            resolved_complaints=sum(h.resolved_complaints for h in hostel_kpis),
            average_resolution_time=0.0,  # Calculate separately
            student_count=sum(h.occupied_beds for h in hostel_kpis)
        )
        
        # Get average resolution time
        complaint_stats = ComplaintRepository.get_statistics(db, hostel_ids, 
                                                            datetime.combine(start_date, datetime.min.time()),
                                                            datetime.combine(end_date, datetime.max.time()))
        summary.average_resolution_time = complaint_stats.get('average_resolution_hours', 0)
        
        return MultiHostelDashboard(
            summary=summary,
            hostels=hostel_kpis,
            period=f"{start_date} to {end_date}",
            generated_at=datetime.utcnow()
        )
    
    @staticmethod
    def _get_hostel_kpi(db: Session, hostel_id: int, start_date: date, end_date: date) -> HostelKPI:
        """Get KPI for a single hostel"""
        
        # Get hostel info
        hostel = db.execute(text("""
            SELECT id, hostel_name, total_beds, current_occupancy
            FROM hostels WHERE id = :hostel_id
        """), {'hostel_id': hostel_id}).first()
        
        if not hostel:
            return None
        
        # Get financial data
        financial = db.execute(text("""
            SELECT 
                SUM(CASE WHEN transaction_type IN ('fee', 'booking') THEN amount ELSE 0 END) as revenue,
                SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) as expenses
            FROM financial_transactions
            WHERE hostel_id = :hostel_id 
            AND transaction_date BETWEEN :start_date AND :end_date
        """), {'hostel_id': hostel_id, 'start_date': start_date, 'end_date': end_date}).first()
        
        revenue = financial.revenue or Decimal(0)
        expenses = financial.expenses or Decimal(0)
        
        # Get complaint stats
        complaint_stats = ComplaintRepository.get_statistics(
            db, [hostel_id],
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.max.time())
        )
        
        # `current_occupancy` stores occupied beds; compute occupancy and available beds from it
        current_occupancy = hostel.current_occupancy or 0
        total_beds = hostel.total_beds or 0  # Default to 0 if NULL
        occupied_beds = current_occupancy
        occupancy_rate = (occupied_beds / total_beds * 100) if total_beds and total_beds > 0 else 0
        
        return HostelKPI(
            hostel_id=hostel.id,
            hostel_name=hostel.hostel_name,
            revenue=revenue,
            expenses=expenses,
            profit=revenue - expenses,
            occupancy_rate=occupancy_rate,
            total_beds=total_beds,
            occupied_beds=occupied_beds,
            complaint_count=complaint_stats['total'],
            resolved_complaints=complaint_stats['resolved'],
            average_rating=0.0
        )
    
    @staticmethod
    def get_revenue_comparison(db: Session, hostel_ids: List[int], 
                              current_start: date, current_end: date,
                              previous_start: date, previous_end: date) -> List[RevenueComparison]:
        """Compare revenue across hostels and periods"""
        
        comparisons = []
        
        for hostel_id in hostel_ids:
            hostel = db.execute(text("SELECT hostel_name FROM hostels WHERE id = :id"), 
                              {'id': hostel_id}).first()
            
            if not hostel:
                continue
            
            # Current period revenue
            current = db.execute(text("""
                SELECT SUM(amount) as total
                FROM financial_transactions
                WHERE hostel_id = :hostel_id 
                AND transaction_type IN ('fee', 'booking')
                AND transaction_date BETWEEN :start_date AND :end_date
            """), {'hostel_id': hostel_id, 'start_date': current_start, 'end_date': current_end}).first()
            
            # Previous period revenue
            previous = db.execute(text("""
                SELECT SUM(amount) as total
                FROM financial_transactions
                WHERE hostel_id = :hostel_id 
                AND transaction_type IN ('fee', 'booking')
                AND transaction_date BETWEEN :start_date AND :end_date
            """), {'hostel_id': hostel_id, 'start_date': previous_start, 'end_date': previous_end}).first()
            
            current_revenue = current.total or Decimal(0)
            previous_revenue = previous.total or Decimal(0)
            
            growth_rate = 0.0
            if previous_revenue > 0:
                growth_rate = float((current_revenue - previous_revenue) / previous_revenue * 100)
            
            # Monthly breakdown
            monthly = db.execute(text("""
                SELECT 
                    DATE_TRUNC('month', transaction_date) as month,
                    SUM(amount) as revenue
                FROM financial_transactions
                WHERE hostel_id = :hostel_id 
                AND transaction_type IN ('fee', 'booking')
                AND transaction_date BETWEEN :start_date AND :end_date
                GROUP BY DATE_TRUNC('month', transaction_date)
                ORDER BY month
            """), {'hostel_id': hostel_id, 'start_date': current_start, 'end_date': current_end}).fetchall()
            
            monthly_breakdown = [{'month': str(row.month), 'revenue': float(row.revenue)} for row in monthly]
            
            comparisons.append(RevenueComparison(
                hostel_id=hostel_id,
                hostel_name=hostel.hostel_name,
                current_period_revenue=current_revenue,
                previous_period_revenue=previous_revenue,
                growth_rate=growth_rate,
                monthly_breakdown=monthly_breakdown
            ))
        
        return comparisons
    
    @staticmethod
    def get_occupancy_trends(db: Session, hostel_ids: List[int], 
                            start_date: date, end_date: date) -> List[OccupancyTrend]:
        """Get occupancy trends over time"""
        
        trends = []
        
        # Generate date range
        current_date = start_date
        while current_date <= end_date:
            for hostel_id in hostel_ids:
                hostel = db.execute(text("""
                    SELECT hostel_name, total_beds, current_occupancy 
                        FROM hostels WHERE id = :id
                """), {'id': hostel_id}).first()
                
                if hostel:
                    current_occupancy = hostel.current_occupancy or 0
                    occupied = current_occupancy
                    total_beds = hostel.total_beds or 0  # Default to 0 if NULL
                    occupancy_rate = (occupied / total_beds * 100) if total_beds and total_beds > 0 else 0

                    trends.append(OccupancyTrend(
                        hostel_id=hostel_id,
                        hostel_name=hostel.hostel_name,
                        date=current_date,
                        occupancy_rate=occupancy_rate,
                        occupied_beds=occupied,
                        total_beds=total_beds
                    ))
            
            current_date += timedelta(days=1)
        
        return trends
    
    @staticmethod
    def get_complaint_metrics(db: Session, hostel_ids: List[int], 
                             start_date: date, end_date: date) -> List[ComplaintMetrics]:
        """Get complaint metrics by hostel"""
        
        metrics = []
        
        for hostel_id in hostel_ids:
            hostel = db.execute(text("SELECT hostel_name FROM hostels WHERE id = :id"), 
                              {'id': hostel_id}).first()
            
            if not hostel:
                continue
            
            # Get complaints by category, status, priority
            by_category = db.execute(text("""
                SELECT category, COUNT(*) as count
                FROM complaints
                WHERE hostel_name = :hostel_name
                AND created_at BETWEEN :start_date AND :end_date
                GROUP BY category
            """), {
                'hostel_name': hostel.hostel_name,
                'start_date': datetime.combine(start_date, datetime.min.time()),
                'end_date': datetime.combine(end_date, datetime.max.time())
            }).fetchall()
            
            by_status = db.execute(text("""
                SELECT status, COUNT(*) as count
                FROM complaints
                WHERE hostel_name = :hostel_name
                AND created_at BETWEEN :start_date AND :end_date
                GROUP BY status
            """), {
                'hostel_name': hostel.hostel_name,
                'start_date': datetime.combine(start_date, datetime.min.time()),
                'end_date': datetime.combine(end_date, datetime.max.time())
            }).fetchall()
            
            by_priority = db.execute(text("""
                SELECT priority, COUNT(*) as count
                FROM complaints
                WHERE hostel_name = :hostel_name
                AND created_at BETWEEN :start_date AND :end_date
                GROUP BY priority
            """), {
                'hostel_name': hostel.hostel_name,
                'start_date': datetime.combine(start_date, datetime.min.time()),
                'end_date': datetime.combine(end_date, datetime.max.time())
            }).fetchall()
            
            stats = ComplaintRepository.get_statistics(
                db, [hostel_id],
                datetime.combine(start_date, datetime.min.time()),
                datetime.combine(end_date, datetime.max.time())
            )
            
            metrics.append(ComplaintMetrics(
                hostel_id=hostel_id,
                hostel_name=hostel.hostel_name,
                total_complaints=stats['total'],
                by_category={row.category: row.count for row in by_category},
                by_status={row.status: row.count for row in by_status},
                by_priority={row.priority: row.count for row in by_priority},
                average_resolution_time=stats['average_resolution_hours'],
                satisfaction_rating=stats['average_rating']
            ))
        
        return metrics
    
    @staticmethod
    def get_marketing_analytics(db: Session, hostel_ids: List[int], 
                                start_date: date, end_date: date) -> List[MarketingAnalytics]:
        """Get marketing analytics by hostel"""
        
        analytics = []
        
        for hostel_id in hostel_ids:
            hostel = db.execute(text("SELECT hostel_name FROM hostels WHERE id = :id"), 
                              {'id': hostel_id}).first()
            
            if not hostel:
                continue
            
            # Profile views
            views = db.execute(text("""
                SELECT COUNT(*) as count
                FROM hostel_profile_views
                WHERE hostel_id = :hostel_id
                AND viewed_at BETWEEN :start_date AND :end_date
            """), {
                'hostel_id': hostel_id,
                'start_date': datetime.combine(start_date, datetime.min.time()),
                'end_date': datetime.combine(end_date, datetime.max.time())
            }).scalar()
            
            # Search appearances (simplified - count from search queries)
            searches = db.execute(text("""
                SELECT COUNT(*) as count
                FROM search_queries
                WHERE searched_at BETWEEN :start_date AND :end_date
            """), {
                'start_date': datetime.combine(start_date, datetime.min.time()),
                'end_date': datetime.combine(end_date, datetime.max.time())
            }).scalar()
            
            # Bookings
            bookings_data = db.execute(text("""
                SELECT COUNT(*) as count
                FROM hostel_bookings
                WHERE hostel_id = :hostel_id
                AND booking_date BETWEEN :start_date AND :end_date
            """), {
                'hostel_id': hostel_id,
                'start_date': datetime.combine(start_date, datetime.min.time()),
                'end_date': datetime.combine(end_date, datetime.max.time())
            }).scalar()
            
            # Top sources
            sources = db.execute(text("""
                SELECT source, COUNT(*) as count
                FROM hostel_profile_views
                WHERE hostel_id = :hostel_id
                AND viewed_at BETWEEN :start_date AND :end_date
                GROUP BY source
                ORDER BY count DESC
                LIMIT 5
            """), {
                'hostel_id': hostel_id,
                'start_date': datetime.combine(start_date, datetime.min.time()),
                'end_date': datetime.combine(end_date, datetime.max.time())
            }).fetchall()
            
            conversion_rate = (bookings_data / views * 100) if views > 0 else 0
            
            analytics.append(MarketingAnalytics(
                hostel_id=hostel_id,
                hostel_name=hostel.hostel_name,
                profile_views=views or 0,
                search_appearances=searches or 0,
                inquiries=0,  # Would need inquiry table
                bookings=bookings_data or 0,
                conversion_rate=conversion_rate,
                top_sources=[{'source': row.source, 'count': row.count} for row in sources]
            ))
        
        return analytics
    
    @staticmethod
    def get_attendance_report(db: Session, hostel_id: int, report_date: date) -> AttendanceReport:
        """Get attendance report for a specific date"""
        
        hostel = db.execute(text("SELECT hostel_name FROM hostels WHERE id = :id"), 
                          {'id': hostel_id}).first()
        
        # Get attendance data from student_attendance (join users to filter by hostel)
        attendance_data = db.execute(text("""
            SELECT 
                COUNT(*) as total_students,
                SUM(CASE WHEN sa.status = 'present' THEN 1 ELSE 0 END) as present_count
            FROM student_attendance sa
            JOIN users u ON u.id::text = sa.student_id
            WHERE u.hostel_id = :hostel_id AND sa.attendance_date = :date
        """), {'hostel_id': hostel_id, 'date': report_date}).first()

        # Get absent students (join users for name)
        absent = db.execute(text("""
            SELECT sa.student_id as student_id, u.name as student_name
            FROM student_attendance sa
            LEFT JOIN users u ON u.id::text = sa.student_id
            WHERE u.hostel_id = :hostel_id AND sa.attendance_date = :date AND sa.status != 'present'
        """), {'hostel_id': hostel_id, 'date': report_date}).fetchall()
        
        total = attendance_data.total_students or 0
        present = attendance_data.present_count or 0
        absent_count = total - present
        attendance_rate = (present / total * 100) if total > 0 else 0
        
        return AttendanceReport(
            hostel_id=hostel_id,
            hostel_name=hostel.hostel_name if hostel else "Unknown",
            date=report_date,
            total_students=total,
            present_count=present,
            absent_count=absent_count,
            attendance_rate=attendance_rate,
            absent_students=[{'student_id': str(row.student_id), 'student_name': row.student_name} for row in absent]
        )
    
    @staticmethod
    def get_attendance_trends(db: Session, hostel_id: int, 
                             start_date: date, end_date: date) -> AttendanceTrend:
        """Get attendance trends over a period"""
        
        hostel = db.execute(text("SELECT hostel_name FROM hostels WHERE id = :id"), 
                          {'id': hostel_id}).first()
        
        # Daily trends
        daily = db.execute(text("""
            SELECT 
                sa.attendance_date as date,
                COUNT(*) as total_students,
                SUM(CASE WHEN sa.status = 'present' THEN 1 ELSE 0 END) as present_count
            FROM student_attendance sa
            JOIN users u ON u.id::text = sa.student_id
            WHERE u.hostel_id = :hostel_id 
            AND sa.attendance_date BETWEEN :start_date AND :end_date
            GROUP BY sa.attendance_date
            ORDER BY sa.attendance_date
        """), {'hostel_id': hostel_id, 'start_date': start_date, 'end_date': end_date}).fetchall()
        
        daily_trends = []
        total_rate = 0
        for row in daily:
            rate = (row.present_count / row.total_students * 100) if row.total_students > 0 else 0
            daily_trends.append({
                'date': str(row.date),
                'total_students': row.total_students,
                'present_count': row.present_count,
                'attendance_rate': rate
            })
            total_rate += rate
        
        avg_rate = total_rate / len(daily) if daily else 0
        
        # Patterns (day of week analysis)
        patterns = db.execute(text("""
            SELECT 
                EXTRACT(DOW FROM sa.attendance_date) as day_of_week,
                AVG(CASE WHEN sa.status = 'present' THEN 100.0 ELSE 0.0 END) as avg_attendance
            FROM student_attendance sa
            JOIN users u ON u.id::text = sa.student_id
            WHERE u.hostel_id = :hostel_id 
            AND sa.attendance_date BETWEEN :start_date AND :end_date
            GROUP BY EXTRACT(DOW FROM sa.attendance_date)
            ORDER BY day_of_week
        """), {'hostel_id': hostel_id, 'start_date': start_date, 'end_date': end_date}).fetchall()
        
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        pattern_dict = {day_names[int(row.day_of_week)]: float(row.avg_attendance) for row in patterns}
        
        return AttendanceTrend(
            hostel_id=hostel_id,
            hostel_name=hostel.hostel_name if hostel else "Unknown",
            period=f"{start_date} to {end_date}",
            daily_trends=daily_trends,
            average_attendance_rate=avg_rate,
            patterns=pattern_dict
        )
    
    @staticmethod
    def get_student_attendance_history(db: Session, student_id: int, 
                                       start_date: date, end_date: date) -> StudentAttendanceHistory:
        """Get attendance history for a student"""
        
        # Get student info and attendance from student_attendance
        attendance = db.execute(text("""
            SELECT 
                sa.student_id as student_id, u.name as student_name, u.hostel_id,
                COUNT(*) as total_days,
                SUM(CASE WHEN sa.status = 'present' THEN 1 ELSE 0 END) as present_days
            FROM student_attendance sa
            LEFT JOIN users u ON u.id::text = sa.student_id
            WHERE sa.student_id = (:student_id)::text 
            AND sa.attendance_date BETWEEN :start_date AND :end_date
            GROUP BY sa.student_id, u.name, u.hostel_id
        """), {'student_id': student_id, 'start_date': start_date, 'end_date': end_date}).first()
        
        if not attendance:
            return None
        
        # Get recent absences
        absences = db.execute(text("""
            SELECT sa.attendance_date as date
            FROM student_attendance sa
            WHERE sa.student_id = (:student_id)::text 
            AND sa.status != 'present'
            AND sa.attendance_date BETWEEN :start_date AND :end_date
            ORDER BY sa.attendance_date DESC
            LIMIT 10
        """), {'student_id': student_id, 'start_date': start_date, 'end_date': end_date}).fetchall()
        
        total = int(attendance.total_days or 0)
        present = int(attendance.present_days or 0)
        absent = total - present
        percentage = (present / total * 100) if total > 0 else 0

        # Safely coerce/replace nullable fields coming from the DB so pydantic validation doesn't fail
        try:
            student_id_val = int(attendance.student_id) if attendance.student_id is not None else int(student_id)
        except Exception:
            student_id_val = int(student_id)

        student_name_val = attendance.student_name or ""

        # If hostel_id is missing, use 0 as a safe default (or change to raise a 404 if preferred)
        try:
            hostel_id_val = int(attendance.hostel_id) if attendance.hostel_id is not None else 0
        except Exception:
            hostel_id_val = 0

        return StudentAttendanceHistory(
            student_id=student_id_val,
            student_name=student_name_val,
            hostel_id=hostel_id_val,
            total_days=total,
            present_days=present,
            absent_days=absent,
            attendance_percentage=percentage,
            recent_absences=[row.date for row in absences]
        )
    
    @staticmethod
    def get_consolidated_attendance_report(db: Session, hostel_ids: List[int], 
                                          start_date: date, end_date: date) -> ConsolidatedAttendanceReport:
        """Get consolidated attendance report across multiple hostels"""
        
        # Summary
        summary_data = db.execute(text("""
            SELECT 
                COUNT(DISTINCT u.hostel_id) as total_hostels,
                COUNT(DISTINCT sa.student_id) as total_students,
                COUNT(*) as total_records,
                SUM(CASE WHEN sa.status = 'present' THEN 1 ELSE 0 END) as total_present
            FROM student_attendance sa
            JOIN users u ON u.id::text = sa.student_id
            WHERE u.hostel_id = ANY(:hostel_ids)
            AND sa.attendance_date BETWEEN :start_date AND :end_date
        """), {'hostel_ids': hostel_ids, 'start_date': start_date, 'end_date': end_date}).first()
        
        total_records = summary_data.total_records or 0
        total_present = summary_data.total_present or 0
        overall_rate = (total_present / total_records * 100) if total_records > 0 else 0
        
        summary = {
            'total_hostels': summary_data.total_hostels or 0,
            'total_students': summary_data.total_students or 0,
            'overall_attendance_rate': overall_rate,
            'total_records': total_records
        }
        
        # Hostel-wise reports
        hostel_reports = []
        for hostel_id in hostel_ids:
            # Use end_date for the report
            report = AnalyticsService.get_attendance_report(db, hostel_id, end_date)
            hostel_reports.append(report)
        
        # Trends
        trends = []
        for hostel_id in hostel_ids:
            trend = AnalyticsService.get_attendance_trends(db, hostel_id, start_date, end_date)
            trends.append(trend)
        
        return ConsolidatedAttendanceReport(
            period=DateRangeFilter(start_date=start_date, end_date=end_date, hostel_ids=hostel_ids),
            summary=summary,
            hostel_wise=hostel_reports,
            trends=trends,
            generated_at=datetime.utcnow()
        )