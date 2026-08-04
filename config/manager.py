import os
import yaml
from core.exceptions import ConfigurationError

class ConfigManager:
    def __init__(self, config_dir='config/yaml'):
        self.config_dir = config_dir
        self._configs = {}

    def load_all(self):
        files = ['app.yaml', 'companies.yaml', 'scheduler.yaml', 
                 'notifications.yaml', 'excel.yaml', 'ai.yaml', 
                 'database.yaml', 'logging.yaml', 'cache.yaml']
        # In a real scenario, this reads YAML files
        for f in files:
            self._configs[f.replace('.yaml', '')] = {}

    def get(self, section):
        if section not in self._configs:
            raise ConfigurationError(f"Configuration section {section} not found")
        return self._configs.get(section, {})
