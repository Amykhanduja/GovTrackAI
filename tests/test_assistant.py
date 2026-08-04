import unittest
from assistant.llm_providers import LocalOllamaProvider
from assistant.vector_db import LocalVectorStore
from assistant.rag_engine import RAGEngine
from assistant.chat import GovTrackAssistant

class TestAssistant(unittest.TestCase):
    def setUp(self):
        self.llm = LocalOllamaProvider()
        self.vdb = LocalVectorStore()
        
        # Seed DB
        self.vdb.add_documents([{"title": "NIC Scientist B", "skills": "Python"}], [[0.5]*4096])
        
        self.rag = RAGEngine(self.llm, self.vdb)
        self.assistant = GovTrackAssistant(self.llm, self.rag)

    def test_rag_query(self):
        res = self.assistant.ask("Show jobs requiring Python")
        self.assertEqual(res, "Ollama Llama3 Mock Response")
        self.assertIn("user", self.assistant.memory.messages[0]['role'])

    def test_coach(self):
        res = self.assistant.ask("Recommend skills for NIC")
        self.assertEqual(res, "Ollama Llama3 Mock Response")
