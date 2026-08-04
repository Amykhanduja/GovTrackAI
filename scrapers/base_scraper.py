import logging
from typing import List, Dict
from utils.change_detection import ChangeDetector
from utils.normalization import NormalizationEngine
from storage.download_manager import DownloadManager
from core.validation import RecordValidator
from utils.request_engine import RequestEngine

logger = logging.getLogger('app.scrapers')

class BaseScraper:
    # Subclasses must override this
    org_id = "unknown"
    org_name = "Unknown"

    def __init__(self, config):
        self.config = config
        self.request_engine = RequestEngine(config)
        self.change_detector = ChangeDetector()
        self.normalizer = NormalizationEngine()
        self.download_manager = DownloadManager(config)
        self.validator = RecordValidator()
        self.stats = {'total': 0, 'new': 0, 'updated': 0, 'failed': 0, 'downloads': 0}

    # --- LIFECYCLE METHODS ---
    def execute(self):
        try:
            self.initialize()
            self.validate_configuration()
            raw_html = self.fetch_recruitment_page()
            raw_notifications = self.extract_notifications(raw_html)
            
            for raw_notif in raw_notifications:
                self.stats['total'] += 1
                try:
                    if not self.detect_changes(raw_notif):
                        continue # Unchanged
                    
                    normalized_job = self.normalize_data(raw_notif)
                    self.download_documents(normalized_job)
                    
                    if self.validate_records(normalized_job):
                        self.save_results(normalized_job)
                except Exception as e:
                    self.stats['failed'] += 1
                    logger.error(f"[{self.org_name}] Failed to process notification: {e}")
            
            self.generate_summary()
        except Exception as e:
            logger.error(f"[{self.org_name}] Scraper execution failed: {e}")
        finally:
            self.cleanup()
        return self.stats

    def initialize(self):
        logger.info(f"[{self.org_name}] Initializing scraper...")

    def validate_configuration(self):
        pass

    def fetch_recruitment_page(self):
        raise NotImplementedError("Subclasses must implement fetch_recruitment_page()")

    def extract_notifications(self, html) -> List[Dict]:
        raise NotImplementedError("Subclasses must implement extract_notifications()")

    def detect_changes(self, raw_notif: Dict) -> bool:
        changed = self.change_detector.has_changed(self.org_id, raw_notif)
        if changed:
            self.stats['new'] += 1
        return changed

    def normalize_data(self, raw_notif: Dict):
        return self.normalizer.normalize(self.org_id, raw_notif)

    def download_documents(self, job_obj):
        docs = self.download_manager.download_for_job(self.org_id, job_obj)
        self.stats['downloads'] += len(docs)

    def validate_records(self, job_obj) -> bool:
        return self.validator.validate_job(job_obj)

    def save_results(self, job_obj):
        logger.debug(f"[{self.org_name}] Saving result: {job_obj['title']}")
        # In actual phase, insert into database

    def generate_summary(self):
        logger.info(f"[{self.org_name}] Execution Summary: {self.stats}")

    def cleanup(self):
        logger.info(f"[{self.org_name}] Cleanup complete.")
