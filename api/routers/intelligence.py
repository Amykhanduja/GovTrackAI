from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import datetime

from db.connection import SessionLocal
from db.models import (
    Organization, Job, RecruitmentHistory, RecruitmentCycle, 
    RecruitmentTrend, PredictionCache, NotificationArchive
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/intelligence", tags=["Intelligence"])

@router.get("/organizations/{org_id}")
def get_organization_intelligence(org_id: int, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    current_jobs = db.query(Job).filter(Job.org_id == org_id, Job.is_archived == False, Job.is_trashed == False).all()
    history = db.query(RecruitmentHistory).filter(RecruitmentHistory.org_id == org_id).order_by(desc(RecruitmentHistory.notification_date)).all()
    
    # Basic Insights & Predictions
    insights = []
    expected_next = None
    avg_freq = "Unknown"
    avg_sal = "Unknown"
    avg_vac = 0
    
    if len(history) > 1:
        dates = sorted([h.notification_date for h in history if h.notification_date])
        if len(dates) > 1:
            diffs = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            avg_days = sum(diffs) / len(diffs)
            months = round(avg_days / 30)
            avg_freq = f"Every {months} months"
            insights.append(f"This organization generally recruits every {months} months.")
            
            # Predict Next
            last_date = dates[-1]
            next_date = last_date + datetime.timedelta(days=avg_days)
            expected_next = f"Q{(next_date.month-1)//3 + 1} {next_date.year}"
            
        vacancies = [h.vacancies for h in history if h.vacancies]
        if vacancies:
            avg_vac = round(sum(vacancies) / len(vacancies))
            insights.append(f"Average vacancies per cycle: {avg_vac}.")
            
        salaries = [h.salary for h in history if h.salary and h.salary != '0']
        if salaries:
            avg_sal = salaries[0] # just use the most recent valid one as trend
            insights.append(f"Salary is typically around {avg_sal}.")
            
        quals = [h.qualification for h in history if h.qualification and h.qualification != 'None']
        if quals:
            from collections import Counter
            typical_qual = Counter(quals).most_common(1)[0][0]
            insights.append(f"Typical Qualification: {typical_qual}")
            
    status = "Active Recruitment" if current_jobs else ("Recruitment Expected Soon" if expected_next else "No Recruitment History")
    
    return {
        "organization": org.name,
        "status": status,
        "current_recruitments": current_jobs,
        "history": history,
        "trend_analysis": {
            "average_frequency": avg_freq,
            "average_salary": avg_sal,
            "average_vacancies": avg_vac,
            "expected_next": expected_next
        },
        "insights": insights
    }

@router.get("/search")
def search_history(q: str, db: Session = Depends(get_db)):
    active = db.query(Job).filter(Job.title.ilike(f"%{q}%")).all()
    historical = db.query(RecruitmentHistory).filter(RecruitmentHistory.post_name.ilike(f"%{q}%")).all()
    
    return {
        "active": active,
        "historical": historical
    }

@router.get("/dashboard")
def get_intelligence_dashboard(db: Session = Depends(get_db)):
    tracked = db.query(Organization).count()
    active = db.query(Job).filter(Job.is_archived == False).count()
    historical = db.query(RecruitmentHistory).count()
    
    return {
        "organizations_tracked": tracked,
        "active_recruitments": active,
        "historical_recruitments": historical,
        "expected_upcoming": 0,
        "organizations_recruiting_soon": 0,
        "expired_recruitments": 0
    }

from fastapi.responses import FileResponse
import csv
import os

@router.get("/export")
def export_intelligence(db: Session = Depends(get_db)):
    history = db.query(RecruitmentHistory).all()
    filepath = "data/intelligence_export.csv"
    os.makedirs("data", exist_ok=True)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Organization", "Recruitment Name", "Post", "Date", "Vacancies", "Salary", "Status"])
        for h in history:
            org = db.query(Organization).filter(Organization.id == h.org_id).first()
            org_name = org.name if org else "Unknown"
            writer.writerow([
                org_name,
                h.recruitment_name,
                h.post_name,
                str(h.notification_date.date()) if h.notification_date else "",
                h.vacancies,
                h.salary,
                h.status
            ])
            
    return FileResponse(filepath, filename="intelligence_export.csv")
