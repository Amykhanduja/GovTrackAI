import logging
import time

logger = logging.getLogger('app.scheduler')

class TaskScheduler:
    def __init__(self):
        self.jobs = []
        self.history = []

    def schedule_job(self, name: str, func, interval_seconds: int):
        self.jobs.append({'name': name, 'func': func, 'interval': interval_seconds, 'last_run': 0})

    def run_pending(self):
        current_time = time.time()
        for job in self.jobs:
            if current_time - job['last_run'] >= job['interval']:
                try:
                    logger.info(f"Running scheduled job: {job['name']}")
                    job['func']()
                    self.history.append({'name': job['name'], 'status': 'Success', 'time': current_time})
                except Exception as e:
                    logger.error(f"Scheduled job {job['name']} failed: {e}")
                    self.history.append({'name': job['name'], 'status': 'Failed', 'error': str(e), 'time': current_time})
                finally:
                    job['last_run'] = time.time()
