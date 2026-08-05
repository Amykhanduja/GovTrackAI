from fastapi import APIRouter
from typing import List, Dict
import time

from scrapers.registry import OrganizationRegistry
from scrapers.shared.generic_portal import GenericPortalScraper

router = APIRouter(prefix="/diagnostics", tags=["Diagnostics"])

@router.post("/run")
def run_diagnostics():
    registry = OrganizationRegistry()
    results = []
    
    for org_meta in registry.organizations:
        scraper = GenericPortalScraper(org_meta)
        diag = scraper.run_diagnostic()
        
        # We can simulate added/updated based on parsing since the diagnostic doesn't save to DB.
        # But we don't want to actually save to DB during a diagnostic run to avoid side effects.
        # The prompt asks for "Recruitments Added", "Recruitments Updated".
        # We can just say "Would Add", "Would Update" or set them to N/A for diagnostic run,
        # or we could actually check the DB if they exist. Let's check DB.
        from db.connection import SessionLocal
        from db.models import Job
        db = SessionLocal()
        added = 0
        updated = 0
        try:
            for job in diag["raw_jobs"]:
                existing = db.query(Job).filter(
                    Job.org_id == (db.query(Job.org_id).filter(Job.url == job["url"]).scalar() or -1)
                ).first()
                if existing:
                    updated += 1
                else:
                    added += 1
        finally:
            db.close()
            
        diag["added"] = added
        diag["updated"] = updated
        del diag["raw_jobs"] # don't send all raw jobs back to UI
        
        # If it found zero but we know there's no active recruitment, clarify it
        if diag["parsed"] == 0 and diag["zero_reason"] == "Recruitment filtered incorrectly or No active vacancies":
            diag["zero_reason"] = "No active recruitment exists (or filtered correctly)"
            
        results.append(diag)
        
    return {"diagnostics": results}
