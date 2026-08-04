import os

project_root = "/mnt/c/Users/khand/GovTrackAI"

nlp_code = '''import re
import io
import requests
import dateparser
from bs4 import BeautifulSoup
from pypdf import PdfReader
from datetime import datetime
import logging

logger = logging.getLogger('app.nlp_extractor')

def parse_salary(text):
    # Extract numeric salary values (e.g. 50000, 100000) or Pay Levels
    match = re.search(r'(?:Rs\.?|₹|INR|Salary|Pay Scale)[\s]*([0-9,]{4,}(?:\s*-\s*[0-9,]{4,})?)/?|-?\s*Level\s*([0-9]{1,2})', text, re.IGNORECASE)
    if match:
        val = match.group(1)
        if val:
            try:
                return int(re.sub(r'[^0-9]', '', val.split('-')[0]))
            except:
                pass
        if match.group(2):
            return int(match.group(2)) * 10000 # Estimate
    return 0

def parse_vacancies(text):
    match = re.search(r'(?:Total|No\.\s*of)?\s*(?:Vacancies|Posts|Positions)[\s:-]*(\d{1,4})', text, re.IGNORECASE)
    if match:
        try: return int(match.group(1))
        except: pass
    return 0

def parse_age(text):
    match = re.search(r'(?:Age Limit|Maximum Age|Upper Age)[\s:-]*(?:up to\s*)?(\d{2})', text, re.IGNORECASE)
    if match:
        try: return int(match.group(1))
        except: pass
    return None

def parse_experience(text):
    match = re.search(r'(\d+)\s*(?:years|yrs)[\s]*(?:experience)', text, re.IGNORECASE)
    if match:
        try: return int(match.group(1))
        except: pass
    return None

def parse_deadline(text):
    match = re.search(r'(?:Last Date|Closing Date|Deadline|Apply till)[\s:-]*([0-9]{1,2}[\s\-/A-Za-z]+[0-9]{2,4})', text, re.IGNORECASE)
    if match:
        dt = dateparser.parse(match.group(1))
        if dt: return dt
    return None

def parse_qualification(text):
    match = re.search(r'(?:Qualification|Eligibility|Education)[\s:-]*([A-Za-z\s,.\/]+(?:Degree|Diploma|B\.E|B\.Tech|M\.Tech|Ph\.D|B\.Sc|M\.Sc|M\.A|B\.A|Masters|Bachelors|10th|12th|Graduation))', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()[:100]
    return None

def extract_details_from_url(url: str):
    data = {
        "salary": 0,
        "vacancies": 0,
        "deadline": None,
        "age_limit": None,
        "experience_years": None,
        "qualification": None
    }
    
    if not url.startswith('http'):
        return data

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        text_content = ""
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
            reader = PdfReader(io.BytesIO(response.content))
            for page in reader.pages[:5]:
                text_content += page.extract_text() + " "
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text(separator=' ', strip=True)
            
        data['salary'] = parse_salary(text_content)
        data['vacancies'] = parse_vacancies(text_content)
        data['age_limit'] = parse_age(text_content)
        data['experience_years'] = parse_experience(text_content)
        data['deadline'] = parse_deadline(text_content)
        data['qualification'] = parse_qualification(text_content)
        
    except Exception as e:
        logger.error(f"NLP Extractor failed for {url}: {e}")
        
    return data
'''

manager_code = '''import logging
import time
from datetime import datetime
from scrapers.shared.generic_portal import GenericPortalScraper
from scrapers.registry import OrganizationRegistry
from scrapers.nlp_extractor import extract_details_from_url
from db.connection import SessionLocal
from db.models import Job, Organization

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
            'failed_orgs': [],
            'duration_seconds': 0,
            'last_successful_refresh': None
        }

    def calc_status(self, deadline):
        if not deadline: return "Applications Open"
        diff = (deadline - datetime.now()).days
        if diff < 0: return "Closed"
        if diff <= 3: return "Closing Soon"
        if diff > 30: return "Upcoming"
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
                    existing = db.query(Job).filter(
                        Job.org_id == org.id,
                        Job.url == j['url']
                    ).first()
                    
                    if not existing:
                        # Deep parse the PDF/HTML
                        nlp = extract_details_from_url(j['url'])
                        deadline = nlp['deadline'] or j.get('deadline')
                        
                        new_job = Job(
                            org_id=org.id,
                            title=j['post'],
                            url=j['url'],
                            salary=nlp['salary'] or j.get('salary', 0),
                            vacancies=nlp['vacancies'] or j.get('vacancies', 0),
                            deadline=deadline,
                            created_at=now,
                            domain=j['domains'][0] if j['domains'] else 'uncategorized',
                            qualification=nlp['qualification'],
                            age_limit=nlp['age_limit'],
                            experience_years=nlp['experience_years'],
                            status=self.calc_status(deadline)
                        )
                        db.add(new_job)
                        self.stats['jobs_added'] += 1
                    else:
                        updated = False
                        # Retry extracting missing info for existing jobs dynamically!
                        if (existing.salary == 0 or not existing.deadline or not existing.qualification) and not existing.is_archived:
                            nlp = extract_details_from_url(existing.url)
                            if not existing.salary and nlp['salary']:
                                existing.salary = nlp['salary']
                                updated = True
                            if not existing.deadline and nlp['deadline']:
                                existing.deadline = nlp['deadline']
                                updated = True
                            if not existing.qualification and nlp['qualification']:
                                existing.qualification = nlp['qualification']
                                updated = True
                            if not existing.age_limit and nlp['age_limit']:
                                existing.age_limit = nlp['age_limit']
                                updated = True
                        
                        # Recalculate status
                        new_status = self.calc_status(existing.deadline)
                        if existing.status != new_status:
                            existing.status = new_status
                            updated = True
                            
                        if updated:
                            self.stats['jobs_updated'] += 1
                
                db.commit()
            self.stats['last_successful_refresh'] = now.strftime("%Y-%m-%d %H:%M:%S")
        finally:
            self.stats['duration_seconds'] = round(time.time() - start_time, 2)
            db.close()
            
        return self.stats
'''

with open(os.path.join(project_root, "scrapers", "nlp_extractor.py"), "w") as f:
    f.write(nlp_code)

with open(os.path.join(project_root, "scrapers", "manager.py"), "w") as f:
    f.write(manager_code)

print("Phase 29 NLP Extractors Generated.")
