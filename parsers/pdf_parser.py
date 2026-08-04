from parsers.base_parser import BaseParser
import pdfplumber
import fitz
import logging

logger = logging.getLogger(__name__)

class PDFParser(BaseParser):
    def extract_text(self, file_path: str) -> list:
        """Returns a list of tuples: [(page_num, text), ...]"""
        pages_text = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    t = page.extract_text()
                    if t: pages_text.append((i+1, t))
        except Exception as e:
            logger.warning(f"pdfplumber failed on {file_path}: {e}")
            try:
                with fitz.open(file_path) as doc:
                    for i, page in enumerate(doc):
                        t = page.get_text()
                        if t: pages_text.append((i+1, t))
            except Exception as e2:
                logger.error(f"PyMuPDF failed on {file_path}: {e2}")
        return pages_text

    def parse(self, source: str, **kwargs) -> dict:
        try:
            pages = self.extract_text(source)
            text_str = "\n".join([p[1] for p in pages])
            return self._standard_response(
                parser_name="pdf",
                success=True,
                text=text_str,
                confidence=0.95
            )
        except Exception as e:
            logger.error(f"PDF parse failed: {e}")
            return self._standard_response(parser_name="pdf", success=False, confidence=0.0)
