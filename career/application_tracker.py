class ApplicationTracker:
    def __init__(self, db_manager=None):
        self.db = db_manager
        # In reality, this would store in a career_applications table
        self.applications = {}

    def track_application(self, job_id: int, status: str, details: dict = None):
        valid_statuses = ['Submitted', 'Fee Paid', 'Admit Card', 'Interview', 'Rejected', 'Offer Accepted']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")
            
        self.applications[job_id] = {
            'status': status,
            'details': details or {}
        }
