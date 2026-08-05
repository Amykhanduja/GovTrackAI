import sys
import os
import time
from scrapers.shared.generic_portal import GenericPortalScraper
from scrapers.registry import OrganizationRegistry
import json

def generate_report():
    registry = OrganizationRegistry()
    report = []
    
    print(f"{'Organization':<25} | {'Status':<10} | {'Found':<5} | {'Errors':<5} | {'Skipped':<7}")
    print("-" * 70)
    
    for org_meta in registry.organizations:
        scraper = GenericPortalScraper(org_meta)
        org_name = org_meta['name']
        try:
            jobs = scraper.scrape()
            if jobs is None:
                status = "Failed"
                found = 0
                errors = 1
                skipped = 0
            else:
                status = "OK"
                found = len(jobs)
                errors = 0
                skipped = 0
        except Exception as e:
            status = "Error"
            found = 0
            errors = 1
            skipped = 0
            
        print(f"{org_name:<25} | {status:<10} | {found:<5} | {errors:<5} | {skipped:<7}")
        
        report.append({
            "Organization": org_name,
            "Status": status,
            "Jobs Found": found,
            "Errors": errors,
            "Skipped Jobs": skipped,
            "Reason": "N/A" if status == "OK" else "Scraping failed"
        })
        
    with open("scraper_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\nReport saved to scraper_report.json")

if __name__ == "__main__":
    generate_report()
