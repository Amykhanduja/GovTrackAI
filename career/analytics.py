class CareerAnalytics:
    def __init__(self, db_manager=None):
        self.db = db_manager

    def generate_personal_statistics(self) -> dict:
        return {
            'applications_submitted': 15,
            'interview_rate': 0.20,
            'offer_rate': 0.05,
            'average_salary_applied': 1200000,
            'most_applied_org': 'NIC'
        }

    def analyze_skill_gaps(self, user_profile: dict, market_data: list) -> dict:
        # Mocks gap analysis
        user_skills = set(user_profile.get('skills', {}).get('programming', []))
        market_demand = {'Python', 'Cloud', 'Cybersecurity', 'Java'}
        
        missing = market_demand - user_skills
        return {
            'frequent_skills_demanded': list(market_demand),
            'your_gaps': list(missing),
            'recommendation': f"Prioritize learning {list(missing)[0]} to match 40% more jobs." if missing else "Skills align with market."
        }
