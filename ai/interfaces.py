from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class ISummarizer(ABC):
    @abstractmethod
    def summarize(self, text: str, metadata: Dict[str, Any] = None) -> str: pass

class IClassifier(ABC):
    @abstractmethod
    def classify(self, text: str) -> str: pass

class IExtractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> Dict[str, Any]: pass

class IEligibilityEngine(ABC):
    @abstractmethod
    def check_eligibility(self, job_requirements: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]: pass

class IPriorityEngine(ABC):
    @abstractmethod
    def calculate_score(self, job_data: Dict[str, Any], user_preferences: Dict[str, Any]) -> float: pass

class IDuplicateDetector(ABC):
    @abstractmethod
    def detect(self, text: str, metadata: Dict[str, Any] = None) -> str: pass

class IEmbeddingEngine(ABC):
    @abstractmethod
    def embed_document(self, text: str) -> List[float]: pass
    
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]: pass

class IRecommendationEngine(ABC):
    @abstractmethod
    def recommend(self, user_profile: Dict[str, Any], available_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]: pass
