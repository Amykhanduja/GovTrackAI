from ai.interfaces import IEligibilityEngine
from typing import Dict, Any

class ConfigurableEligibilityEngine(IEligibilityEngine):
    def check_eligibility(self, job_requirements: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        # Evaluates match against user profile config
        status = "Eligible"
        reason = "Meets all criteria."
        
        req_degrees = job_requirements.get('degrees', [])
        user_degrees = user_profile.get('degrees', [])
        
        if req_degrees and not any(d in user_degrees for d in req_degrees):
            status = "Not Eligible"
            reason = f"Missing required degrees: {req_degrees}"
            
        return {'status': status, 'reason': reason}
