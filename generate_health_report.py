import os
import json
import logging
from sqlalchemy.orm import Session
from datetime import datetime

from scrapers.manager import ScraperManager
from scrapers.registry import OrganizationRegistry
from db.connection import SessionLocal
from db.models import Job, Organization

def generate_health_report():
    print("Running scraper manager...")
    manager = ScraperManager()
    stats = manager.run_all()
    print("Scraping completed.")

    db = SessionLocal()
    orgs = db.query(Organization).all()
    
    report_lines = [
        "# Scraper Infrastructure Health Report",
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Overall Statistics",
        f"- Organizations Scanned: {stats['organizations_scanned']}",
        f"- Jobs Added: {stats['jobs_added']}",
        f"- Jobs Updated: {stats['jobs_updated']}",
        f"- Duration: {stats['duration_seconds']}s",
        f"- Failed Organizations: {len(stats['failed_orgs'])}",
        "",
        "## Organization Breakdown"
    ]
    
    # Check each org
    registry = OrganizationRegistry()
    
    for org_meta in registry.organizations:
        org_name = org_meta['name']
        org_record = db.query(Organization).filter(Organization.name == org_name).first()
        
        report_lines.append(f"### {org_name}")
        report_lines.append(f"- **Configured URL**: {org_meta.get('recruitment_url', '')}")
        if not org_record:
            report_lines.append("- **Status**: Database record not found (Scraper likely completely failed)")
        else:
            job_count = db.query(Job).filter(Job.org_id == org_record.id).count()
            active_count = db.query(Job).filter(Job.org_id == org_record.id, Job.is_archived == False).count()
            report_lines.append(f"- **Total Jobs in DB**: {job_count}")
            report_lines.append(f"- **Active Jobs in DB**: {active_count}")
            
            if org_name in stats['failed_orgs']:
                report_lines.append("- **Scraper Status**: FAILED")
            else:
                report_lines.append("- **Scraper Status**: SUCCESS")
                
        report_lines.append("")
        
    db.close()
    
    # API Verification
    report_lines.append("## API Verification")
    from fastapi.testclient import TestClient
    from api.main import app
    client = TestClient(app)
    
    try:
        res = client.get("/api/v1/jobs/active")
        if res.status_code == 200:
            data = res.json()
            report_lines.append(f"- **Active Jobs API Endpoint**: SUCCESS ({len(data)} jobs returned)")
        else:
            report_lines.append(f"- **Active Jobs API Endpoint**: FAILED (Status: {res.status_code})")
    except Exception as e:
        report_lines.append(f"- **Active Jobs API Endpoint**: FAILED ({str(e)})")
        
    report_lines.append("")
    report_lines.append("## Frontend Verification")
    frontend_files = ["frontend/index.html", "frontend/app.js", "frontend/diagnostics.js"]
    for f in frontend_files:
        if os.path.exists(f):
            report_lines.append(f"- {f}: EXISTS")
        else:
            report_lines.append(f"- {f}: MISSING")
            
    with open("diagnostics_health_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print("Health report generated: diagnostics_health_report.md")

if __name__ == '__main__':
    generate_health_report()
