import logging
from parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)

class TXTParser(BaseParser):
    def parse(self, source: str, **kwargs) -> dict:
        try:
            with open(source, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            return self._standard_response(
                parser_name="txt",
                success=True,
                text=content,
                confidence=0.9
            )
        except Exception as e:
            logger.error(f"TXTParser failed: {e}")
            return self._standard_response(parser_name="txt", success=False, confidence=0.0)
