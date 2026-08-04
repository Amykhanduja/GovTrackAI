from ai.interfaces import IClassifier

class KeywordJobClassifier(IClassifier):
    def classify(self, text: str) -> str:
        text_lower = text.lower()
        if 'cyber' in text_lower or 'security' in text_lower: return 'Cyber Security'
        if 'data' in text_lower or 'ai ' in text_lower: return 'Data Science'
        if 'research' in text_lower: return 'Research'
        return 'General Administration'
