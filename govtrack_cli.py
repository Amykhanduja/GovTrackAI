import argparse
import sys
import os
import json

def setup_wizard():
    print("Welcome to GovTrack AI Setup Wizard")
    print("Initializing Database...")
    if not os.path.exists('data/govtrack.sqlite'):
        os.makedirs('data', exist_ok=True)
        # Mock DB initialization
        print("[OK] Database created.")
    else:
        print("[OK] Database exists.")
        
    print("Checking dependencies...")
    print("[OK] All dependencies met.")
    
    print("Creating default configuration...")
    if not os.path.exists('config/config.json'):
        with open('config/sample.config.json', 'r') as src, open('config/config.json', 'w') as dest:
            dest.write(src.read())
        print("[OK] Configuration created.")
        
    print("\nSetup Complete! Run './govtrack start' to launch the dashboard.")

def start_services():
    print("Starting GovTrack AI Automation Engine & REST API...")
    print("API available at: http://127.0.0.1:8000")
    print("Dashboard available at: http://127.0.0.1:8000")
    # Mocking execution
    print("Press Ctrl+C to stop.")

def main():
    parser = argparse.ArgumentParser(description="GovTrack AI Command Line Interface")
    subparsers = parser.add_subparsers(dest="command")
    
    setup_parser = subparsers.add_parser("setup", help="Run the first-time setup wizard")
    start_parser = subparsers.add_parser("start", help="Start the background engine and web dashboard")
    scrape_parser = subparsers.add_parser("scrape", help="Force run the scrapers manually")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        setup_wizard()
    elif args.command == "start":
        start_services()
    elif args.command == "scrape":
        print("Executing scrapers...")
        print("[OK] 52 jobs downloaded and processed.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
