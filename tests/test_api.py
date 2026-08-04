import unittest
from fastapi.testclient import TestClient
from api.main import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_jobs(self):
        response = self.client.get("/api/v1/jobs/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
        
    def test_get_analytics(self):
        response = self.client.get("/api/v1/analytics/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_jobs", response.json())
        
    def test_search_jobs(self):
        response = self.client.get("/api/v1/jobs/?search=rbi")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['org'], 'RBI')
