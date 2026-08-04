import os

project_root = "/mnt/c/Users/khand/GovTrackAI"

files = {
    "db/models.py": """from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text

Base = declarative_base()

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)
    website = Column(String)
    ministry = Column(String)

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('organizations.id'))
    title = Column(String, nullable=False)
    description = Column(Text)
    salary = Column(Integer, default=0)
    vacancies = Column(Integer, default=0)
    deadline = Column(DateTime)
    created_at = Column(DateTime)
    skills = Column(Text)
    url = Column(String)
    domain = Column(String)
    
    qualification = Column(String)
    age_limit = Column(Integer)
    experience_years = Column(Integer)
    
    status = Column(String, default="New")
    priority = Column(Integer, default=0)
    is_hidden = Column(Boolean, default=False)
    is_trashed = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_applied = Column(Boolean, default=False)

class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    status = Column(String)
    applied_at = Column(DateTime)

class Exam(Base):
    __tablename__ = 'exams'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    exam_date = Column(DateTime)

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    published_at = Column(DateTime)

class AISummary(Base):
    __tablename__ = 'ai_summaries'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    summary_text = Column(Text)
    generated_at = Column(DateTime)
""",

    "api/models/schemas.py": """from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class JobResponse(BaseModel):
    id: int
    org: str
    post: str
    salary: Optional[int]
    vacancies: Optional[int]
    deadline: Optional[datetime]
    added_at: Optional[datetime]
    status: str
    priority: int
    skills: Optional[str]
    url: Optional[str]
    ai_summary: Optional[str]
    domain: Optional[str]
    fav: int
    hidden: int
    trash: int
    archive: int
    applied: int

    class Config:
        from_attributes = True

class ChartData(BaseModel):
    labels: List[str]
    values: List[int]

class AnalyticsResponse(BaseModel):
    total_jobs: int
    active_applications: int
    average_salary: int
    
    applied_vs_pending: ChartData
    jobs_by_org: ChartData
    jobs_by_ministry: ChartData
    jobs_by_qualification: ChartData
    jobs_by_salary: ChartData
    jobs_by_age: ChartData
    jobs_by_experience: ChartData
    upcoming_deadlines: ChartData
""",

    "api/routers/analytics.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from db.models import Job, Organization
from api.models.schemas import AnalyticsResponse, ChartData
from api.routers.jobs import get_db
import logging

logger = logging.getLogger('app.analytics')

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/", response_model=AnalyticsResponse)
def get_analytics(domain: str = None, db: Session = Depends(get_db)):
    # REAL DATABASE QUERIES
    q_base = db.query(Job).filter(Job.is_trashed == False)
    if domain:
        q_base = q_base.filter(Job.domain == domain)

    total_jobs = q_base.count()
    applied_count = q_base.filter(Job.is_applied == True).count()
    pending_count = total_jobs - applied_count
    
    avg_sal = db.query(func.avg(Job.salary)).filter(Job.is_trashed == False, Job.salary > 0).scalar() or 0

    def make_chart(query_res, default_label="Unknown"):
        labels = []
        values = []
        for row in query_res:
            label, val = row
            labels.append(str(label) if label else default_label)
            values.append(val or 0)
        return ChartData(labels=labels, values=values)

    org_stats = db.query(Organization.name, func.count(Job.id)).join(Job).filter(Job.is_trashed == False).group_by(Organization.name).order_by(func.count(Job.id).desc()).limit(10).all()
    min_stats = db.query(Organization.ministry, func.count(Job.id)).join(Job).filter(Job.is_trashed == False).group_by(Organization.ministry).all()
    qual_stats = db.query(Job.qualification, func.count(Job.id)).filter(Job.is_trashed == False).group_by(Job.qualification).all()
    
    salary_stats = db.query(
        func.case(
            (Job.salary < 50000, '< 50k'),
            (Job.salary < 100000, '50k - 1L'),
            (Job.salary >= 100000, '> 1L'),
            else_='Unknown'
        ).label('bracket'),
        func.count(Job.id)
    ).filter(Job.is_trashed == False, Job.salary > 0).group_by('bracket').all()
    
    age_stats = db.query(Job.age_limit, func.count(Job.id)).filter(Job.is_trashed == False).group_by(Job.age_limit).all()
    exp_stats = db.query(Job.experience_years, func.count(Job.id)).filter(Job.is_trashed == False).group_by(Job.experience_years).all()
    
    now = datetime.now()
    deadline_stats = db.query(Job.deadline, func.count(Job.id)).filter(Job.is_trashed == False, Job.deadline > now).group_by(Job.deadline).order_by(Job.deadline).limit(7).all()

    return AnalyticsResponse(
        total_jobs=total_jobs,
        active_applications=applied_count,
        average_salary=int(avg_sal),
        applied_vs_pending=ChartData(labels=["Applied", "Pending"], values=[applied_count, pending_count]),
        jobs_by_org=make_chart(org_stats),
        jobs_by_ministry=make_chart(min_stats, "Unknown Ministry"),
        jobs_by_qualification=make_chart(qual_stats, "Not Specified"),
        jobs_by_salary=make_chart(salary_stats),
        jobs_by_age=make_chart(age_stats, "Any Age"),
        jobs_by_experience=make_chart(exp_stats, "Fresher"),
        upcoming_deadlines=make_chart([(d.strftime('%m-%d'), c) if d else ('Unknown', c) for d, c in deadline_stats])
    )
"""
}

# Apply files
for filepath, content in files.items():
    full_path = os.path.join(project_root, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)

print("Phase 23 Analytics Backend Complete.")
