from parsers.base_parser import BaseParser
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class HTMLParser(BaseParser):
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

    def parse(self, source: str, **kwargs) -> dict:
        is_file = kwargs.get('is_file', True)
        try:
            pages = self.extract_text(source, is_file=is_file)
            text_str = "\n".join([p[1] for p in pages])
            return self._standard_response(
                parser_name="html",
                success=True,
                text=text_str,
                confidence=0.85
            )
        except Exception as e:
            logger.error(f"HTML parse failed: {e}")
            return self._standard_response(parser_name="html", success=False, confidence=0.0)
