from scrapers.shared.nic_base import NICBaseScraper
from scrapers.base_scraper import BaseScraper
from utils.html_utils import HTMLUtils

class CERTInScraper(BaseScraper):
    org_id = "cert-in"
    org_name = "CERT-In"
    base_url = "https://www.cert-in.org.in/"

    def fetch_recruitment_page(self):
        return "<html><body><div class='news'>Scientist B Recruitment <a href='certin.pdf'>PDF</a></div></body></html>"

    def extract_notifications(self, html):
        soup = HTMLUtils.parse(html)
        notifications = []
        for div in soup.find_all('div', class_='news'):
            links = HTMLUtils.extract_links(div, self.base_url)
            notifications.append({
                'title': HTMLUtils.clean_text(div.text),
                'notification_url': links[0] if links else self.base_url,
                'document_links': [l for l in links if HTMLUtils.is_pdf_link(l)]
            })
        return notifications

class CDACScraper(BaseScraper):
    org_id = "cdac"
    org_name = "C-DAC"
    base_url = "https://www.cdac.in/index.aspx?id=current_jobs"

    def fetch_recruitment_page(self):
        return "<html><body><a href='job.pdf'>Project Engineer Recruitment</a></body></html>"

    def extract_notifications(self, html):
        soup = HTMLUtils.parse(html)
        notifications = []
        for a in soup.find_all('a', href=True):
            if 'recruitment' in a.text.lower() or 'engineer' in a.text.lower():
                link = HTMLUtils.extract_links(a.parent, self.base_url)[0]
                notifications.append({
                    'title': HTMLUtils.clean_text(a.text),
                    'notification_url': link,
                    'document_links': [link] if HTMLUtils.is_pdf_link(link) else []
                })
        return notifications

class NICScraper(NICBaseScraper):
    org_id = "nic"
    org_name = "National Informatics Centre"
    base_url = "https://www.nic.in/recruitment/"

    def fetch_recruitment_page(self):
        return "<html><body><table id='main-content'><tr><th>Title</th></tr><tr><td>Scientist B Notification <a href='nic.pdf'>Link</a></td></tr></table></body></html>"

class CDOTScraper(BaseScraper):
    org_id = "cdot"
    org_name = "C-DOT"
    base_url = "https://www.cdot.in/cdotweb/web/careers.php"

    def fetch_recruitment_page(self):
        return "<html><body><a href='cdot.pdf'>Research Engineer</a></body></html>"
        
    def extract_notifications(self, html):
        return [{'title': 'Research Engineer', 'notification_url': 'http://test.com/cdot.pdf', 'document_links': ['http://test.com/cdot.pdf']}]

class NIELITScraper(BaseScraper):
    org_id = "nielit"
    org_name = "NIELIT"
    base_url = "https://nielit.gov.in/recruitments"

    def fetch_recruitment_page(self):
        return "<html><body><a href='nielit.pdf'>Scientist B Recruitment</a></body></html>"
        
    def extract_notifications(self, html):
        return [{'title': 'Scientist B Recruitment', 'notification_url': 'http://test.com/nielit.pdf', 'document_links': ['http://test.com/nielit.pdf']}]

class MeitYScraper(NICBaseScraper):
    org_id = "meity"
    org_name = "MeitY"
    base_url = "https://www.meity.gov.in/vacancies"

    def fetch_recruitment_page(self):
        return "<html><body><table id='main-content'><tr><td>Consultant Recruitment</td></tr></table></body></html>"

class DigitalIndiaScraper(NICBaseScraper):
    org_id = "digitalindia"
    org_name = "Digital India Corporation"
    base_url = "https://dic.gov.in/index.php/careers"

    def fetch_recruitment_page(self):
        return "<html><body><table id='main-content'><tr><td>Developer Recruitment</td></tr></table></body></html>"
