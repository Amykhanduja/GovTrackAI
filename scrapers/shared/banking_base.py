from scrapers.base_scraper import BaseScraper
from utils.html_utils import HTMLUtils

class BankingBaseScraper(BaseScraper):
    # Common logic for IBPS-based recruitment portals
    def extract_notifications(self, html):
        soup = HTMLUtils.parse(html)
        notifications = []
        
        # Many banking portals use standard table structures or div lists
        for row in soup.find_all('tr'):
            links = HTMLUtils.extract_links(row, self.base_url)
            text = HTMLUtils.clean_text(row.text)
            
            if 'recruitment' in text.lower() or 'notification' in text.lower() or links:
                notif = {
                    'title': text[:200],
                    'notification_url': links[0] if links else self.base_url,
                    'document_links': [l for l in links if HTMLUtils.is_pdf_link(l)]
                }
                notifications.append(notif)
        
        # Fallback to general links if table fails
        if not notifications:
            for a in soup.find_all('a', href=True):
                text = HTMLUtils.clean_text(a.text)
                if 'recruitment' in text.lower() or 'apply' in text.lower():
                    link = HTMLUtils.extract_links(a.parent, self.base_url)[0]
                    notifications.append({
                        'title': text,
                        'notification_url': link,
                        'document_links': [link] if HTMLUtils.is_pdf_link(link) else []
                    })
        return notifications
