import unittest
from scrapers.manager import ScraperManager
from utils.html_utils import HTMLUtils
from utils.change_detection import ChangeDetector
from utils.normalization import NormalizationEngine

class TestScraperFramework(unittest.TestCase):
    
    def test_plugin_discovery(self):
        manager = ScraperManager({})
        self.assertTrue(len(manager.registry.organizations) > 0)

    def test_html_utils(self):
        soup = HTMLUtils.parse("<a href='/test.pdf'>Link</a>")
        links = HTMLUtils.extract_links(soup, "http://demo.com")
        self.assertEqual(links[0], "http://demo.com/test.pdf")
        self.assertTrue(HTMLUtils.is_pdf_link(links[0]))

    def test_change_detection(self):
        detector = ChangeDetector()
        notif = {"title": "Test"}
        
        # First time should be changed
        self.assertTrue(detector.has_changed("org1", notif))
        
        # Second time should be unchanged
        self.assertFalse(detector.has_changed("org1", notif))

    def test_normalization(self):
        engine = NormalizationEngine()
        raw = {"title": "Test Job"}
        normalized = engine.normalize("org1", raw)
        
        self.assertEqual(normalized['org_id'], "org1")
        self.assertEqual(normalized['status'], "Active")
        self.assertEqual(normalized['title'], "Test Job")
