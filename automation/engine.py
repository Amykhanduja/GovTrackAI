import logging
from automation.scheduler import TaskScheduler
from automation.health import HealthMonitor
from automation.backup import BackupManager
from notifications.engine import NotificationEngine

logger = logging.getLogger('app.automation_engine')

class AutomationEngine:
    def __init__(self, config):
        self.config = config
        self.scheduler = TaskScheduler()
        self.notifier = NotificationEngine()
        self.health = HealthMonitor(config.get('db_path', 'data/govtrack.sqlite'))
        self.backup = BackupManager(config.get('db_path', 'data/govtrack.sqlite'), config.get('backup_dir', 'data/backups'))
        
        self._register_core_tasks()

    def _register_core_tasks(self):
        # Weekly backup (simulated as 604800 seconds)
        self.scheduler.schedule_job("Database Backup", self.perform_backup, 604800)
        # Daily health check
        self.scheduler.schedule_job("Health Check", self.check_health, 86400)
        
    def perform_backup(self):
        dest = self.backup.backup_database()
        if dest:
            self.notifier.notify("System Backup", f"Database backed up successfully to {dest}")
            
    def check_health(self):
        report = self.health.generate_report()
        if not report['database']:
            self.notifier.notify("CRITICAL ERROR", "Database integrity check failed!")

    def run_full_cycle(self, scraper_manager, ai_pipeline, excel_engine):
        # 1. Scrape
        logger.info("Starting Automation Cycle: Scraping")
        scraper_stats = scraper_manager.run_all()
        
        # 2. AI Processing (simulated queue drain)
        logger.info("Starting Automation Cycle: AI Processing")
        
        # 3. DB Cleanup / Sync
        logger.info("Starting Automation Cycle: Database Maintenance")
        
        # 4. Generate Reports
        logger.info("Starting Automation Cycle: Excel Dashboard Generation")
        excel_engine.generate()
        
        # 5. Notify
        self.notifier.send_daily_summary({'new_jobs': 5, 'deadlines': 2})
        logger.info("Automation Cycle Complete")
