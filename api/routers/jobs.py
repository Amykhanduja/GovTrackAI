from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from api.models.schemas import JobResponse
from db.models import Job, Organization, AISummary
from db.connection import SessionLocal
from scrapers.manager import ScraperManager
import logging

logger = logging.getLogger('app.jobs_router')

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
            "id": job.id, "org": org_name or "Unknown", "post": job.title, "salary": job.salary, "vacancies": job.vacancies,
            "deadline": job.deadline, "added_at": job.created_at, "status": job.status, "priority": job.priority,
            "skills": job.skills, "url": job.url, "ai_summary": ai_sum, "domain": job.domain, "fav": job.priority,
            "hidden": 1 if job.is_hidden else 0, "trash": 1 if job.is_trashed else 0, "archive": 1 if job.is_archived else 0,
            "applied": 1 if job.is_applied else 0,
            "age_limit": job.age_limit,
            "experience_years": job.experience_years,
            "qualification": job.qualification,
            "description": job.description
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
    logger.info("Executing Master Refresh Cycle...")
    manager = ScraperManager()
    stats = manager.run_all()
    # Trigger Excel export automatically in background
    try:
        from excel.generator import ExcelGenerator
        from excel.data_provider import DataProvider
        provider = DataProvider()
        generator = ExcelGenerator(provider)
        generator.generate_dashboard()
    except Exception as e:
        logger.error(f"Auto-Excel export failed: {e}")
        
    return {"status": "success", "stats": stats}

@router.patch("/{job_id}/note")
def update_job_note(job_id: int, note_data: dict, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.description = note_data.get('note', '')
    db.commit()
    return {"status": "success"}

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
