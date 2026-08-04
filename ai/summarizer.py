from ai.interfaces import ISummarizer
from typing import Dict, Any

class RuleBasedSummarizer(ISummarizer):
    def summarize(self, text: str, metadata: Dict[str, Any] = None) -> str:
        meta = metadata or {}
        return f"Role: {meta.get('post', 'Unknown')}. Salary: {meta.get('salary', 'NA')}. Deadline: {meta.get('deadline', 'NA')}."
