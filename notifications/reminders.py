import logging
from datetime import datetime, timedelta

logger = logging.getLogger('app.reminders')

class ReminderSystem:
    def __init__(self, notification_engine):
        self.notifier = notification_engine
        self.thresholds = [30, 15, 7, 3, 1] # Days before deadline

    def process_deadlines(self, jobs: list):
        # Jobs should be a list of dicts with 'deadline' (YYYY-MM-DD) and 'title'
        today = datetime.now()
        for job in jobs:
            try:
                deadline = datetime.strptime(job['deadline'], '%Y-%m-%d')
                days_left = (deadline - today).days
                if days_left in self.thresholds:
                    self.notifier.notify("Deadline Reminder", f"Only {days_left} days left for {job['title']}!")
            except Exception as e:
                logger.error(f"Error processing reminder for {job}: {e}")
