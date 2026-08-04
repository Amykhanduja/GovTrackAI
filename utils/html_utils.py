import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class HTMLUtils:
    @staticmethod
    def parse(html):
        return BeautifulSoup(html, 'html.parser')

    @staticmethod
    def clean_text(text):
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def extract_links(soup, base_url=""):
        links = []
        for a in soup.find_all('a', href=True):
            links.append(urljoin(base_url, a['href']))
        return links

    @staticmethod
    def is_pdf_link(url):
        return url.lower().endswith('.pdf') or 'pdf' in url.lower()

    @staticmethod
    def parse_table(table_soup):
        headers = [HTMLUtils.clean_text(th.text) for th in table_soup.find_all('th')]
        rows = []
        for tr in table_soup.find_all('tr'):
            cells = [HTMLUtils.clean_text(td.text) for td in tr.find_all('td')]
            if cells:
                rows.append(dict(zip(headers, cells)) if headers else cells)
        return rows
