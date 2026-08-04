import logging
from parsers.base_parser import BaseParser
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class RSSParser(BaseParser):
    def parse(self, source: str, **kwargs) -> dict:
        try:
            tree = ET.parse(source)
            root = tree.getroot()
            
            items = []
            text_blocks = []
            
            for item in root.findall('.//item'):
                title = item.find('title')
                desc = item.find('description')
                link = item.find('link')
                
                t = title.text if title is not None else ""
                d = desc.text if desc is not None else ""
                l = link.text if link is not None else ""
                
                items.append({"title": t, "description": d, "link": l})
                text_blocks.append(f"{t}\n{d}")
                
            return self._standard_response(
                parser_name="rss",
                success=True,
                text="\n\n".join(text_blocks),
                structured_data={"items": items},
                confidence=0.9
            )
        except Exception as e:
            logger.error(f"RSSParser failed: {e}")
            return self._standard_response(parser_name="rss", success=False, confidence=0.0)
