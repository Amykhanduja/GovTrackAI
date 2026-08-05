import sys
import os
import json
from pprint import pprint

def run_trace():
    print("--- TRACE START ---")
    
    print("\n[1] Scraper Stage")
    from scrapers.shared.generic_portal import GenericPortalScraper
    from scrapers.registry import OrganizationRegistry
    registry = OrganizationRegistry()
    org_meta = next(o for o in registry.organizations if o['name'] == 'UPSC')
    scraper = GenericPortalScraper(org_meta)
    jobs = scraper.scrape()
    print(f"Scraped {len(jobs)} jobs from UPSC")
    if not jobs:
        print("No jobs found for UPSC, tracing failed.")
        return
        
    first_job = jobs[0]
    print("Sample Job extracted by Scraper:")
    pprint(first_job)
    
    print("\n[2] Parser Stage")
    from scrapers.nlp_extractor import extract_details_from_url
    nlp_result = extract_details_from_url(first_job['url'], org_meta['name'])
    print("NLP Parsed Data:")
    pprint(nlp_result)
    
    print("\n[3] SQLite Pipeline")
    from db.connection import SessionLocal
    from db.models import Job, Organization, JobDocument
    db = SessionLocal()
    org = db.query(Organization).filter_by(name='UPSC').first()
    if not org:
        org = Organization(name='UPSC', category='Commission')
        db.add(org)
        db.commit()
        
    new_job = Job(
        org_id=org.id,
        title=first_job['post'],
        url=first_job['url'],
        domain=first_job['domains'][0],
        salary=nlp_result['salary'],
        vacancies=nlp_result['vacancies'],
        deadline=nlp_result['deadline'],
        age_limit=nlp_result['age_limit'],
        qualification=nlp_result['qualification'],
        experience_years=nlp_result['experience_years'],
        status="Applications Open"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    print(f"Inserted Job into SQLite with ID: {new_job.id}")
    
    print("\n[4] API Pipeline")
    from fastapi.testclient import TestClient
    from api.main import app
    client = TestClient(app)
    response = client.get("/api/v1/jobs/")
    print(f"API /api/v1/jobs/ status: {response.status_code}")
    
    # find the job in API response
    data = response.json()
    job_in_api = next((j for j in data if j['id'] == new_job.id), None)
    if job_in_api:
        print("Job retrieved via API:")
        pprint(job_in_api)
        print("\nPipeline Trace Successful.")
        print(f"Salary preserved: {job_in_api['salary'] == nlp_result['salary']}")
        print(f"Vacancies preserved: {job_in_api['vacancies'] == nlp_result['vacancies']}")
        print(f"Qualification preserved: {job_in_api['qualification'] == nlp_result['qualification']}")
        print(f"Experience preserved: {job_in_api['experience_years'] == nlp_result['experience_years']}")
        print(f"Age preserved: {job_in_api['age_limit'] == nlp_result['age_limit']}")
    else:
        print("Job not found in API response!")
        
if __name__ == "__main__":
    run_trace()
