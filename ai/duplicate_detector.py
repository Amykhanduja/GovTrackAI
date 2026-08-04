from ai.interfaces import IDuplicateDetector
from typing import Dict, Any

class SignatureDuplicateDetector(IDuplicateDetector):
    def detect(self, text: str, metadata: Dict[str, Any] = None) -> str:
        # Returns 'Unique', 'Duplicate', 'Corrigendum', 'Updated'
        if 'corrigendum' in text.lower():
            return 'Corrigendum'
        if hash(text[:100]) % 2 == 0: # Mock logic
            return 'Unique'
        return 'Unique' # Defaulting for tests
