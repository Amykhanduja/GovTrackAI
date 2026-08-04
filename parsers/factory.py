import os
import logging
from parsers.base_parser import BaseParser

# Lazy loading to prevent circular imports
logger = logging.getLogger(__name__)

class ParserFactory:
    @staticmethod
    def get_parser(file_path_or_url: str) -> BaseParser:
        """Automatically detect file type and return the correct parser instance."""
        ext = file_path_or_url.lower().split('.')[-1].split('?')[0]
        
        if ext == 'pdf':
            from parsers.pdf_parser import PDFParser
            return PDFParser()
        elif ext in ['html', 'htm', 'php', 'aspx']:
            from parsers.html_parser import HTMLParser
            return HTMLParser()
        elif ext == 'json':
            from parsers.json_parser import JSONAPIParser
            return JSONAPIParser()
        elif ext == 'xml' or ext == 'rss':
            from parsers.rss_parser import RSSParser
            return RSSParser()
        elif ext == 'zip':
            from parsers.zip_parser import ZIPParser
            return ZIPParser()
        elif ext == 'docx':
            from parsers.docx_parser import DOCXParser
            return DOCXParser()
        elif ext == 'txt':
            from parsers.txt_parser import TXTParser
            return TXTParser()
        
        logger.warning(f"Unsupported extension '{ext}'. Defaulting to TXTParser.")
        from parsers.txt_parser import TXTParser
        return TXTParser()
