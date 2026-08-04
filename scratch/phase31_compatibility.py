import os
import re

base_path = "/mnt/c/Users/khand/GovTrackAI/parsers"

# Update pdf_parser.py to inherit from BaseParser and add parse() method
pdf_path = os.path.join(base_path, "pdf_parser.py")
with open(pdf_path, "r") as f:
    pdf_content = f.read()

if "from parsers.base_parser import BaseParser" not in pdf_content:
    pdf_content = "from parsers.base_parser import BaseParser\n" + pdf_content
    pdf_content = pdf_content.replace("class PDFParser:", "class PDFParser(BaseParser):")
    
    parse_method = """
    def parse(self, source: str, **kwargs) -> dict:
        try:
            pages = self.extract_text(source)
            text_str = "\\n".join([p[1] for p in pages])
            return self._standard_response(
                parser_name="pdf",
                success=True,
                text=text_str,
                confidence=0.95
            )
        except Exception as e:
            logger.error(f"PDF parse failed: {e}")
            return self._standard_response(parser_name="pdf", success=False, confidence=0.0)
"""
    pdf_content += parse_method
    with open(pdf_path, "w") as f:
        f.write(pdf_content)

# Update html_parser.py to inherit from BaseParser and add parse() method
html_path = os.path.join(base_path, "html_parser.py")
with open(html_path, "r") as f:
    html_content = f.read()

if "from parsers.base_parser import BaseParser" not in html_content:
    html_content = "from parsers.base_parser import BaseParser\n" + html_content
    html_content = html_content.replace("class HTMLParser:", "class HTMLParser(BaseParser):")
    
    parse_method = """
    def parse(self, source: str, **kwargs) -> dict:
        is_file = kwargs.get('is_file', True)
        try:
            pages = self.extract_text(source, is_file=is_file)
            text_str = "\\n".join([p[1] for p in pages])
            return self._standard_response(
                parser_name="html",
                success=True,
                text=text_str,
                confidence=0.85
            )
        except Exception as e:
            logger.error(f"HTML parse failed: {e}")
            return self._standard_response(parser_name="html", success=False, confidence=0.0)
"""
    html_content += parse_method
    with open(html_path, "w") as f:
        f.write(html_content)

# Update text_parser.py to inherit from BaseParser and replace all 'except: pass'
txt_parser_path = os.path.join(base_path, "text_parser.py")
with open(txt_parser_path, "r") as f:
    text_parser_content = f.read()

text_parser_content = text_parser_content.replace("except: pass", "except Exception as e: logger.debug(f'Parsing error: {e}')")

if "from parsers.base_parser import BaseParser" not in text_parser_content:
    text_parser_content = "from parsers.base_parser import BaseParser\n" + text_parser_content
    text_parser_content = text_parser_content.replace("class TextParser:", "class TextParser(BaseParser):")
    
    parse_method = """
    def parse(self, source: str, **kwargs) -> dict:
        # source here is expected to be a list of pages [(page_num, text)] or plain text
        if isinstance(source, str):
            source = [(1, source)]
        try:
            structured = self.parse_all(source)
            text_combined = "\\n".join([p[1] for p in source])
            return self._standard_response(
                parser_name="text_field_extractor",
                success=True,
                text=text_combined,
                structured_data=structured,
                confidence=0.9
            )
        except Exception as e:
            logger.error(f"TextParser parse failed: {e}")
            return self._standard_response(parser_name="text_field_extractor", success=False, confidence=0.0)
"""
    text_parser_content += parse_method
    with open(txt_parser_path, "w") as f:
        f.write(text_parser_content)
