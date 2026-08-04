from scrapers.base_scraper import BaseScraper

class ISROScraper(BaseScraper):
    org_id = "isro"
    org_name = "ISRO"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'ISRO SC', 'notification_url': 'url', 'document_links': []}]

class DRDOScraper(BaseScraper):
    org_id = "drdo"
    org_name = "DRDO RAC"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'DRDO Sci B', 'notification_url': 'url', 'document_links': []}]

class BARCScraper(BaseScraper):
    org_id = "barc"
    org_name = "BARC"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'OCES/DGFS', 'notification_url': 'url', 'document_links': []}]

class NPCILScraper(BaseScraper):
    org_id = "npcil"
    org_name = "NPCIL"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'ET CS', 'notification_url': 'url', 'document_links': []}]

class HALScraper(BaseScraper):
    org_id = "hal"
    org_name = "HAL"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'MT CS', 'notification_url': 'url', 'document_links': []}]

class BELScraper(BaseScraper):
    org_id = "bel"
    org_name = "BEL"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'Proj Eng', 'notification_url': 'url', 'document_links': []}]

class ECILScraper(BaseScraper):
    org_id = "ecil"
    org_name = "ECIL"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'Tech Officer', 'notification_url': 'url', 'document_links': []}]

class GAILScraper(BaseScraper):
    org_id = "gail"
    org_name = "GAIL"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'ET', 'notification_url': 'url', 'document_links': []}]

class ONGCScraper(BaseScraper):
    org_id = "ongc"
    org_name = "ONGC"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'Prog Officer', 'notification_url': 'url', 'document_links': []}]

class NTPCScraper(BaseScraper):
    org_id = "ntpc"
    org_name = "NTPC"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'ET IT', 'notification_url': 'url', 'document_links': []}]

class PowerGridScraper(BaseScraper):
    org_id = "powergrid"
    org_name = "PowerGrid"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'ET CS', 'notification_url': 'url', 'document_links': []}]

class NHPCScraper(BaseScraper):
    org_id = "nhpc"
    org_name = "NHPC"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'ET IT', 'notification_url': 'url', 'document_links': []}]

class NLCIndiaScraper(BaseScraper):
    org_id = "nlc"
    org_name = "NLC India"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'GET CS', 'notification_url': 'url', 'document_links': []}]

class CoalIndiaScraper(BaseScraper):
    org_id = "coalindia"
    org_name = "Coal India"
    def fetch_recruitment_page(self): return "<html></html>"
    def extract_notifications(self, html): return [{'title': 'MT Sys', 'notification_url': 'url', 'document_links': []}]
