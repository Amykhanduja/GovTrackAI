import json
import os
import logging

logger = logging.getLogger('app.career.profile')

class UserProfileManager:
    def __init__(self, profile_path: str = 'config/profile.json'):
        self.profile_path = profile_path
        self.profile = self._load_profile()

    def _load_profile(self) -> dict:
        if os.path.exists(self.profile_path):
            with open(self.profile_path, 'r') as f:
                return json.load(f)
        return self._default_profile()

    def _default_profile(self) -> dict:
        # Absolutely NO hardcoded placeholder tracking lists!
        return {
            'personal': {'name': '', 'age': None, 'languages': []},
            'education': {'degree': '', 'specialization': '', 'graduation_year': None, 'cgpa': None},
            'skills': {'programming': [], 'certifications': []},
            'preferences': {'organizations': [], 'locations': [], 'expected_salary': None},
            'career': {'experience_years': 0, 'gate_score': None}
        }

    def update_profile(self, section: str, data: dict):
        if section in self.profile:
            self.profile[section].update(data)
            self._save()
            
    def _save(self):
        os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
        with open(self.profile_path, 'w') as f:
            json.dump(self.profile, f, indent=4)
