class CareerWorkspace:
    def __init__(self, db_manager=None):
        self.db = db_manager
        self.favorites = set()
        self.tags = {}
        self.watchlist = ['RBI', 'NIC', 'ISRO', 'CERT-In', 'DRDO']
        
    def add_favorite(self, job_id: int):
        self.favorites.add(job_id)

    def add_tag(self, job_id: int, tag: str):
        if job_id not in self.tags:
            self.tags[job_id] = []
        self.tags[job_id].append(tag)
        
    def get_watchlist(self) -> list:
        return self.watchlist
