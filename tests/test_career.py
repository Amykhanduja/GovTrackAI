import unittest
import os
from career.profile import UserProfileManager
from career.search import SmartSearchEngine
from career.documents import DocumentRepository
from career.workspace import CareerWorkspace
from career.application_tracker import ApplicationTracker
from career.analytics import CareerAnalytics

class TestCareerManagement(unittest.TestCase):
    def setUp(self):
        self.test_profile = 'config/test_profile.json'
        self.profile_mgr = UserProfileManager(self.test_profile)
        
    def test_profile_management(self):
        self.profile_mgr.update_profile('personal', {'name': 'Test User'})
        self.assertEqual(self.profile_mgr.profile['personal']['name'], 'Test User')
        
    def test_smart_search(self):
        search = SmartSearchEngine(None)
        results = search.search("Cyber Security fresher")
        self.assertTrue(len(results) > 0)
        
    def test_application_tracker(self):
        tracker = ApplicationTracker(None)
        tracker.track_application(101, 'Submitted', {'fee': 500})
        self.assertEqual(tracker.applications[101]['status'], 'Submitted')
        with self.assertRaises(ValueError):
            tracker.track_application(101, 'Invalid Status')
            
    def test_analytics_and_skill_gap(self):
        analytics = CareerAnalytics(None)
        gaps = analytics.analyze_skill_gaps(self.profile_mgr.profile, [])
        self.assertIn('recommendation', gaps)
        self.assertIn('your_gaps', gaps)

    def tearDown(self):
        if os.path.exists(self.test_profile):
            os.remove(self.test_profile)
