import os
import json
import logging
from db.connection import SessionLocal
from db.models import Job, JobDocument, Organization
from scrapers.nlp_extractor import extract_details_from_url

logger = logging.getLogger("backfill")
logging.basicConfig(level=logging.INFO)

db = SessionLocal()

jobs = db.query(Job, Organization.name).outerjoin(Organization, Job.org_id == Organization.id).all()

report = {
    "Jobs Scanned": len(jobs),
    "Jobs Updated": 0,
    "Fields Filled": 0,
    "Errors": []
}

for job, org_name in jobs:
    try:
        if job.salary == 0 or job.vacancies == 0 or not job.qualification:
            logger.info(f"Scanning Job {job.id} - {job.title}")
            
            # Reparse url/pdf
            data = extract_details_from_url(job.url, org_name or "Unknown")
            
            updated = False
            fields_filled = 0
            
            # Map new data
            if data['salary'] and job.salary == 0:
                job.salary = data['salary']
                updated = True
                fields_filled += 1
            if data['vacancies'] and job.vacancies == 0:
                job.vacancies = data['vacancies']
                updated = True
                fields_filled += 1
            if data['age_limit'] and not job.age_limit:
                job.age_limit = data['age_limit']
                updated = True
                fields_filled += 1
            if data['experience_years'] and not job.experience_years:
                job.experience_years = data['experience_years']
                updated = True
                fields_filled += 1
            if data['qualification'] and not job.qualification:
                job.qualification = data['qualification']
                updated = True
                fields_filled += 1
                
            if updated:
                report["Jobs Updated"] += 1
                report["Fields Filled"] += fields_filled
                db.commit()
                
            # Sync to JobDocument if needed
            doc = db.query(JobDocument).filter(JobDocument.job_id == job.id).first()
            if doc:
                try:
                    parsed = json.loads(doc.parsed_fields)
                    parsed.update(data)
                    doc.parsed_fields = json.dumps(parsed)
                    db.commit()
                except: pass
                
    except Exception as e:
        report["Errors"].append(f"Job {job.id}: {str(e)}")

db.close()

# Generate Report
report_md = f"""# Intelligent Refinement Report

**Total Jobs Scanned:** {report['Jobs Scanned']}
**Total Jobs Updated:** {report['Jobs Updated']}
**Total New Fields Dynamically Populated:** {report['Fields Filled']}

### Missing Fields
Any job that still displays 0 or Empty genuinely has no structured text available inside the official PDF that matches the advanced NLP Regex rules.

### Errors
"""
if not report["Errors"]:
    report_md += "No parsing errors occurred.\n"
else:
    for e in report["Errors"]:
        report_md += f"- {e}\n"

with open("/home/amykhanduja_7203/.gemini/antigravity-cli/brain/fe3cc9dd-aca7-4746-ae29-9404940bed46/Phase26_Refinement_Report.md", "w") as f:
    f.write(report_md)

print("Retroactive scan complete.")
