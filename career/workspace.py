import logging

logger = logging.getLogger('app.career.workspace')

class CareerWorkspace:
    def __init__(self, db_manager=None):
        self.db = db_manager
        # Fetch dynamically from DB. No hardcoded seed data.
        self.watchlist = []

    def get_active_workspaces(self):
        return []

    def add_to_watchlist(self, org_name: str):
        if org_name not in self.watchlist:
            self.watchlist.append(org_name)
