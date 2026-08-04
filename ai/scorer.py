from ai.interfaces import IPriorityEngine
from typing import Dict, Any

class MultiFactorPriorityEngine(IPriorityEngine):
    def calculate_score(self, job_data: Dict[str, Any], user_preferences: Dict[str, Any]) -> float:
        score = 50.0
        
        if job_data.get('eligibility_status') == 'Eligible':
            score += 20.0
            
        if user_preferences.get('preferred_location') in job_data.get('locations', []):
            score += 15.0
            
        # Add score for high salary, urgent deadlines, matching career relevance...
        return min(score, 100.0)
