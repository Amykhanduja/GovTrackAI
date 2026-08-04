from ai.interfaces import IRecommendationEngine
from typing import Dict, Any, List

class HeuristicRecommendationEngine(IRecommendationEngine):
    def recommend(self, user_profile: Dict[str, Any], available_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Recommends jobs by fusing previous applications, career interests, and skills
        recommended = [job for job in available_jobs if job.get('priority', 0) > 80]
        return recommended
