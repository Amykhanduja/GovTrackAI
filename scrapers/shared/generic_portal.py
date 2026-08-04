from scrapers.base_scraper import BaseScraper
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
        
        if is_lang:
            return 'foreign_lang'
        if is_cyber:
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
