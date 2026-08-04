import unittest
from scrapers.plugins.batch_a.banking_finance import RBIScraper, SBIScraper, IBPSMasterScraper, NABARDScraper, SEBIScraper, SIDBIScraper, LICScraper, IRDAIScraper, PFRDAScraper

class TestBatch1(unittest.TestCase):
    def setUp(self):
        self.config = {}

    def _test_scraper(self, scraper_class):
        scraper = scraper_class(self.config)
        html = scraper.fetch_recruitment_page()
        notifs = scraper.extract_notifications(html)
        self.assertTrue(len(notifs) > 0)
        self.assertIn('title', notifs[0])

    def test_rbi(self): self._test_scraper(RBIScraper)
    def test_sbi(self): self._test_scraper(SBIScraper)
    def test_ibps(self): self._test_scraper(IBPSMasterScraper)
    def test_nabard(self): self._test_scraper(NABARDScraper)
    def test_sebi(self): self._test_scraper(SEBIScraper)
    def test_sidbi(self): self._test_scraper(SIDBIScraper)
    def test_lic(self): self._test_scraper(LICScraper)
    def test_irdai(self): self._test_scraper(IRDAIScraper)
    def test_pfrda(self): self._test_scraper(PFRDAScraper)
