import unittest
from ai.pipeline import DocumentProcessingPipeline

class TestAIPipeline(unittest.TestCase):
    def setUp(self):
        self.config = {
            'user_profile': {'degrees': ['B.Tech']},
            'user_preferences': {'preferred_location': 'Delhi'}
        }
        self.pipeline = DocumentProcessingPipeline(self.config)

    def test_full_pipeline(self):
        text = "Recruitment for Cyber Security Engineer. Python required. B.Tech mandatory."
        result = self.pipeline.process_document(text)
        
        self.assertEqual(result['status'], 'Processed')
        self.assertEqual(result['category'], 'Cyber Security')
        self.assertTrue('Programming Languages' in result['skills'])
        self.assertEqual(result['eligibility']['status'], 'Eligible')
        self.assertTrue(result['priority'] > 50.0)
        self.assertEqual(result['vector_length'], 768)
