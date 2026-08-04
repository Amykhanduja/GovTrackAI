import os
import importlib
import inspect
import logging
from scrapers.base_scraper import BaseScraper
import pkgutil

logger = logging.getLogger('app.scraper_manager')

class ScraperManager:
    def __init__(self, config):
        self.config = config
        self.plugins = {}
        self.stats = {'total_run': 0, 'successful': 0, 'failed': 0}

    def discover_scrapers(self):
        import scrapers.plugins
        plugins_path = os.path.dirname(scrapers.plugins.__file__)
        
        for loader, name, is_pkg in pkgutil.walk_packages([plugins_path], prefix='scrapers.plugins.'):
            if not is_pkg:
                module = importlib.import_module(name)
                for member_name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseScraper) and obj is not BaseScraper:
                        org_id = getattr(obj, 'org_id', 'unknown')
                        self.plugins[org_id] = obj
                        
        logger.info(f"Discovered {len(self.plugins)} scraper plugins.")

    def run_one(self, org_id):
        if org_id not in self.plugins:
            logger.error(f"Scraper for {org_id} not found.")
            return None
        
        scraper_class = self.plugins[org_id]
        scraper = scraper_class(self.config.get(org_id, {}))
        
        self.stats['total_run'] += 1
        try:
            stats = scraper.execute()
            self.stats['successful'] += 1
            return stats
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"Execution failed for {org_id}: {e}")
            return None

    def run_multiple(self, org_ids):
        results = {}
        for org_id in org_ids:
            results[org_id] = self.run_one(org_id)
        return results

    def run_all(self):
        return self.run_multiple(self.plugins.keys())

    def get_execution_report(self):
        return self.stats
