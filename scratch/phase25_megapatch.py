import os
import json

project_root = "/mnt/c/Users/khand/GovTrackAI"

# 1. Update Models
models_path = os.path.join(project_root, "db", "models.py")
with open(models_path, "a") as f:
    f.write('''
class JobDocument(Base):
    __tablename__ = 'job_documents'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    pdf_path = Column(String)
    extracted_text = Column(Text)
    parsed_fields = Column(Text)
    extracted_tables = Column(Text)
    ai_summary = Column(Text)
    eligibility_status = Column(String)
    eligibility_reason = Column(Text)
    version = Column(Integer, default=1)
''')

# 2. Re-write NLP Extractor to include PDFPlumber, PyMuPDF, AI Summary, Eligibility Engine
nlp_path = os.path.join(project_root, "scrapers", "nlp_extractor.py")
with open(nlp_path, "r") as f:
    nlp_content = f.read()

# We will just append the deep parsing methods to the end, and then modify the caller in manager.py
new_engines = '''
import pdfplumber
import fitz

def generate_ai_summary(text, fields):
    summary = "Official Notification Analysis:\\n"
    if fields.get('qualification'):
        summary += f"- Requires {fields['qualification']}\\n"
    if fields.get('vacancies', 0) > 0:
        summary += f"- {fields['vacancies']} total vacancies announced.\\n"
    if fields.get('salary', 0) > 0:
        summary += f"- Compensation scale starts around ₹{fields['salary']}.\\n"
    if 'written test' in text.lower() or 'cbt' in text.lower():
        summary += "- Selection involves a Written Examination / CBT.\\n"
    if 'interview' in text.lower():
        summary += "- Selection involves a Personal Interview.\\n"
    return summary

def calculate_eligibility(fields):
    reasons = []
    status = "Eligible"
    
    age = fields.get('age_limit')
    exp = fields.get('experience_years')
    qual = fields.get('qualification', '').lower()
    
    if age and age < 25:
        status = "Not Eligible"
        reasons.append(f"Age limit ({age}) is highly restrictive.")
    if exp and exp > 3:
        status = "Possibly Eligible"
        reasons.append(f"Requires {exp} years of prior experience.")
    if 'ph.d' in qual or 'master' in qual:
        status = "Possibly Eligible"
        reasons.append(f"Requires advanced postgraduate degree ({qual}).")
        
    if not reasons:
        reasons.append("Matches standard generic criteria.")
        
    return status, " ".join(reasons)

def deep_parse_pdf(local_path):
    text = ""
    tables = []
    try:
        with pdfplumber.open(local_path) as pdf:
            for page in pdf.pages[:10]: # Parse first 10 pages deeply
                t = page.extract_text()
                if t: text += t + "\\n"
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
'''

with open(nlp_path, "a") as f:
    f.write(new_engines)

# 3. Update Manager to store the JobDocument
manager_path = os.path.join(project_root, "scrapers", "manager.py")
with open(manager_path, "r") as f:
    mgr_content = f.read()
    
patch_str = '''
                        db.add(new_job)
                        db.flush() # get ID
                        
                        # Phase R2.5D, R2.5F, R2.5G
                        local_path = None
                        from scrapers.pdf_manager import PDFStorageManager
                        if new_job.url.endswith('.pdf'):
                            local_path = PDFStorageManager().download_if_needed(new_job.url, org.name)
                        
                        if local_path:
                            from scrapers.nlp_extractor import deep_parse_pdf, generate_ai_summary, calculate_eligibility
                            from db.models import JobDocument
                            import json
                            
                            text, tables = deep_parse_pdf(local_path)
                            summary = generate_ai_summary(text, nlp)
                            elig_stat, elig_reason = calculate_eligibility(nlp)
                            
                            doc = JobDocument(
                                job_id=new_job.id,
                                pdf_path=local_path,
                                extracted_text=text[:10000], # store up to 10k chars
                                parsed_fields=json.dumps(nlp),
                                extracted_tables=json.dumps(tables),
                                ai_summary=summary,
                                eligibility_status=elig_stat,
                                eligibility_reason=elig_reason
                            )
                            db.add(doc)
                        
                        self.stats['jobs_added'] += 1
'''
mgr_content = mgr_content.replace(
    "                        db.add(new_job)\n                        self.stats['jobs_added'] += 1",
    patch_str
)
with open(manager_path, "w") as f:
    f.write(mgr_content)


# 4. Update API Router to fetch JobDocument
router_path = os.path.join(project_root, "api", "routers", "jobs.py")
with open(router_path, "a") as f:
    f.write('''
@router.get("/{job_id}/document")
def get_job_document(job_id: int, db: Session = Depends(get_db)):
    from db.models import JobDocument
    import json
    doc = db.query(JobDocument).filter(JobDocument.job_id == job_id).first()
    if not doc:
        return {"status": "not_found"}
    return {
        "status": "found",
        "pdf_path": doc.pdf_path,
        "ai_summary": doc.ai_summary,
        "eligibility_status": doc.eligibility_status,
        "eligibility_reason": doc.eligibility_reason,
        "parsed_fields": json.loads(doc.parsed_fields) if doc.parsed_fields else {},
        "extracted_tables": json.loads(doc.extracted_tables) if doc.extracted_tables else []
    }

from fastapi.responses import FileResponse
@router.get("/{job_id}/pdf")
def get_job_pdf(job_id: int, db: Session = Depends(get_db)):
    from db.models import JobDocument
    doc = db.query(JobDocument).filter(JobDocument.job_id == job_id).first()
    if not doc or not doc.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(doc.pdf_path, media_type="application/pdf")
''')

print("Backend engines generated.")
