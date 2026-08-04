import logging
import os
import sqlite3

logger = logging.getLogger('app.health')

class HealthMonitor:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def check_database(self) -> bool:
        if not os.path.exists(self.db_path):
            return False
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            conn.close()
            return True
        except:
            return False

    def check_storage(self) -> dict:
        # Mock checking disk space
        return {'status': 'OK', 'free_gb': 100}

    def generate_report(self) -> dict:
        return {
            'database': self.check_database(),
            'storage': self.check_storage()
        }
