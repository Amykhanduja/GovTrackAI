import re
import logging

logger = logging.getLogger("app.filters")

KEEP_KEYWORDS = [
    r'recruitment', r'vacancy', r'vacancies', r'employment notice', 
    r'advertisement', r'job opening', r'walk-in', r'walk\s*in',
    r'hiring', r'employment opportunity', r'appointment', 
    r'selection notice', r'career', r'jobs', r'post of', r'posts of',
    r'recruitment notification', r'engagement', r'fellowship'
]

REMOVE_KEYWORDS = [
    r'\bnews\b', r'\bevents?\b', r'press release', r'\btenders?\b',
    r'\badmissions?\b', r'\bcourses?\b', r'\btraining\b', r'\bworkshops?\b',
    r'\bconferences?\b', r'academic calendar', r'exam notifications?',
    r'\bcirculars?\b', r'general information', r'\bseminars?\b',
    r'information bulletins?', r'entrance test', r'deeksharambh',
    r'notice board', r'medical benefits', r'cghs', r'empanelment',
    r'houselisting', r'delisting', r'census', r'spot admission',
    r'syllabus', r'exam result', r'answer key', r'corrigendum'
]

def is_valid_job(title: str, org_name: str = "") -> bool:
    title_lower = title.lower()
    
    # 1. Reject if it matches any REMOVE_KEYWORDS
    for kw in REMOVE_KEYWORDS:
        if re.search(kw, title_lower):
            logger.debug(f"Rejected '{title}' due to keyword: {kw}")
            return False
            
    # 2. Check if it explicitly contains a KEEP keyword
    for kw in KEEP_KEYWORDS:
        if re.search(kw, title_lower):
            return True
            
    # If it is a generic university, they post a lot of junk. Be strict.
    if 'university' in org_name.lower() or 'eflu' in org_name.lower() or 'isro' in org_name.lower():
        return False
        
    # By default, reject if it doesn't sound like a job.
    return False
