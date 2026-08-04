from scrapers.shared.generic_portal import GenericPortalScraper
from scrapers.registry import OrganizationRegistry
import logging

logger = logging.getLogger('app.batch_d')

def register_ministry_scrapers():
    registry = OrganizationRegistry("config/organizations.json")
    ministries = registry.get_by_category("MINISTRIES")
    
    scrapers = []
    for org in ministries:
        scraper = GenericPortalScraper(org)
        scrapers.append(scraper)
        logger.info(f"Registered dynamic scraper for {org['name']}")
    return scrapers
