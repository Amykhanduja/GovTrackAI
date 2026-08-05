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
        self.url = self.metadata.get('recruitment_url', '')
        self.base_url = self.metadata.get('base_url', self.url)
        self.org_domains = self.metadata.get('career_domain', [])
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Referer': self.base_url
        }

    def _fetch_url_with_retry(self, url, max_retries=3):
        import time
        import requests
        backoff = 1
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=15, verify=False, allow_redirects=True)
                
                if response.status_code in (404, 403, 410):
                    logger.warning(f"Ignored invalid URL ({response.status_code}): {url}")
                    return None
                    
                response.raise_for_status()
                return response
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on {url}, attempt {attempt+1}/{max_retries}")
            except requests.exceptions.TooManyRedirects:
                logger.warning(f"Redirect loop on {url}")
                return None
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed on {url}: {e}")
                
            time.sleep(backoff)
            backoff *= 2
        return None

    def _discover_recruitment_url(self):
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin
        
        if not self.base_url: return self.url
        
        response = self._fetch_url_with_retry(self.base_url)
        if not response:
            return self.url
            
        soup = BeautifulSoup(response.text, 'html.parser')
        nav_kws = ['career', 'recruit', 'vacanc', 'opportunit', 'job', 'opening']
        for link in soup.find_all('a', href=True):
            text = link.get_text(separator=' ', strip=True).lower()
            href = link['href'].lower()
            if any(kw in text for kw in nav_kws) or any(kw in href for kw in nav_kws):
                full_url = urljoin(self.base_url, link['href'])
                logger.info(f"Dynamically discovered recruitment page: {full_url}")
                return full_url
        return self.url
        
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
        from urllib.parse import urljoin
        
        target_url = self._discover_recruitment_url()
        logger.info(f"REAL SCRAPE executing for {self.name} at {target_url}")
        jobs = []
        try:
            response = self._fetch_url_with_retry(target_url)
            if not response:
                return []
            
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
                        href = urljoin(target_url, href)
                            
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

    def run_diagnostic(self) -> dict:
        import time
        start = time.time()
        diag = {
            "organization": self.name,
            "url": self.url,
            "success": False,
            "status_code": None,
            "last_scan_time": datetime.now().isoformat(),
            "pages_visited": 1,
            "links_found": 0,
            "parsed": 0,
            "ignored": 0,
            "ignored_reasons": {},
            "errors": [],
            "execution_time_sec": 0,
            "zero_reason": None,
            "raw_jobs": []
        }
        
        try:
            target_url = self._discover_recruitment_url()
            diag["url"] = target_url
            response = self._fetch_url_with_retry(target_url)
            if not response:
                diag["errors"].append("Failed to fetch URL")
                diag["zero_reason"] = "Failed to fetch URL"
                return diag
                
            diag["status_code"] = response.status_code
            diag["success"] = True
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pos_kws = ['recruit', 'vacancy', 'vacancies', 'apply', 'advertisement', 'notice', 'post of', 'hiring', 'walk-in', 'career']
            neg_kws = ['news', 'tender', 'press release', 'event', 'seminar', 'competition', 'admission', 'scholarship', 'training', 'workshop', 'circular', 'conference', 'academic', 'result', 'syllabus', 'curriculum', 'exam schedule', 'answer key', 'corrigendum', 'cancellation']
            
            links = soup.find_all('a', href=True)
            diag["links_found"] = len(links)
            seen_titles = set()
            
            jobs = []
            
            for link in links:
                text = link.get_text(separator=' ', strip=True)
                href = link['href']
                
                if not text or len(text) < 10:
                    diag["ignored"] += 1
                    diag["ignored_reasons"]["Too short / No text"] = diag["ignored_reasons"].get("Too short / No text", 0) + 1
                    continue
                    
                text_lower = text.lower()
                href_lower = href.lower()
                
                has_pos = any(k in text_lower for k in pos_kws) or any(k in href_lower for k in pos_kws)
                has_neg = any(k in text_lower for k in neg_kws) or any(k in href_lower for k in neg_kws)
                
                if not has_pos:
                    diag["ignored"] += 1
                    diag["ignored_reasons"]["No recruitment keywords"] = diag["ignored_reasons"].get("No recruitment keywords", 0) + 1
                    continue
                    
                if has_neg:
                    diag["ignored"] += 1
                    diag["ignored_reasons"]["Contains negative keywords (e.g. tender, result)"] = diag["ignored_reasons"].get("Contains negative keywords (e.g. tender, result)", 0) + 1
                    continue
                
                if text in seen_titles:
                    diag["ignored"] += 1
                    diag["ignored_reasons"]["Duplicate title"] = diag["ignored_reasons"].get("Duplicate title", 0) + 1
                    continue
                    
                seen_titles.add(text)
                
                from urllib.parse import urljoin
                href = urljoin(target_url, href)
                    
                diag["parsed"] += 1
                jobs.append({
                    "post": text[:200],
                    "url": href
                })
            
            diag["raw_jobs"] = jobs
            if len(jobs) == 0:
                if diag["links_found"] == 0:
                    diag["zero_reason"] = "Website layout changed or no links found"
                elif diag["ignored"] > 0:
                    diag["zero_reason"] = "Recruitment filtered incorrectly or No active vacancies"
                else:
                    diag["zero_reason"] = "No recruitment page found"
                    
        except Exception as e:
            diag["errors"].append(str(e))
            diag["zero_reason"] = f"Parser failed: {e}"
        finally:
            diag["execution_time_sec"] = round(time.time() - start, 2)
            
        return diag
