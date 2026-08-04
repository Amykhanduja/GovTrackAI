import os
import logging
from db.connection import SessionLocal
from db.models import Job, JobDocument, Organization
from scrapers.filters import is_valid_job

logger = logging.getLogger("scrubber")
logging.basicConfig(level=logging.INFO)

db = SessionLocal()

jobs = db.query(Job).join(Organization).all()
total = len(jobs)
deleted = 0

for job in jobs:
    org_name = job.organization.name if job.organization else ""
    if not is_valid_job(job.title, org_name):
        logger.info(f"Deleting non-job notification: [{org_name}] {job.title}")
        # Delete associated documents
        db.query(JobDocument).filter(JobDocument.job_id == job.id).delete()
        # Delete job
        db.delete(job)
        deleted += 1

db.commit()
db.close()

print(f"Scrubbed {deleted} out of {total} records from the database.")
