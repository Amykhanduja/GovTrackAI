import json
import logging
import os

logger = logging.getLogger('app.domain_manager')

class DomainManager:
    def __init__(self, config_path="config/domains.json"):
        self.config_path = config_path
        self.domains = self._load_domains()
        self.active_domain = None

    def _load_domains(self) -> dict:
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, 'r') as f:
            data = json.load(f)
            return {d['id']: d for d in data.get('domains', [])}

    def set_active_domain(self, domain_id: str):
        if domain_id not in self.domains:
            raise ValueError(f"Domain {domain_id} not found.")
        self.active_domain = domain_id
        logger.info(f"Switched active domain to: {self.domains[domain_id]['name']}")

    def get_active_domain(self) -> dict:
        if not self.active_domain:
            return None
        return self.domains[self.active_domain]
        
    def classify_job(self, text: str, org: str) -> list:
        # Evaluates which domains a job belongs to based on keywords/orgs
        assigned = []
        text_lower = text.lower()
        for d_id, domain in self.domains.items():
            if org in domain.get('orgs', []):
                assigned.append(d_id)
                continue
            if any(k in text_lower for k in domain.get('keywords', [])):
                assigned.append(d_id)
        return assigned
