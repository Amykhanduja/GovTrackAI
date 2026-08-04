from scrapers.base_scraper import BaseScraper
from utils.html_utils import HTMLUtils

class NICBaseScraper(BaseScraper):
    # Common logic for NIC S3WaaS portals (Ministries, State Govts)
    def extract_notifications(self, html):
        soup = HTMLUtils.parse(html)
        notifications = []
        
        tables = soup.find_all('table')
        for table in tables:
            parsed_table = HTMLUtils.parse_table(table)
            for row in parsed_table:
                title = ""
                if isinstance(row, dict):
                    title = row.get('Title', '') or row.get('Description', '') or str(row)
                elif isinstance(row, list) and row:
                    title = row[0]
                
                if title:
                    notifications.append({
                        'title': title,
                        'notification_url': self.base_url,
                        'document_links': []
                    })
        return notifications
