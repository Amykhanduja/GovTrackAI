import hashlib
import json

class ChangeDetector:
    def __init__(self):
        self.known_hashes = set() # In reality, read from DB/Cache

    def _generate_fingerprint(self, data: dict) -> str:
        # Sort keys to ensure consistent hashing
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    def has_changed(self, org_id: str, raw_notif: dict) -> bool:
        fingerprint = self._generate_fingerprint(raw_notif)
        key = f"{org_id}:{fingerprint}"
        if key in self.known_hashes:
            return False
        self.known_hashes.add(key)
        return True
