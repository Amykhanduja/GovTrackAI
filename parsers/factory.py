from parsers.pdf_parser import PDFParser
from parsers.docx_parser import DOCXParser
from parsers.html_parser import HTMLParser
from parsers.txt_parser import TXTParser

class ParserFactory:
    @staticmethod
    def get_parser(file_path: str):
        ext = file_path.lower().split('.')[-1]
        if ext == 'pdf': return PDFParser()
        if ext == 'docx': return DOCXParser()
        if ext in ['htm', 'html']: return HTMLParser()
        if ext in ['txt', 'json']: return TXTParser()
        raise ValueError(f"Unsupported file type: {ext}")
