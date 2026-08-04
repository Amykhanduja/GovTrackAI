import logging
import shutil
import os
from datetime import datetime

logger = logging.getLogger('app.backup')

class BackupManager:
    def __init__(self, db_path: str, backup_dir: str):
        self.db_path = db_path
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)

    def backup_database(self) -> str:
        if not os.path.exists(self.db_path):
            return None
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(self.backup_dir, f"govtrack_{timestamp}.sqlite")
        try:
            shutil.copy2(self.db_path, dest)
            return dest
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
