import uvicorn
import os
import sys

def get_base_dir():
    # If bundled by PyInstaller, sys._MEIPASS is the temp directory where resources are extracted.
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_user_data_dir():
    # Store dynamic data in user's AppData/Home instead of the installation folder
    if sys.platform == "win32":
        base = os.getenv("APPDATA")
    else:
        base = os.path.expanduser("~")
    
    app_dir = os.path.join(base, "GovTrackAI")
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def check_first_run():
    user_data = get_user_data_dir()
    os.makedirs(os.path.join(user_data, "data"), exist_ok=True)
    os.makedirs(os.path.join(user_data, "logs"), exist_ok=True)
    
    db_path = os.path.join(user_data, "data", "govtrack.sqlite")
    if not os.path.exists(db_path):
        print(f"Initializing database at {db_path}...")
        # SQLAlchemy will automatically create it.

def start_backend():
    print("GovTrack Desktop Backend Initializing...")
    
    # We need to change cwd to sys._MEIPASS so that FastAPI static files and relative imports work.
    # But wait, data should be saved to AppData.
    # We'll just change to MEIPASS so it finds frontend/ etc.
    base_dir = get_base_dir()
    os.chdir(base_dir)
    
    check_first_run()
    
    # Start the actual FastAPI app
    print("Starting uvicorn server on port 8000...")
    # NOTE: uvicorn doesn't work well with string "api.main:app" inside PyInstaller without some hacks, 
    # so we import the app and pass the object directly.
    from api.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    start_backend()
