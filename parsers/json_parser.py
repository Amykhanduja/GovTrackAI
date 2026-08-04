import json
import logging
from parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)

class JSONAPIParser(BaseParser):
    def parse(self, source: str, **kwargs) -> dict:
        try:
            with open(source, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            text_rep = json.dumps(data, indent=2)
            return self._standard_response(
                parser_name="json",
                success=True,
                text=text_rep,
                structured_data=data if isinstance(data, dict) else {"items": data},
                confidence=1.0
            )
        except Exception as e:
            logger.error(f"JSONAPIParser failed: {e}")
            return self._standard_response(parser_name="json", success=False, confidence=0.0)
