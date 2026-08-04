from assistant.llm_providers import ILLMProvider
from assistant.memory import ConversationMemory
from assistant.rag_engine import RAGEngine
from assistant.career_coach import CareerCoach

class GovTrackAssistant:
    def __init__(self, llm: ILLMProvider, rag: RAGEngine):
        self.llm = llm
        self.rag = rag
        self.memory = ConversationMemory()
        self.coach = CareerCoach(llm)
        
    def ask(self, query: str) -> str:
        self.memory.add_user(query)
        
        # Simple routing
        if "skill" in query.lower() or "recommend" in query.lower():
            response = self.coach.recommend_skills({}, "Govt IT Officer")
        elif "interview" in query.lower():
            response = self.coach.interview_prep("NIC", "Scientist")
        else:
            response = self.rag.query(query)
            
        self.memory.add_assistant(response)
        return response
