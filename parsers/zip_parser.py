import zipfile
import logging
import os
from parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)

class ZIPParser(BaseParser):
    def parse(self, source: str, **kwargs) -> dict:
        try:
            attachments = []
            text_blocks = []
            
            with zipfile.ZipFile(source, 'r') as z:
                for file_info in z.infolist():
                    attachments.append(file_info.filename)
                    if file_info.filename.endswith('.txt'):
                        try:
                            content = z.read(file_info.filename).decode('utf-8')
                            text_blocks.append(content)
                        except Exception as decode_e:
                            logger.warning(f"Could not decode text file in zip: {decode_e}")
                            
            return self._standard_response(
                parser_name="zip",
                success=True,
                text="\n".join(text_blocks),
                attachments=attachments,
                confidence=0.8
            )
        except Exception as e:
            logger.error(f"ZIPParser failed: {e}")
            return self._standard_response(parser_name="zip", success=False, confidence=0.0)
