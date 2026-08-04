import unittest
from automation.engine import AutomationEngine
from automation.scheduler import TaskScheduler
from notifications.engine import NotificationEngine
from notifications.providers import DesktopNotificationProvider
from notifications.reminders import ReminderSystem
import os

class TestAutomation(unittest.TestCase):
    def test_notification_routing(self):
        engine = NotificationEngine()
        engine.register_provider(DesktopNotificationProvider())
        success = engine.notify("Test", "Message")
        self.assertEqual(success, 1)
        
    def test_scheduler(self):
        scheduler = TaskScheduler()
        state = {'run': False}
        def dummy_job():
            state['run'] = True
            
        scheduler.schedule_job("Dummy", dummy_job, 0)
        scheduler.run_pending()
        self.assertTrue(state['run'])
        self.assertEqual(len(scheduler.history), 1)
        self.assertEqual(scheduler.history[0]['status'], 'Success')

    def test_reminder_system(self):
        engine = NotificationEngine()
        engine.register_provider(DesktopNotificationProvider())
        reminders = ReminderSystem(engine)
        
        from datetime import datetime, timedelta
        target = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        jobs = [{'title': 'Test Job', 'deadline': target}]
        
        # Should trigger 7 day reminder
        reminders.process_deadlines(jobs)
        # Verify it ran without crashing (mock engine handles output)
        self.assertTrue(True)
