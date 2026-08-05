import logging
import time
from datetime import datetime
from scrapers.shared.generic_portal import GenericPortalScraper
from scrapers.registry import OrganizationRegistry
from scrapers.nlp_extractor import extract_details_from_url
from scrapers.filters import is_valid_job
from db.connection import SessionLocal
from db.models import Job, Organization, JobDocument, RecruitmentHistory
from scrapers.nlp_extractor import generate_ai_summary, calculate_eligibility
import json

logger = logging.getLogger('app.scraper_manager')

class ScraperManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.registry = OrganizationRegistry()
        self.stats = {
            'organizations_scanned': 0, 
            'jobs_added': 0, 
            'jobs_updated': 0, 
            'jobs_archived': 0,
            'duration_seconds': 0,
            'failed_orgs': [],
            'last_successful_refresh': None
        }

    def calc_status(self, deadline):
        if not deadline: return "Applications Open"
        if isinstance(deadline, str):
            deadline = datetime.fromisoformat(deadline)
        now = datetime.now()
        diff = (deadline - now).days
        if diff < 0: return "Closed"
        if diff <= 3: return "Closing Soon"
        return "Applications Open"

    def run_all(self):
        db = SessionLocal()
        start_time = time.time()
        try:
            now = datetime.now()
            expired_jobs = db.query(Job).filter(Job.deadline < now, Job.is_archived == False).all()
            for ej in expired_jobs:
                ej.is_archived = True
                ej.status = "Closed"
                
                # Also update history status if exists
                hist = db.query(RecruitmentHistory).filter(RecruitmentHistory.job_id == ej.id).first()
                if hist:
                    hist.status = "Expired"
                    
                self.stats['jobs_archived'] += 1
            db.commit()

            for org_meta in self.registry.organizations:
                self.stats['organizations_scanned'] += 1
                scraper = GenericPortalScraper(org_meta)
                jobs = scraper.scrape()
                
                if jobs is None:
                    self.stats['failed_orgs'].append(org_meta['name'])
                    continue
                
                org_name = org_meta['name']
                org = db.query(Organization).filter(Organization.name == org_name).first()
                if not org:
                    org = Organization(name=org_name, category=org_meta.get('category'))
                    db.add(org)
                    db.commit()
                
                for j in jobs:
                    if not is_valid_job(j['post'], org.name):
                        logger.info(f"Filtered out non-job notification: {j['post']}")
                        continue
                        
                    existing = db.query(Job).filter(
                        Job.org_id == org.id,
                        Job.url == j['url']
                    ).first()
                    
                    # Deep parse the PDF/HTML
                    # --- NEW PARSER ARCHITECTURE INTEGRATION ---
                    # Only parse if we lack info or need to update
                    nlp = extract_details_from_url(j['url'], org.name)
                    
                    if not existing:
                        # Log extracted fields
                        for field, conf in nlp.get('confidence_scores', {}).items():
                            logger.info(f"{field.capitalize()} extracted - Confidence {conf:.2f}")

                        new_job = Job(
                            org_id=org.id,
                            title=j['post'],
                            url=j['url'],
                            domain=j['domains'][0] if j.get('domains') else 'uncategorized',
                            salary=nlp['salary'],
                            vacancies=nlp['vacancies'],
                            deadline=nlp['deadline'],
                            age_limit=nlp['age_limit'],
                            qualification=nlp['qualification'],
                            experience_years=nlp['experience_years'],
                            status=self.calc_status(nlp['deadline'])
                        )
                        db.add(new_job)
                        db.commit()
                        db.refresh(new_job)
                        
                        history = RecruitmentHistory(
                            org_id=org.id,
                            recruitment_name=j['post'],
                            post_name=j['post'],
                            notification_date=datetime.now(),
                            vacancies=nlp['vacancies'],
                            salary=nlp.get('salary', ''),
                            qualification=nlp.get('qualification', ''),
                            experience=nlp.get('experience_years'),
                            age_limit=nlp.get('age_limit'),
                            official_link=j['url'],
                            status=new_job.status,
                            job_id=new_job.id
                        )
                        db.add(history)
                        db.commit()
                        
                        # Store AI Extract
                        doc = JobDocument(
                            job_id=new_job.id,
                            pdf_path="",
                            extracted_text="",
                            parsed_fields=json.dumps(nlp),
                            extracted_tables="[]",
                            ai_summary=generate_ai_summary("", nlp),
                            eligibility_status=calculate_eligibility(nlp)[0],
                            eligibility_reason=calculate_eligibility(nlp)[1]
                        )
                        db.add(doc)
                        self.stats['jobs_added'] += 1

                    else:
                        updated = False
                        
                        # Confidence-based overwriting
                        old_doc = db.query(JobDocument).filter_by(job_id=existing.id).first()
                        old_conf = {}
                        if old_doc and old_doc.parsed_fields:
                            try: old_conf = json.loads(old_doc.parsed_fields).get('confidence_scores', {})
                            except: pass
                            
                        new_conf = nlp.get('confidence_scores', {})
                        
                        if nlp['salary'] and (not existing.salary or new_conf.get('salary', 0) > old_conf.get('salary', 0)):
                            existing.salary = nlp['salary']
                            updated = True
                        if nlp['vacancies'] and (not existing.vacancies or new_conf.get('vacancies', 0) > old_conf.get('vacancies', 0)):
                            existing.vacancies = nlp['vacancies']
                            updated = True
                        if nlp['deadline'] and (not existing.deadline or new_conf.get('dates', 0) > old_conf.get('dates', 0)):
                            existing.deadline = nlp['deadline']
                            updated = True
                        if nlp['qualification'] and (not existing.qualification or new_conf.get('qualification', 0) > old_conf.get('qualification', 0)):
                            existing.qualification = nlp['qualification']
                            updated = True
                        if nlp['age_limit'] and (not existing.age_limit or new_conf.get('age', 0) > old_conf.get('age', 0)):
                            existing.age_limit = nlp['age_limit']
                            updated = True
                            
                        # Recalculate status
                        new_status = self.calc_status(existing.deadline)
                        if existing.status != new_status:
                            existing.status = new_status
                            updated = True
                            
                        if updated:
                            if old_doc:
                                old_doc.parsed_fields = json.dumps(nlp)
                            self.stats['jobs_updated'] += 1

                
                db.commit()
            self.stats['last_successful_refresh'] = now.strftime("%Y-%m-%d %H:%M:%S")
        finally:
            self.stats['duration_seconds'] = round(time.time() - start_time, 2)
            db.close()
            
        return self.stats
