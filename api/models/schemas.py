from pydantic import BaseModel
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
    age_limit: Optional[int] = None
    experience_years: Optional[int] = None
    qualification: Optional[str] = None
    description: Optional[str] = None

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
