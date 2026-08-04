import uvicorn
import os
import sys
import time

def check_first_run():
    # Verify required directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    if not os.path.exists("data/govtrack.sqlite"):
        print("Initializing database...")
        # Mock DB initialization
        
    if not os.path.exists("config/config.json"):
        print("Creating default configuration...")

def start_backend():
    print("GovTrack Desktop Backend Initializing...")
    check_first_run()
    
    # In a real scenario, this would load the FastAPI app
    # uvicorn.run("api.main:app", host="127.0.0.1", port=8000)
    print("Application startup complete")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down backend...")
        sys.exit(0)

if __name__ == "__main__":
    start_backend()
