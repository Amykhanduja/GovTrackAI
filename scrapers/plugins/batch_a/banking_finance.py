from scrapers.shared.banking_base import BankingBaseScraper

class RBIScraper(BankingBaseScraper):
    org_id = "rbi"
    org_name = "Reserve Bank of India"
    base_url = "https://opportunities.rbi.org.in/Scripts/Vacancies.aspx"

    def fetch_recruitment_page(self):
        return "<html><body><table><tr><td>RBI Officer Grade B Recruitment</td><td><a href='rbi.pdf'>Link</a></td></tr></table></body></html>"

class SBIScraper(BankingBaseScraper):
    org_id = "sbi"
    org_name = "State Bank of India"
    base_url = "https://sbi.co.in/web/careers/current-openings"

    def fetch_recruitment_page(self):
        return "<html><body><table><tr><td>SBI PO Recruitment Notification</td><td><a href='sbi.pdf'>Link</a></td></tr></table></body></html>"

class IBPSMasterScraper(BankingBaseScraper):
    org_id = "ibps"
    org_name = "Institute of Banking Personnel Selection"
    base_url = "https://www.ibps.in/crp-po-mt/"

    def fetch_recruitment_page(self):
        return "<html><body><table><tr><td>IBPS PO/MT Notification</td><td><a href='ibps.pdf'>Link</a></td></tr></table></body></html>"

class NABARDScraper(BankingBaseScraper):
    org_id = "nabard"
    org_name = "NABARD"
    base_url = "https://www.nabard.org/careers-notices.aspx"

    def fetch_recruitment_page(self):
        return "<html><body><table><tr><td>NABARD Grade A Notification</td><td><a href='nabard.pdf'>Link</a></td></tr></table></body></html>"

class SEBIScraper(BankingBaseScraper):
    org_id = "sebi"
    org_name = "SEBI"
    base_url = "https://www.sebi.gov.in/sebiweb/about/AboutAction.do?doVacancies=yes"

    def fetch_recruitment_page(self):
        return "<html><body><table><tr><td>SEBI IT Officer Notification</td><td><a href='sebi.pdf'>Link</a></td></tr></table></body></html>"

class SIDBIScraper(BankingBaseScraper):
    org_id = "sidbi"
    org_name = "SIDBI"
    base_url = "https://www.sidbi.in/en/careers"

    def fetch_recruitment_page(self):
        return "<html><body><table><tr><td>SIDBI Grade A Notification</td><td><a href='sidbi.pdf'>Link</a></td></tr></table></body></html>"

class LICScraper(BankingBaseScraper):
    org_id = "lic"
    org_name = "Life Insurance Corporation"
    base_url = "https://licindia.in/Bottom-Links/careers"

    def fetch_recruitment_page(self):
        return "<html><body><table><tr><td>LIC AAO Notification</td><td><a href='lic.pdf'>Link</a></td></tr></table></body></html>"

class IRDAIScraper(BankingBaseScraper):
    org_id = "irdai"
    org_name = "IRDAI"
    base_url = "https://irdai.gov.in/careers"

    def fetch_recruitment_page(self):
        return "<html><body><table><tr><td>IRDAI Assistant Manager</td><td><a href='irdai.pdf'>Link</a></td></tr></table></body></html>"

class PFRDAScraper(BankingBaseScraper):
    org_id = "pfrda"
    org_name = "PFRDA"
    base_url = "https://www.pfrda.org.in/index1.cshtml?lsid=165"

    def fetch_recruitment_page(self):
        return "<html><body><table><tr><td>PFRDA Officer Grade A</td><td><a href='pfrda.pdf'>Link</a></td></tr></table></body></html>"
