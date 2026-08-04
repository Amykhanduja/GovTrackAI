from abc import ABC, abstractmethod

class INotificationProvider(ABC):
    @abstractmethod
    def send(self, title: str, message: str, meta: dict = None) -> bool: pass

class DesktopNotificationProvider(INotificationProvider):
    def send(self, title: str, message: str, meta: dict = None) -> bool:
        # Mock desktop notification
        return True

class TelegramNotificationProvider(INotificationProvider):
    def send(self, title: str, message: str, meta: dict = None) -> bool:
        # Mock telegram HTTP call
        return True

class WebhookNotificationProvider(INotificationProvider):
    def send(self, title: str, message: str, meta: dict = None) -> bool:
        # Mock webhook POST
        return True
