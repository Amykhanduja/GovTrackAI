import sqlalchemy
from sqlalchemy import create_engine
from .models import Base

class DatabaseManager:
    def __init__(self, config):
        conn_str = config.get('connection_string', 'sqlite:///govtrack.db')
        self.engine = create_engine(conn_str)
        
    def initialize(self):
        Base.metadata.create_all(self.engine)
