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

from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    # High-performance settings for Desktop environments
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-64000") # 64MB cache
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA mmap_size=30000000000")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseManager:
    def __init__(self, config=None):
        self.engine = engine
        
    def initialize(self):
        Base.metadata.create_all(self.engine)
