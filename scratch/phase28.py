import json
import os

project_root = "/mnt/c/Users/khand/GovTrackAI"
orgs_file = os.path.join(project_root, "config", "organizations.json")
scraper_file = os.path.join(project_root, "scrapers", "shared", "generic_portal.py")

# 1. Update organizations.json
with open(orgs_file, "r") as f:
    data = json.load(f)

new_orgs = [
    {"name": "MEA", "category": "Ministry", "career_domain": ["foreign_lang"], "recruitment_url": "https://www.mea.gov.in/vacancies.htm"},
    {"name": "ICCR", "category": "Council", "career_domain": ["foreign_lang"], "recruitment_url": "https://www.iccr.gov.in/vacancies"},
    {"name": "JNU", "category": "University", "career_domain": ["foreign_lang"], "recruitment_url": "https://jnu.ac.in/career"},
    {"name": "Delhi University (DU)", "category": "University", "career_domain": ["foreign_lang"], "recruitment_url": "http://www.du.ac.in/index.php?page=work-with-du"},
    {"name": "JMI", "category": "University", "career_domain": ["foreign_lang"], "recruitment_url": "https://jmi.ac.in/bulletinboard/NoticeJob/latest/1"},
    {"name": "IGNOU", "category": "University", "career_domain": ["foreign_lang"], "recruitment_url": "http://ignou.ac.in/ignou/bulletinboard/advertisements/latest/jobs"},
    {"name": "KVS", "category": "Education", "career_domain": ["foreign_lang"], "recruitment_url": "https://kvsangathan.nic.in/employment-notice/"},
    {"name": "NVS", "category": "Education", "career_domain": ["foreign_lang"], "recruitment_url": "https://navodaya.gov.in/nvs/en/Recruitment/"},
    {"name": "DSSSB", "category": "Board", "career_domain": ["foreign_lang"], "recruitment_url": "https://dsssb.delhi.gov.in/current-vacancies"},
    {"name": "UGC", "category": "Commission", "career_domain": ["foreign_lang"], "recruitment_url": "https://www.ugc.gov.in/ugc_jobs.aspx"},
    {"name": "AICTE", "category": "Council", "career_domain": ["foreign_lang"], "recruitment_url": "https://www.aicte-india.org/bulletins/advertisements"},
    {"name": "NCERT", "category": "Council", "career_domain": ["foreign_lang"], "recruitment_url": "https://ncert.nic.in/vacancies.php"},
    {"name": "NTA", "category": "Agency", "career_domain": ["foreign_lang"], "recruitment_url": "https://nta.ac.in/Recruitment"},
    {"name": "Intelligence Bureau (IB)", "category": "Security", "career_domain": ["foreign_lang"], "recruitment_url": "https://mha.gov.in/vacancies"},
    {"name": "Army Education Corps", "category": "Defense", "career_domain": ["foreign_lang"], "recruitment_url": "https://joinindianarmy.nic.in/"},
    {"name": "Indian Navy Education", "category": "Defense", "career_domain": ["foreign_lang"], "recruitment_url": "https://www.joinindiannavy.gov.in/"},
    {"name": "IAF Education", "category": "Defense", "career_domain": ["foreign_lang"], "recruitment_url": "https://afcat.cdac.in/"}
]

existing_names = [o["name"] for o in data["organizations"]]

for org in new_orgs:
    if org["name"] not in existing_names:
        data["organizations"].append(org)
    else:
        # If exists, ensure foreign_lang is in its domain
        for existing_org in data["organizations"]:
            if existing_org["name"] == org["name"]:
                if "foreign_lang" not in existing_org["career_domain"]:
                    existing_org["career_domain"].append("foreign_lang")

# Also ensure SSC, UPSC, DRDO have foreign_lang added to their domains
for o in data["organizations"]:
    if o["name"] in ["SSC", "UPSC", "DRDO"]:
        if "foreign_lang" not in o["career_domain"]:
            o["career_domain"].append("foreign_lang")

with open(orgs_file, "w") as f:
    json.dump(data, f, indent=4)

# 2. Rewrite scraper logic
generic_portal_code = '''from scrapers.base_scraper import BaseScraper
import logging
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger('app.generic_scraper')

class GenericPortalScraper(BaseScraper):
    def __init__(self, org_metadata: dict):
        super().__init__({})
        self.metadata = org_metadata
        self.name = self.metadata['name']
        self.url = self.metadata['recruitment_url']
        self.org_domains = self.metadata.get('career_domain', [])
        
    def determine_domain(self, text: str) -> str:
        text = text.lower()
        
        # Language Keywords
        lang_kws = ['language', 'interpreter', 'translator', 'linguist', 'subtitling', 'transcription', 'localization', 'proofreading', 'japanese', 'chinese', 'korean', 'french', 'german', 'russian', 'arabic', 'spanish', 'persian', 'portuguese', 'italian', 'thai', 'vietnamese', 'turkish', 'hebrew', 'pashto', 'sinhala', 'nepali', 'tibetan', 'urdu', 'english', 'hindi']
        
        # Cyber Keywords
        cyber_kws = ['cyber', 'security', 'developer', 'engineer', 'programmer', 'software', 'hardware', 'it officer', 'scientist', 'technical', 'network', 'database', 'system', 'ciso', 'computer', 'data', 'analyst', 'technology']
        
        is_lang = any(kw in text for kw in lang_kws)
        is_cyber = any(kw in text for kw in cyber_kws)
        
        if is_lang and 'foreign_lang' in self.org_domains:
            return 'foreign_lang'
        if is_cyber and 'cyber_tech' in self.org_domains:
            return 'cyber_tech'
            
        # Fallback to the org's primary domain if it specifically matches their vibe, 
        # but if the org is multi-domain (e.g. UPSC), fallback to the first domain.
        if len(self.org_domains) == 1:
            return self.org_domains[0]
            
        # If it's a general org and no keywords hit, default to uncategorized or the first domain
        return self.org_domains[0] if self.org_domains else 'uncategorized'

    def scrape(self) -> list:
        logger.info(f"REAL SCRAPE executing for {self.name} at {self.url}")
        jobs = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(self.url, headers=headers, timeout=20, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Strict Positive job keywords
            pos_kws = ['recruit', 'vacancy', 'vacancies', 'apply', 'advertisement', 'notice', 'post of', 'hiring', 'walk-in', 'career']
            
            # Strict Negative keywords (Ignore news, tenders, academics)
            neg_kws = ['news', 'tender', 'press release', 'event', 'seminar', 'competition', 'admission', 'scholarship', 'training', 'workshop', 'circular', 'conference', 'academic', 'result', 'syllabus', 'curriculum', 'exam schedule', 'answer key', 'corrigendum', 'cancellation']
            
            links = soup.find_all('a', href=True)
            seen_titles = set()
            
            for link in links:
                text = link.get_text(separator=' ', strip=True)
                href = link['href']
                
                if not text or len(text) < 10:
                    continue
                    
                text_lower = text.lower()
                href_lower = href.lower()
                
                # Must contain at least one positive keyword in text or href
                has_pos = any(k in text_lower for k in pos_kws) or any(k in href_lower for k in pos_kws)
                # Must NOT contain any negative keywords
                has_neg = any(k in text_lower for k in neg_kws) or any(k in href_lower for k in neg_kws)
                
                if has_pos and not has_neg:
                    if text not in seen_titles:
                        seen_titles.add(text)
                        
                        # Fix relative URLs
                        if not href.startswith('http'):
                            href = self.url.rstrip('/') + '/' + href.lstrip('/')
                            
                        # Domain classification
                        assigned_domain = self.determine_domain(text_lower)
                        
                        # Only append if the domain matches what the org is allowed to scrape
                        if assigned_domain in self.org_domains or len(self.org_domains) == 0:
                            jobs.append({
                                "org": self.name,
                                "post": text[:200],
                                "url": href,
                                "salary": 0,
                                "vacancies": 0,
                                "domains": [assigned_domain],
                                "deadline": None
                            })
                            
            logger.info(f"Successfully scraped {len(jobs)} potential jobs from {self.name}")
        except Exception as e:
            logger.error(f"Failed to scrape {self.name}: {e}")
            
        return jobs
'''

with open(scraper_file, "w") as f:
    f.write(generic_portal_code)

print("Phase 28 Scraper Enhancement Complete.")
