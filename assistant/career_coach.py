class CareerCoach:
    def __init__(self, llm_provider):
        self.llm = llm_provider
        
    def recommend_skills(self, user_profile: dict, target_role: str) -> str:
        prompt = f"Analyze skills for {target_role} compared to profile {user_profile}. Recommend 3 missing skills."
        return self.llm.generate(prompt)
        
    def interview_prep(self, organization: str, role: str) -> str:
        prompt = f"Provide 5 common technical interview questions for {role} at {organization}."
        return self.llm.generate(prompt)
