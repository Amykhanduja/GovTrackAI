import os
import json

project_root = "/mnt/c/Users/khand/GovTrackAI"

orgs_data = {
    "organizations": [
        {"name": "RBI", "category": "Banking", "career_domain": ["finance"], "recruitment_url": "https://opportunities.rbi.org.in/Scripts/Vacancies.aspx"},
        {"name": "SBI", "category": "Banking", "career_domain": ["finance"], "recruitment_url": "https://sbi.co.in/web/careers/current-openings"},
        {"name": "IBPS", "category": "Banking", "career_domain": ["finance"], "recruitment_url": "https://www.ibps.in/"},
        {"name": "NIC", "category": "Technology", "career_domain": ["cyber_tech"], "recruitment_url": "https://www.nic.in/recruitments/"},
        {"name": "NIELIT", "category": "Technology", "career_domain": ["cyber_tech"], "recruitment_url": "https://nielit.gov.in/recruitments"},
        {"name": "DRDO", "category": "Defense", "career_domain": ["cyber_tech"], "recruitment_url": "https://www.drdo.gov.in/careers"},
        {"name": "ISRO", "category": "Space", "career_domain": ["cyber_tech"], "recruitment_url": "https://www.isro.gov.in/Careers.html"},
        {"name": "BARC", "category": "Research", "career_domain": ["cyber_tech"], "recruitment_url": "https://www.barc.gov.in/careers/"},
        {"name": "CDAC", "category": "Technology", "career_domain": ["cyber_tech"], "recruitment_url": "https://www.cdac.in/index.aspx?id=current_jobs"},
        {"name": "CERT-In", "category": "Security", "career_domain": ["cyber_tech"], "recruitment_url": "https://www.cert-in.org.in/"},
        {"name": "MeitY", "category": "Ministry", "career_domain": ["cyber_tech"], "recruitment_url": "https://www.meity.gov.in/vacancies"},
        {"name": "NCIIPC", "category": "Security", "career_domain": ["cyber_tech"], "recruitment_url": "https://nciipc.gov.in/"},
        {"name": "ECIL", "category": "PSU", "career_domain": ["cyber_tech"], "recruitment_url": "https://www.ecil.co.in/jobs.html"},
        {"name": "BEL", "category": "PSU", "career_domain": ["cyber_tech"], "recruitment_url": "https://bel-india.in/CareersGridbind.aspx"},
        {"name": "BHEL", "category": "PSU", "career_domain": ["cyber_tech"], "recruitment_url": "https://careers.bhel.in/"},
        {"name": "HAL", "category": "PSU", "career_domain": ["cyber_tech"], "recruitment_url": "https://hal-india.co.in/Career"},
        {"name": "GAIL", "category": "PSU", "career_domain": ["energy"], "recruitment_url": "https://gailonline.com/CRApplyingGail.html"},
        {"name": "ONGC", "category": "PSU", "career_domain": ["energy"], "recruitment_url": "https://ongcindia.com/web/eng/career"},
        {"name": "NPCIL", "category": "PSU", "career_domain": ["energy"], "recruitment_url": "https://npcilcareers.co.in/"},
        {"name": "C-DOT", "category": "Technology", "career_domain": ["cyber_tech"], "recruitment_url": "https://www.cdot.in/cdotweb/web/careers.php"},
        {"name": "Income Tax", "category": "Ministry", "career_domain": ["finance"], "recruitment_url": "https://incometaxindia.gov.in/Pages/about-us/recruitment-notices.aspx"},
        {"name": "UPSC", "category": "Commission", "career_domain": ["admin"], "recruitment_url": "https://upsc.gov.in/"},
        {"name": "SSC", "category": "Commission", "career_domain": ["admin"], "recruitment_url": "https://ssc.nic.in/"}
    ]
}

files = {
    "config/organizations.json": json.dumps(orgs_data, indent=4),

    "scrapers/shared/generic_portal.py": """from scrapers.base_scraper import BaseScraper
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger('app.generic_scraper')

class GenericPortalScraper(BaseScraper):
    def __init__(self, org_metadata: dict):
        super().__init__({})
        self.metadata = org_metadata
        self.name = self.metadata['name']
        self.url = self.metadata['recruitment_url']
        self.domains = self.metadata.get('career_domain', [])
        
    def scrape(self) -> list:
        logger.info(f"REAL SCRAPE executing for {self.name} at {self.url}")
        jobs = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(self.url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for links containing recruitment keywords
            keywords = ['recruit', 'vacancy', 'apply', 'advertisement', 'notice']
            links = soup.find_all('a', href=True)
            
            seen_titles = set()
            for link in links:
                text = link.get_text(strip=True)
                if not text:
                    continue
                if any(k in text.lower() for k in keywords) or any(k in link['href'].lower() for k in keywords):
                    if len(text) > 5 and text not in seen_titles:
                        seen_titles.add(text)
                        href = link['href']
                        if not href.startswith('http'):
                            if href.startswith('/'):
                                href = self.url.rstrip('/') + href
                            else:
                                href = self.url.rstrip('/') + '/' + href
                        
                        jobs.append({
                            "org": self.name,
                            "post": text[:200],  # truncate if too long
                            "url": href,
                            "salary": 0,
                            "vacancies": 0,
                            "domains": self.domains,
                            "deadline": None
                        })
            logger.info(f"Successfully scraped {len(jobs)} potential jobs from {self.name}")
        except Exception as e:
            logger.error(f"Failed to scrape {self.name}: {e}")
            # Fail gracefully, don't crash other scrapers
        return jobs
""",

    "scrapers/manager.py": """import logging
from scrapers.shared.generic_portal import GenericPortalScraper
from scrapers.registry import OrganizationRegistry
from db.connection import SessionLocal
from db.models import Job, Organization
from datetime import datetime

logger = logging.getLogger('app.scraper_manager')

class ScraperManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.registry = OrganizationRegistry()
        self.stats = {'total_run': 0, 'successful': 0, 'failed': 0, 'inserted': 0, 'updated': 0}

    def run_all(self):
        db = SessionLocal()
        try:
            for org_meta in self.registry.organizations:
                self.stats['total_run'] += 1
                scraper = GenericPortalScraper(org_meta)
                jobs = scraper.scrape()
                
                if jobs is None:
                    self.stats['failed'] += 1
                    continue
                self.stats['successful'] += 1
                
                # DB Sync logic
                # Ensure Organization exists
                org_name = org_meta['name']
                org = db.query(Organization).filter(Organization.name == org_name).first()
                if not org:
                    org = Organization(name=org_name, category=org_meta.get('category'))
                    db.add(org)
                    db.commit()
                
                for j in jobs:
                    # Duplicate check by URL or Post Title for the same org
                    existing = db.query(Job).filter(
                        Job.org_id == org.id,
                        Job.url == j['url']
                    ).first()
                    
                    if not existing:
                        new_job = Job(
                            org_id=org.id,
                            title=j['post'],
                            url=j['url'],
                            salary=j.get('salary', 0),
                            vacancies=j.get('vacancies', 0),
                            deadline=j.get('deadline'),
                            created_at=datetime.now(),
                            domain=j['domains'][0] if j['domains'] else 'uncategorized',
                            status="New"
                        )
                        db.add(new_job)
                        self.stats['inserted'] += 1
                    else:
                        # Update changed notifications (e.g., deadline extended)
                        updated = False
                        if j.get('deadline') and existing.deadline != j.get('deadline'):
                            existing.deadline = j.get('deadline')
                            updated = True
                        if updated:
                            self.stats['updated'] += 1
                
                db.commit()
        finally:
            db.close()
        return self.stats
""",

    "api/routers/jobs.py": """from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from api.models.schemas import JobResponse
from db.models import Job, Organization, AISummary
from db.connection import SessionLocal
from scrapers.manager import ScraperManager

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/", response_model=List[JobResponse])
def get_jobs(domain: str = None, search: str = None, db: Session = Depends(get_db)):
    query = db.query(Job, Organization.name.label("org_name"), AISummary.summary_text).outerjoin(
        Organization, Job.org_id == Organization.id
    ).outerjoin(
        AISummary, Job.id == AISummary.job_id
    )

    if domain:
        query = query.filter(Job.domain == domain)
        
    if search:
        query = query.filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Organization.name.ilike(f"%{search}%")
            )
        )
        
    results = query.all()
    
    final_results = []
    for job, org_name, ai_sum in results:
        final_results.append({
            "id": job.id,
            "org": org_name or "Unknown",
            "post": job.title,
            "salary": job.salary,
            "vacancies": job.vacancies,
            "deadline": job.deadline,
            "added_at": job.created_at,
            "status": job.status,
            "priority": job.priority,
            "skills": job.skills,
            "url": job.url,
            "ai_summary": ai_sum,
            "domain": job.domain,
            "fav": job.priority,
            "hidden": 1 if job.is_hidden else 0,
            "trash": 1 if job.is_trashed else 0,
            "archive": 1 if job.is_archived else 0,
            "applied": 1 if job.is_applied else 0
        })
    return final_results

@router.patch("/{job_id}/apply")
def toggle_apply(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.is_applied = not job.is_applied
    db.commit()
    return {"status": "success", "applied": job.is_applied}

@router.post("/refresh")
def run_scrapers():
    manager = ScraperManager()
    stats = manager.run_all()
    return {"status": "success", "stats": stats}
"""
}

for filepath, content in files.items():
    full_path = os.path.join(project_root, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)

print("Phase 21 Real Scrapers Complete.")
