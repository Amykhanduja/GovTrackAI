from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseParser(ABC):
    @abstractmethod
    def parse(self, source, **kwargs) -> dict:
        """
        Parse the source (file path or content) and return a standardized dictionary.
        """
        raise NotImplementedError("Subclasses must implement parse()")

    def _standard_response(self, parser_name: str, success: bool = True, text: str = "", metadata: dict = None, structured_data: dict = None, tables: list = None, attachments: list = None, confidence: float = 1.0) -> dict:
        return {
            "success": success,
            "parser": parser_name,
            "metadata": metadata or {},
            "text": text,
            "structured_data": structured_data or {},
            "tables": tables or [],
            "attachments": attachments or [],
            "confidence": confidence
        }
