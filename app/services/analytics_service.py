from sqlalchemy.orm import Session
from sqlalchemy import func , extract , case
from typing import List, Dict, Any, Tuple

from app.models.analytics import HotFactReport, ColdFactReport
from app.models.user import User
from app.schemas.analytics import DashboardStatsResponse
from app.models.report import Report

class AnalyticsService:
    """Business logic for Analytics DB queries"""
    
    @staticmethod
    def get_dashboard_stats(db: Session) -> DashboardStatsResponse:
        """
        Get high-level KPIs for admin dashboard.
        Queries the Analytics DB (hot table).
        """
        
        # Total reports (hot + cold)
        hot_count = db.query(func.count(HotFactReport.reportId)).scalar() or 0
        
        # Try to get cold count (may fail if cold table empty)
        try:
            cold_count = db.query(func.count(ColdFactReport.reportId)).scalar() or 0
        except:
            cold_count = 0
        
        total_reports = hot_count + cold_count
        
        # Reports by status (from hot table)
        status_counts = db.query(
            HotFactReport.status,
            func.count(HotFactReport.reportId).label('count')
        ).group_by(HotFactReport.status).all()
        
        # Reports by category
        category_counts = db.query(
            HotFactReport.categoryId,
            func.count(HotFactReport.reportId).label('count')
        ).group_by(HotFactReport.categoryId).all()
        
        # Average AI confidence
        avg_confidence = db.query(
            func.avg(HotFactReport.aiConfidence)
        ).scalar() or 0.0
        
        # Anonymous vs Registered
        anonymous_count = db.query(
            func.count(HotFactReport.reportId)
        ).filter(HotFactReport.isAnonymous == True).scalar() or 0


    @staticmethod
    def get_cold_monthly_category_breakdown(db: Session):
        """Returns (year, month, category, count) for COLD database."""
        return db.query(
            extract('year', ColdFactReport.createdAt).label('report_year'),
            extract('month', ColdFactReport.createdAt).label('report_month'),
            ColdFactReport.categoryId,
            func.count().label('count')
        ).group_by(
            extract('year', ColdFactReport.createdAt),
            extract('month', ColdFactReport.createdAt),
            ColdFactReport.categoryId
        ).order_by(
            'report_year',
            'report_month'
        ).all()

  
    @staticmethod
    def get_hot_monthly_category_breakdown(db: Session):
        """Returns (year, month, category, count) for HOT database."""
        return db.query(
            extract('year', HotFactReport.createdAt).label('report_year'),
            extract('month', HotFactReport.createdAt).label('report_month'),
            HotFactReport.categoryId,
            func.count().label('count')
        ).group_by(
            extract('year', HotFactReport.createdAt),
            extract('month', HotFactReport.createdAt),
            HotFactReport.categoryId
        ).order_by(
            'report_year',
            'report_month'
        ).all()




        return DashboardStatsResponse(
            totalReports=total_reports,
            hotReports=hot_count,
            coldReports=cold_count,
            statusBreakdown={row.status: row.count for row in status_counts},
            categoryBreakdown={row.categoryId: row.count for row in category_counts},
            avgAiConfidence=float(avg_confidence),
            anonymousReports=anonymous_count,
            registeredReports=hot_count - anonymous_count
        )
    
    @staticmethod
    def export_csv_data(db: Session) -> List[HotFactReport]:
        """Get recent reports for CSV export"""
        return db.query(HotFactReport).order_by(
            HotFactReport.createdAt.desc()
        ).limit(10000).all()

    def get_user_demographic_breakdown(db: Session) -> List[Tuple]:
        """Returns (role, is_anonymous, account_age_segment, user_count) for dashboard."""
        
        # SQLAlchemy 2.0 syntax - use positional arguments, not a list
        account_age_segment = case(
            (func.extract('day', func.now() - User.createdAt) <= 30, 'New (< 30 days)'),
            (func.extract('day', func.now() - User.createdAt) <= 90, 'Active (1-3 months)'),
            (func.extract('day', func.now() - User.createdAt) <= 365, 'Established (3-12 months)'),
            else_='Long-term (> 1 year)'
        ).label('account_age_segment')
        
        return db.query(
            User.role,
            User.isAnonymous,
            account_age_segment,
            func.count(User.userId).label('user_count')
        ).group_by(
            User.role,
            User.isAnonymous,
            account_age_segment
        ).order_by(
            User.role,
            User.isAnonymous,
            account_age_segment
        ).all()
    

    @staticmethod
    def get_all_users_list(db: Session):
        """Returns (userId, email, phoneNumber, role, isAnonymous, createdAt) for all users."""
        return db.query(
            User.userId,
            User.email,
            User.phoneNumber,
            User.role,
            User.isAnonymous,
            User.createdAt,
            User.hashedDeviceId,
            User.passwordHash
        ).order_by(
            User.createdAt.desc()
        ).all()