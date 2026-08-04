import os
import shutil
import platform
from datetime import datetime

class DataManager:
    def __init__(self):
        self.is_portable = os.path.exists(".portable")
        self.app_name = "GovTrackAI"
        self.base_path = self._determine_base_path()
        self.init_directories()

    def _determine_base_path(self):
        if self.is_portable:
            return os.path.abspath("data")
        
        system = platform.system()
        if system == "Windows":
            return os.path.join(os.environ.get("APPDATA", ""), self.app_name)
        elif system == "Darwin":
            return os.path.join(os.path.expanduser("~"), "Library", "Application Support", self.app_name)
        else:
            return os.path.join(os.path.expanduser("~"), f".{self.app_name.lower()}")

    def init_directories(self):
        dirs = ['database', 'config', 'logs', 'reports', 'downloads', 'backups', 'cache']
        for d in dirs:
            os.makedirs(os.path.join(self.base_path, d), exist_ok=True)
            
    def get_db_path(self):
        return os.path.join(self.base_path, "database", "govtrack.sqlite")
        
    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(self.base_path, "backups", f"backup_{timestamp}")
        os.makedirs(backup_dir)
        
        # Copy DB and Config
        shutil.copy2(self.get_db_path(), backup_dir)
        config_path = os.path.join(self.base_path, "config")
        if os.path.exists(config_path):
            shutil.copytree(config_path, os.path.join(backup_dir, "config"), dirs_exist_ok=True)
        return backup_dir
