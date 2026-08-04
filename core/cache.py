import logging
from typing import Any
import time

logger = logging.getLogger('app.cache')

class MemoryCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.store = {}
        self.ttl = ttl_seconds

    def set(self, key: str, value: Any):
        self.store[key] = {'val': value, 'exp': time.time() + self.ttl}

    def get(self, key: str) -> Any:
        if key in self.store:
            if time.time() < self.store[key]['exp']:
                return self.store[key]['val']
            else:
                del self.store[key]
        return None
        
    def invalidate(self, key: str):
        if key in self.store:
            del self.store[key]
