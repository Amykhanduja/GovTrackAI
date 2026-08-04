import unittest
from core.domain_manager import DomainManager

class TestMultiDomain(unittest.TestCase):
    def setUp(self):
        self.mgr = DomainManager("config/domains.json")
        
    def test_domain_loading(self):
        self.assertIn("cyber_tech", self.mgr.domains)
        self.assertIn("foreign_lang", self.mgr.domains)
        
    def test_job_classification(self):
        cyber_job = "Required Python and Cloud expert"
        lang_job = "Required French Translator"
        dual_job = "Cyber Security Expert fluent in Japanese"
        
        self.assertIn("cyber_tech", self.mgr.classify_job(cyber_job, "NIC"))
        self.assertIn("foreign_lang", self.mgr.classify_job(lang_job, "Embassy"))
        
        dual_class = self.mgr.classify_job(dual_job, "Unknown")
        self.assertIn("cyber_tech", dual_class)
        self.assertIn("foreign_lang", dual_class)
        
    def test_domain_isolation(self):
        self.mgr.set_active_domain("foreign_lang")
        self.assertEqual(self.mgr.get_active_domain()['name'], "Foreign Languages")
