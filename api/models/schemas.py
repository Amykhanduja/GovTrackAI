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
    highest_salary: int
    lowest_salary: int
    bookmarks: int
    hidden_jobs: int
    archived_jobs: int
    trash_jobs: int
    jobs_closing_today: int
    jobs_closing_this_week: int
    jobs_closing_this_month: int
    
    applied_vs_pending: ChartData
    applications_by_org: ChartData
    applications_by_ministry: ChartData
    jobs_by_domain: ChartData
    jobs_by_qual: ChartData
    jobs_by_salary: ChartData
    jobs_by_age: ChartData
    jobs_by_exp: ChartData
    monthly_trend: ChartData
    upcoming_deadlines: ChartData
    favorite_orgs: ChartData
    most_applied_orgs: ChartData
    top_recruiting_orgs: ChartData
    top_paying_orgs: ChartData
