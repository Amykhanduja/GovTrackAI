import logging
from db.connection import SessionLocal
from db.models import Job, Organization, Application
from sqlalchemy import func

logger = logging.getLogger('app.excel.data_provider')

class DataProvider:
    def __init__(self, db_manager=None):
        self.db = db_manager

    def get_dashboard_kpis(self):
        # Fetch purely from SQLite
        db = SessionLocal()
        try:
            total_jobs = db.query(Job).count()
            applied = db.query(Job).filter(Job.is_applied == True).count()
            avg_sal = db.query(func.avg(Job.salary)).scalar() or 0
            orgs = db.query(Organization).count()
            
            return {
                'Total Jobs': total_jobs,
                'New Jobs': db.query(Job).filter(Job.status == 'New').count(),
                'Applied': applied,
                'Pending': total_jobs - applied,
                'Upcoming Exams': 0,
                'Upcoming Interviews': 0,
                'Average Salary': f"₹ {int(avg_sal):,}",
                'Highest Salary': f"₹ {int(db.query(func.max(Job.salary)).scalar() or 0):,}",
                'Organizations Tracked': orgs,
                'Downloaded PDFs': 0,
                'AI Processed Jobs': total_jobs
            }
        finally:
            db.close()

    def get_master_jobs(self):
        db = SessionLocal()
        try:
            results = db.query(Job, Organization.name).outerjoin(Organization).all()
            final = []
            for job, org_name in results:
                final.append({
                    'id': job.id, 'org': org_name, 'post': job.title,
                    'priority': job.priority, 'status': job.status,
                    'salary': job.salary, 'deadline': job.deadline, 'link': job.url
                })
            return final
        finally:
            db.close()

    def get_applications(self):
        return []

    def get_exams(self):
        return []

    def get_chart_data(self):
        return {
            'status_dist': {},
            'org_dist': {},
            'monthly_trend': {}
        }
