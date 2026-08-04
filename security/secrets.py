import os
import logging

logger = logging.getLogger('app.security')

class SecretsManager:
    """
    Manages API keys and sensitive environment variables safely,
    ensuring they are never logged or stored in plain text DBs.
    """
    def __init__(self):
        self._secrets = {}
        
    def load_from_env(self):
        # Mocks loading critical tokens (OpenAI, DB password, Telegram Bot)
        self._secrets['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'mock-key-do-not-use-in-prod')
        
    def get_secret(self, key: str) -> str:
        if key not in self._secrets:
            logger.warning(f"Attempted to access missing secret: {key}")
            return None
        return self._secrets[key]
