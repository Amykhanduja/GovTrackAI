import unittest
from scrapers.plugins.batch_b.tech_cyber import CERTInScraper, CDACScraper, NICScraper, CDOTScraper, NIELITScraper, MeitYScraper, DigitalIndiaScraper

class TestBatch2(unittest.TestCase):
    def setUp(self):
        self.config = {}

    def _test_scraper(self, scraper_class):
        scraper = scraper_class(self.config)
        html = scraper.fetch_recruitment_page()
        notifs = scraper.extract_notifications(html)
        self.assertTrue(len(notifs) > 0)
        self.assertIn('title', notifs[0])

    def test_certin(self): self._test_scraper(CERTInScraper)
    def test_cdac(self): self._test_scraper(CDACScraper)
    def test_nic(self): self._test_scraper(NICScraper)
    def test_cdot(self): self._test_scraper(CDOTScraper)
    def test_nielit(self): self._test_scraper(NIELITScraper)
    def test_meity(self): self._test_scraper(MeitYScraper)
    def test_digitalindia(self): self._test_scraper(DigitalIndiaScraper)
