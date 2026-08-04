import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

engine = create_engine('sqlite:///govtrack.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseManager:
    def __init__(self, config=None):
        self.engine = engine
        
    def initialize(self):
        Base.metadata.create_all(self.engine)
