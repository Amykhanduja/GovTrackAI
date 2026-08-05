import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

import os
import sys

# Determine database path
if getattr(sys, 'frozen', False):
    if sys.platform == "win32":
        base = os.getenv("APPDATA")
    else:
        base = os.path.expanduser("~")
    db_dir = os.path.join(base, "GovTrackAI", "data")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "govtrack.db")
else:
    db_path = "govtrack.db"

engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseManager:
    def __init__(self, config=None):
        self.engine = engine
        
    def initialize(self):
        Base.metadata.create_all(self.engine)
