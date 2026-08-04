import re
import io
import requests
import dateparser
from bs4 import BeautifulSoup
from pypdf import PdfReader
from datetime import datetime
import logging
from scrapers.pdf_manager import PDFStorageManager
import pdfplumber
import fitz

logger = logging.getLogger('app.nlp_extractor')

def parse_salary(text):
    match = re.search(r'(?:Rs\.?|₹|INR|Salary|Pay Scale|Remuneration)[\s]*([0-9,]{4,}(?:\s*-\s*[0-9,]{4,})?)/?|-?\s*(?:Pay\s*)?Level\s*([0-9]{1,2})', text, re.IGNORECASE)
    if match:
        val = match.group(1)
        if val:
            try: return int(re.sub(r'[^0-9]', '', val.split('-')[0]))
            except: pass
        if match.group(2):
            return int(match.group(2)) * 10000
    
    match2 = re.search(r'([0-9]{2,3},[0-9]{3})\s*-\s*([0-9]{2,3},[0-9]{3})', text)
    if match2:
        try: return int(match2.group(1).replace(',', ''))
        except: pass
    return 0

def parse_vacancies(text):
    match = re.search(r'(?:Total|No\.\s*of|Number of)?\s*(?:Vacancies|Posts|Positions|Post)[\s:-]*(\d{1,4})', text, re.IGNORECASE)
    if match:
        try: return int(match.group(1))
        except: pass
    match2 = re.search(r'(\d{1,4})\s*(?:vacancies|posts|positions)', text, re.IGNORECASE)
    if match2:
        try: return int(match2.group(1))
        except: pass
    return 0

def parse_age_fields(text):
    age_limit, min_age, max_age, age_relax = None, None, None, None
    match_max = re.search(r'(?:Upper|Maximum) Age(?: Limit)?[\s:-]*(\d{2})\s*(?:years|yrs)?', text, re.IGNORECASE)
    if match_max: max_age = int(match_max.group(1))
    
    match_min = re.search(r'(?:Lower|Minimum) Age(?: Limit)?[\s:-]*(\d{2})\s*(?:years|yrs)?', text, re.IGNORECASE)
    if match_min: min_age = int(match_min.group(1))
    
    match_gen = re.search(r'(?:Age Limit)[\s:-]*(?:up to\s*|Not exceeding\s*)?(\d{2})\s*(?:years|yrs)', text, re.IGNORECASE)
    if match_gen: age_limit = int(match_gen.group(1))
    
    if max_age and not age_limit: age_limit = max_age
    
    match_relax = re.search(r'(?:Age Relaxation)[\s:-]*(.+?)(?:\.|\n)', text, re.IGNORECASE)
    if match_relax: age_relax = match_relax.group(1).strip()
    
    return age_limit, min_age, max_age, age_relax

def parse_experience(text):
    match = re.search(r'(\d+)\s*(?:years|yrs)[\s]*(?:experience|of post qualification)', text, re.IGNORECASE)
    if match:
        try: return int(match.group(1))
        except: pass
    match2 = re.search(r'(?:Experience)[\s:-]*(\d+)\s*(?:years|yrs)', text, re.IGNORECASE)
    if match2:
        try: return int(match2.group(1))
        except: pass
    return None

def parse_qualification(text):
    qual, ess, des = None, None, None
    match_ess = re.search(r'(?:Essential|Minimum) Qualification[\s:-]*(.+?)(?:Desirable|\Z)', text, re.IGNORECASE | re.DOTALL)
    if match_ess: ess = match_ess.group(1).strip()[:200].replace('\n', ' ')
    
    match_des = re.search(r'(?:Desirable) Qualification[\s:-]*(.+?)(?:\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if match_des: des = match_des.group(1).strip()[:200].replace('\\n', ' ')
    
    match = re.search(r'(?:Qualification|Eligibility|Education)[\s:-]*([A-Za-z\s,.\/]+(?:Degree|Diploma|B\.E|B\.Tech|M\.Tech|Ph\.D|B\.Sc|M\.Sc|M\.A|B\.A|Masters|Bachelors|10th|12th|Graduation))', text, re.IGNORECASE)
    if match: qual = match.group(1).strip()[:100]
    
    if ess and not qual: qual = ess[:100]
    return qual, ess, des

def parse_dates(text):
    app_start, app_end, exam, interview = None, None, None, None
    match_start = re.search(r'(?:Opening Date|Start Date|Commencement)[\s:-]*([0-9]{1,2}[\s\-/A-Za-z]+[0-9]{2,4})', text, re.IGNORECASE)
    if match_start:
        dt = dateparser.parse(match_start.group(1))
        if dt: app_start = dt
        
    match_end = re.search(r'(?:Last Date|Closing Date|Deadline|Apply till)[\s:-]*([0-9]{1,2}[\s\-/A-Za-z]+[0-9]{2,4})', text, re.IGNORECASE)
    if match_end:
        dt = dateparser.parse(match_end.group(1))
        if dt: app_end = dt
        
    match_exam = re.search(r'(?:Exam Date|Date of CBT|Written Test)[\s:-]*([0-9]{1,2}[\s\-/A-Za-z]+[0-9]{2,4})', text, re.IGNORECASE)
    if match_exam:
        dt = dateparser.parse(match_exam.group(1))
        if dt: exam = dt
        
    match_int = re.search(r'(?:Interview Date|Date of Interview)[\s:-]*([0-9]{1,2}[\s\-/A-Za-z]+[0-9]{2,4})', text, re.IGNORECASE)
    if match_int:
        dt = dateparser.parse(match_int.group(1))
        if dt: interview = dt
        
    return app_start, app_end, exam, interview

def deep_parse_pdf(local_path):
    text = ""
    tables = []
    try:
        with pdfplumber.open(local_path) as pdf:
            for page in pdf.pages[:10]:
                t = page.extract_text()
                if t: text += t + "\n"
                page_tables = page.extract_tables()
                if page_tables: tables.extend(page_tables)
    except Exception as e:
        logger.warning(f"pdfplumber failed on {local_path}: {e}")
        try:
            with fitz.open(local_path) as doc:
                for page in doc:
                    text += page.get_text()
        except:
            pass
    return text, tables

def extract_details_from_url(url: str, org_name: str = "Unknown"):
    data = {
        "salary": 0, "vacancies": 0, "deadline": None, "age_limit": None,
        "min_age": None, "max_age": None, "age_relaxation": None,
        "experience_years": None, "qualification": None, "essential_qual": None,
        "desirable_qual": None, "app_start": None, "app_end": None,
        "exam_date": None, "interview_date": None
    }
    
    if not url.startswith('http'): return data

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        text_content = ""
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
            storage = PDFStorageManager()
            local_path = storage.download_if_needed(url, org_name)
            if local_path:
                text_content, _ = deep_parse_pdf(local_path)
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text(separator=' ', strip=True)
            
        data['salary'] = parse_salary(text_content)
        data['vacancies'] = parse_vacancies(text_content)
        data['age_limit'], data['min_age'], data['max_age'], data['age_relaxation'] = parse_age_fields(text_content)
        data['experience_years'] = parse_experience(text_content)
        data['qualification'], data['essential_qual'], data['desirable_qual'] = parse_qualification(text_content)
        
        start, end, exam, inter = parse_dates(text_content)
        data['app_start'] = start
        if end: data['app_end'] = end
        data['deadline'] = data['app_end'] # Map deadline
        data['exam_date'] = exam
        data['interview_date'] = inter
        
    except Exception as e:
        logger.error(f"NLP Extractor failed for {url}: {e}")
        
    return data

def generate_ai_summary(text, fields):
    summary = "Official Notification Analysis:\n"
    if fields.get('qualification'): summary += f"- Requires {fields['qualification']}\n"
    if fields.get('vacancies', 0) > 0: summary += f"- {fields['vacancies']} total vacancies announced.\n"
    if fields.get('salary', 0) > 0: summary += f"- Compensation scale starts around ₹{fields['salary']}.\n"
    if 'written test' in text.lower() or 'cbt' in text.lower(): summary += "- Selection involves a Written Examination / CBT.\n"
    if 'interview' in text.lower(): summary += "- Selection involves a Personal Interview.\n"
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
        reasons.append(f"Requires advanced postgraduate degree ({qual}).")
        
    if not reasons: reasons.append("Matches standard generic criteria.")
    return status, " ".join(reasons)
