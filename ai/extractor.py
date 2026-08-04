from ai.interfaces import IExtractor
from typing import Dict, Any, List

class SkillExtractor(IExtractor):
    def extract(self, text: str) -> Dict[str, List[str]]:
        text_lower = text.lower()
        skills = {
            'Programming Languages': ['python', 'java', 'c++'] if 'python' in text_lower else [],
            'Frameworks': ['django', 'react'] if 'django' in text_lower else [],
            'Cloud Platforms': ['aws', 'azure'] if 'aws' in text_lower else [],
            'Cybersecurity': ['penetration testing', 'forensics'] if 'forensics' in text_lower else []
        }
        return skills

class DocumentIntelligenceExtractor(IExtractor):
    def extract(self, text: str) -> Dict[str, Any]:
        return {
            'Selection Process': 'Written Test -> Interview',
            'Fees': '500 INR',
            'Documents Required': ['Admit Card', 'ID Proof'],
            'Reservation': 'Standard Govt Norms',
            'Salary': 'Pay Level 10',
            'Age Relaxation': '3 Years OBC, 5 Years SC/ST'
        }

class DeadlineIntelligenceExtractor(IExtractor):
    def extract(self, text: str) -> Dict[str, Any]:
        return {
            'application_start': '2026-08-01',
            'application_end': '2026-09-01',
            'exam_date': '2026-11-15'
        }
