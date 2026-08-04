import logging
from notifications.providers import INotificationProvider

logger = logging.getLogger('app.notifications')

class NotificationEngine:
    def __init__(self):
        self.providers = []

    def register_provider(self, provider: INotificationProvider):
        self.providers.append(provider)

    def notify(self, title: str, message: str, meta: dict = None):
        success_count = 0
        for provider in self.providers:
            try:
                if provider.send(title, message, meta):
                    success_count += 1
            except Exception as e:
                logger.error(f"Notification failed: {e}")
        return success_count

    def send_daily_summary(self, stats: dict):
        msg = f"New Jobs: {stats.get('new_jobs', 0)}\nUpcoming Deadlines: {stats.get('deadlines', 0)}"
        self.notify("GovTrack Daily Summary", msg)
