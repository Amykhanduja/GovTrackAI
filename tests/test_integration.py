import unittest
from security.secrets import SecretsManager
from exceptions.errors import ConfigurationError

class TestIntegration(unittest.TestCase):
    def test_secrets_manager(self):
        mgr = SecretsManager()
        mgr.load_from_env()
        self.assertIsNotNone(mgr.get_secret('OPENAI_API_KEY'))
