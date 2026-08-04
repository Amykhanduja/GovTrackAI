from pydantic import BaseModel
from typing import List, Optional

class JobResponse(BaseModel):
    id: int
    org: str
    post: str
    salary: Optional[int]
    status: str
    priority: int
    deadline: Optional[str]

class AnalyticsResponse(BaseModel):
    total_jobs: int
    active_applications: int
    average_salary: int
    top_skills: List[str]
