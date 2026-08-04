from scrapers.base_scraper import BaseScraper

class DemoScraper(BaseScraper):
    org_id = "demo_org"
    org_name = "Mock Demonstration Organization"

    def fetch_recruitment_page(self):
        # Simulate fetching HTML
        return "<html><body><h1>Careers</h1><a href='http://example.com/notif.pdf'>Download Notif</a></body></html>"

    def extract_notifications(self, html):
        # Simulate extracting data
        return [
            {
                'title': 'Demo Software Engineer',
                'notification_url': 'http://example.com/notif.pdf',
                'document_links': ['http://example.com/notif.pdf']
            }
        ]
