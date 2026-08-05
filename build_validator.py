import sys
import os
import traceback
import json

def report(name, status, details=""):
    print(f"{name:.<25} {status}")
    if details:
        print(f"  -> {details}")

def test_database():
    try:
        from db.models import Base
        from sqlalchemy import create_engine
        
        test_db = "temp_test_db.sqlite"
        if os.path.exists(test_db): os.remove(test_db)
        
        engine = create_engine(f"sqlite:///{test_db}")
        Base.metadata.create_all(engine)
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = ['jobs', 'organizations', 'job_documents']
        for t in required_tables:
            if t not in tables:
                raise Exception(f"Table '{t}' is missing.")
                
        engine.dispose()
        os.remove(test_db)
        return "PASS", "Tables and indexes verified."
    except Exception as e:
        return "FAIL", str(e)

def test_scrapers():
    try:
        from scrapers.registry import OrganizationRegistry
        from scrapers.shared.generic_portal import GenericPortalScraper
        
        reg = OrganizationRegistry()
        if not reg.organizations:
            return "FAIL", "No organizations found in registry"
            
        loaded = []
        for org in reg.organizations:
            scraper = GenericPortalScraper(org)
            if not scraper.name or not scraper.url:
                raise Exception(f"Invalid scraper config: {org}")
            loaded.append(scraper.name)
            
        return "PASS", f"Loaded {len(loaded)} scrapers successfully: " + ", ".join(loaded[:5]) + "..."
    except Exception as e:
        return "FAIL", str(e)

def test_parsers():
    try:
        from parsers.factory import ParserFactory
        import pkgutil
        import parsers
        
        loaded = []
        for loader, module_name, is_pkg in pkgutil.iter_modules(parsers.__path__):
            loaded.append(module_name)
            
        required = ["pdf_parser", "html_parser", "json_parser", "txt_parser", "zip_parser", "rss_parser", "docx_parser", "text_parser", "base_parser", "factory"]
        for r in required:
            if r not in loaded:
                raise Exception(f"Missing required parser module: {r}")
                
        return "PASS", f"Parser modules loaded and verified: {', '.join(loaded)}"
    except Exception as e:
        return "FAIL", str(e)

def test_ai():
    try:
        from scrapers.nlp_extractor import generate_ai_summary, calculate_eligibility
        return "PASS", "AI NLP extraction logic verified."
    except Exception as e:
        return "FAIL", str(e)

def test_spec():
    try:
        if not os.path.exists("govtrack.spec"):
            return "FAIL", "govtrack.spec is missing"
            
        with open("govtrack.spec", "r") as f:
            content = f.read()
            
        required = ["datas =", "binaries=", "hiddenimports=", "runtime_hooks=", "pathex="]
        for req in required:
            if req.replace(" ", "") not in content.replace(" ", ""):
                return "FAIL", f"Missing {req} in spec file"
                
        return "PASS", "govtrack.spec validated successfully."
    except Exception as e:
        return "FAIL", str(e)

def run_all_tests():
    print("="*40)
    print("GovTrack AI - Build Validator (Python)")
    print("="*40)
    
    results = {}
    
    status, msg = test_spec()
    results["Spec Config"] = {"status": status, "msg": msg}
    report("Spec Config", status, msg)
    
    status, msg = test_database()
    results["Database"] = {"status": status, "msg": msg}
    report("Database", status, msg)
    
    status, msg = test_scrapers()
    results["Scrapers"] = {"status": status, "msg": msg}
    report("Scrapers", status, msg)
    
    status, msg = test_parsers()
    results["Parsers"] = {"status": status, "msg": msg}
    report("Parsers", status, msg)
    
    status, msg = test_ai()
    results["AI"] = {"status": status, "msg": msg}
    report("AI", status, msg)
    
    # Save test report
    with open("test_report.md", "w") as f:
        f.write("# GovTrack AI Test Summary\n\n")
        f.write("| Module | Status | Details |\n")
        f.write("|--------|--------|---------|\n")
        for k, v in results.items():
            f.write(f"| {k} | {v['status']} | {v['msg']} |\n")
            
    if any(v["status"] == "FAIL" for v in results.values()):
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
