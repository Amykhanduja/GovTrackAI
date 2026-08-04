import logging
from datetime import datetime, timedelta

logger = logging.getLogger('app.excel.data_provider')

class DataProvider:
    def __init__(self, db_manager=None):
        self.db = db_manager

    def get_dashboard_kpis(self):
        return {
            'Total Jobs': 450,
            'New Jobs': 24,
            'Applied': 15,
            'Pending': 8,
            'Upcoming Exams': 3,
            'Upcoming Interviews': 1,
            'Average Salary': '₹ 85,000',
            'Highest Salary': '₹ 2,50,000',
            'Organizations Tracked': 25,
            'Downloaded PDFs': 310,
            'AI Processed Jobs': 450
        }

    def get_master_jobs(self):
        return [
            {'id': 1, 'org': 'RBI', 'post': 'Grade B Officer', 'priority': 95, 'status': 'New', 'salary': 120000, 'deadline': (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'), 'link': 'https://rbi.org.in'},
            {'id': 2, 'org': 'SBI', 'post': 'PO', 'priority': 85, 'status': 'Applied', 'salary': 85000, 'deadline': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'), 'link': 'https://sbi.co.in'},
            {'id': 3, 'org': 'NIC', 'post': 'Scientist B', 'priority': 90, 'status': 'Urgent', 'salary': 100000, 'deadline': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'), 'link': 'https://nic.in'}
        ]

    def get_applications(self):
        return [
            {'app_id': 'APP-1001', 'org': 'SBI', 'post': 'PO', 'date': '2026-07-20', 'fee': 750, 'status': 'Exam Pending', 'progress': 0.4},
            {'app_id': 'APP-1002', 'org': 'IBPS', 'post': 'IT Officer', 'date': '2026-06-15', 'fee': 850, 'status': 'Interview Scheduled', 'progress': 0.8}
        ]

    def get_exams(self):
        return [
            {'org': 'SBI', 'exam': 'Prelims', 'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'), 'status': 'Admit Card Released'},
            {'org': 'IBPS', 'exam': 'Mains', 'date': (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'), 'status': 'Scheduled'}
        ]

    def get_chart_data(self):
        return {
            'status_dist': {'Applied': 15, 'New': 24, 'Expired': 411},
            'org_dist': {'RBI': 5, 'SBI': 10, 'NIC': 8, 'ISRO': 2},
            'monthly_trend': {'Jan': 10, 'Feb': 25, 'Mar': 40, 'Apr': 15, 'May': 30, 'Jun': 50}
        }
