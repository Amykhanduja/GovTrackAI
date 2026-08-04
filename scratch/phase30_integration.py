import os

nlp_path = "/mnt/c/Users/khand/GovTrackAI/scrapers/nlp_extractor.py"
with open(nlp_path, "r") as f:
    nlp_content = f.read()

integration_code = """import re
import io
import requests
from bs4 import BeautifulSoup
import logging
from scrapers.pdf_manager import PDFStorageManager
from parsers.factory import ParserFactory
from parsers.text_parser import TextParser

logger = logging.getLogger('app.nlp_extractor')

def deep_parse_pdf(local_path):
    try:
        parser = ParserFactory.get_parser(local_path)
        pages_text = parser.extract_text(local_path)
        return pages_text, []  # Tables not implemented yet
    except Exception as e:
        logger.error(f"ParserFactory failed on {local_path}: {e}")
        return [], []

def extract_details_from_url(url: str, org_name: str = "Unknown"):
    data = {
        "salary": 0, "vacancies": 0, "deadline": None, "age_limit": None,
        "min_age": None, "max_age": None, "age_relaxation": None,
        "experience_years": None, "qualification": None, "essential_qual": None,
        "desirable_qual": None, "app_start": None, "app_end": None,
        "exam_date": None, "interview_date": None, "selection_process": None,
        "confidence_scores": {}
    }
    
    if not url.startswith('http'): return data

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        pages_text = []
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
            storage = PDFStorageManager()
            local_path = storage.download_if_needed(url, org_name)
            if local_path:
                pages_text, _ = deep_parse_pdf(local_path)
        else:
            parser = ParserFactory.get_parser("temp.html")
            pages_text = parser.extract_text(response.text, is_file=False)
            
        text_parser = TextParser()
        parsed = text_parser.parse_all(pages_text)
        
        # Salary
        if parsed["salary"]["value"] > 0:
            data['salary'] = parsed["salary"]["value"]
            data['confidence_scores']['salary'] = parsed["salary"]["confidence"]
            
        # Vacancies
        if parsed["vacancies"]["value"] > 0:
            data['vacancies'] = parsed["vacancies"]["value"]
            data['confidence_scores']['vacancies'] = parsed["vacancies"]["confidence"]
            
        # Age
        age_dict = parsed["age"]["value"]
        if age_dict["age_limit"]: data['age_limit'] = age_dict["age_limit"]
        if age_dict["min_age"]: data['min_age'] = age_dict["min_age"]
        if age_dict["max_age"]: data['max_age'] = age_dict["max_age"]
        if age_dict["age_relaxation"]: data['age_relaxation'] = age_dict["age_relaxation"]
        data['confidence_scores']['age'] = parsed["age"]["confidence"]
        
        # Experience
        if parsed["experience"]["value"] is not None:
            data['experience_years'] = parsed["experience"]["value"]
            data['confidence_scores']['experience'] = parsed["experience"]["confidence"]
            
        # Qualification
        qual_dict = parsed["qualification"]["value"]
        if qual_dict["qualification"]: data['qualification'] = qual_dict["qualification"]
        if qual_dict["essential_qual"]: data['essential_qual'] = qual_dict["essential_qual"]
        if qual_dict["desirable_qual"]: data['desirable_qual'] = qual_dict["desirable_qual"]
        data['confidence_scores']['qualification'] = parsed["qualification"]["confidence"]
        
        # Dates
        dates_dict = parsed["dates"]["value"]
        if dates_dict["app_start"]: data['app_start'] = dates_dict["app_start"]
        if dates_dict["app_end"]: 
            data['app_end'] = dates_dict["app_end"]
            data['deadline'] = dates_dict["app_end"]
        if dates_dict["exam_date"]: data['exam_date'] = dates_dict["exam_date"]
        if dates_dict["interview_date"]: data['interview_date'] = dates_dict["interview_date"]
        data['confidence_scores']['dates'] = parsed["dates"]["confidence"]
        
        # Selection Process
        if parsed["selection_process"]["value"]:
            data['selection_process'] = parsed["selection_process"]["value"]
            data['confidence_scores']['selection_process'] = parsed["selection_process"]["confidence"]
        
    except Exception as e:
        logger.error(f"NLP Extractor failed for {url}: {e}")
        
    return data

def generate_ai_summary(text, fields):
    summary = "Official Notification Analysis:\\n"
    if fields.get('qualification'): summary += f"- Requires {fields['qualification']}\\n"
    if fields.get('vacancies', 0) > 0: summary += f"- {fields['vacancies']} total vacancies announced.\\n"
    if fields.get('salary', 0) > 0: summary += f"- Compensation scale starts around ₹{fields['salary']}.\\n"
    if fields.get('selection_process'): summary += f"- Selection process includes: {fields['selection_process']}\\n"
    return summary

def calculate_eligibility(fields):
    reasons = []
    status = "Eligible"
    age = fields.get('age_limit')
    exp = fields.get('experience_years')
    qual = (fields.get('qualification') or '').lower()
    
    if age and age < 25:
        status = "Not Eligible"
        reasons.append(f"Age limit ({age}) is highly restrictive.")
    if exp and exp > 3:
        status = "Possibly Eligible"
        reasons.append(f"Requires {exp} years of prior experience.")
    if 'ph.d' in qual or 'master' in qual:
        status = "Possibly Eligible"
        reasons.append(f"Requires advanced postgraduate degree.")
        
    if not reasons: reasons.append("Matches standard generic criteria.")
    return status, " ".join(reasons)
"""

with open(nlp_path, "w") as f:
    f.write(integration_code)
