import logging
from ai.interfaces import *
from ai.summarizer import RuleBasedSummarizer
from ai.classifier import KeywordJobClassifier
from ai.extractor import SkillExtractor, DocumentIntelligenceExtractor, DeadlineIntelligenceExtractor
from ai.eligibility import ConfigurableEligibilityEngine
from ai.scorer import MultiFactorPriorityEngine
from ai.duplicate_detector import SignatureDuplicateDetector
from ai.semantic_search import VectorDatabaseArchitecture
from ai.recommendation import HeuristicRecommendationEngine

logger = logging.getLogger('app.ai_pipeline')

class DocumentProcessingPipeline:
    def __init__(self, config, dependencies: dict = None):
        self.config = config
        deps = dependencies or {}
        
        # Dependency Injection architecture allowing future replacement with LLM implementations
        self.summarizer: ISummarizer = deps.get('summarizer', RuleBasedSummarizer())
        self.classifier: IClassifier = deps.get('classifier', KeywordJobClassifier())
        self.skill_extractor: IExtractor = deps.get('skill_extractor', SkillExtractor())
        self.doc_extractor: IExtractor = deps.get('doc_extractor', DocumentIntelligenceExtractor())
        self.deadline_extractor: IExtractor = deps.get('deadline_extractor', DeadlineIntelligenceExtractor())
        
        self.eligibility_engine: IEligibilityEngine = deps.get('eligibility_engine', ConfigurableEligibilityEngine())
        self.priority_engine: IPriorityEngine = deps.get('priority_engine', MultiFactorPriorityEngine())
        self.duplicate_detector: IDuplicateDetector = deps.get('duplicate_detector', SignatureDuplicateDetector())
        self.embedding_engine: IEmbeddingEngine = deps.get('embedding_engine', VectorDatabaseArchitecture())
        self.recommendation_engine: IRecommendationEngine = deps.get('recommendation_engine', HeuristicRecommendationEngine())

    def process_document(self, raw_text: str, metadata: dict = None) -> dict:
        metadata = metadata or {}
        
        doc_status = self.duplicate_detector.detect(raw_text)
        if doc_status == 'Duplicate':
            return {'status': 'Duplicate'}
            
        category = self.classifier.classify(raw_text)
        skills = self.skill_extractor.extract(raw_text)
        intelligence = self.doc_extractor.extract(raw_text)
        dates = self.deadline_extractor.extract(raw_text)
        
        eligibility = self.eligibility_engine.check_eligibility({'degrees': ['B.Tech']}, self.config.get('user_profile', {}))
        
        priority = self.priority_engine.calculate_score({'eligibility_status': eligibility['status']}, self.config.get('user_preferences', {}))
        summary = self.summarizer.summarize(raw_text, {'post': category, 'salary': intelligence.get('Salary')})
        
        # Prepare for Semantic Search automatically
        vector = self.embedding_engine.embed_document(summary)
        
        return {
            'status': 'Processed',
            'doc_status': doc_status,
            'category': category,
            'skills': skills,
            'intelligence': intelligence,
            'dates': dates,
            'eligibility': eligibility,
            'priority': priority,
            'summary': summary,
            'vector_length': len(vector)
        }
