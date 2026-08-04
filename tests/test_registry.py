import unittest
from scrapers.registry import OrganizationRegistry
from scrapers.shared.generic_portal import GenericPortalScraper
import os

class TestOrganizationRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = OrganizationRegistry("config/organizations.json")
        
    def test_load_registry(self):
        self.assertTrue(len(self.registry.organizations) > 0)
        
    def test_domain_filtering(self):
        foreign_orgs = self.registry.get_by_domain("foreign_lang")
        self.assertTrue(any(org['id'] == 'mea' for org in foreign_orgs))
        
    def test_markdown_generation(self):
        self.registry.generate_markdown_report("docs/test_supported.md")
        self.assertTrue(os.path.exists("docs/test_supported.md"))
        
    def test_generic_scraper(self):
        org = self.registry.organizations[0]
        scraper = GenericPortalScraper(org)
        res = scraper.scrape()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['org'], org['name'])
