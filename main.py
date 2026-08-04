import sys
import logging
from config.manager import ConfigManager
from logger.manager import setup_logging
from db.connection import DatabaseManager
from storage.cache_manager import CacheManager
from scheduler.manager import SchedulerManager
from core.plugin_manager import PluginManager

def main():
    print("Starting GovTrack AI Initialization...")
    
    # Load configuration
    config = ConfigManager()
    config.load_all()
    
    # Initialize logging
    setup_logging(config.get('logging'))
    logger = logging.getLogger('app')
    logger.info("Configuration loaded.")
    
    # Initialize database
    db = DatabaseManager(config.get('database'))
    db.initialize()
    logger.info("Database initialized.")
    
    # Initialize cache
    cache = CacheManager(config.get('cache'))
    logger.info("Cache initialized.")
    
    # Initialize scheduler
    scheduler = SchedulerManager(config.get('scheduler'))
    logger.info("Scheduler initialized.")
    
    # Initialize plugin manager
    plugin_manager = PluginManager()
    plugin_manager.discover_scrapers()
    logger.info("Plugin manager initialized.")
    
    print("Project status: READY")
    logger.info("System initialized successfully. Exiting cleanly.")
    sys.exit(0)

if __name__ == '__main__':
    main()
