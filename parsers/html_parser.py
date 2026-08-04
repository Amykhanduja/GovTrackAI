from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class HTMLParser:
    def extract_text(self, file_path_or_html: str, is_file: bool = True) -> list:
        """Returns a list of tuples: [(page_num, text), ...]"""
        html = file_path_or_html
        if is_file:
            try:
                with open(file_path_or_html, "r", encoding="utf-8") as f:
                    html = f.read()
            except Exception as e:
                logger.error(f"Failed to read HTML file {file_path_or_html}: {e}")
                return []
        
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return [(1, text)]
