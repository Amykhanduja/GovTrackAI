from fastapi import APIRouter, Query
from typing import List
from api.models.schemas import JobResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# Mock DB Data
MOCK_JOBS = [
    {"id": 1, "org": "RBI", "post": "Grade B", "salary": 120000, "status": "New", "priority": 95, "deadline": "2026-10-01"},
    {"id": 2, "org": "NIC", "post": "Scientist B", "salary": 150000, "status": "Applied", "priority": 90, "deadline": "2026-09-15"},
    {"id": 3, "org": "ISRO", "post": "Scientist", "salary": 140000, "status": "New", "priority": 85, "deadline": "2026-11-01"},
]

@router.get("/", response_model=List[JobResponse])
def get_jobs(skip: int = 0, limit: int = 10, search: str = None):
    # Simulates DB fetch, pagination, search
    results = MOCK_JOBS
    if search:
        results = [j for j in results if search.lower() in j['org'].lower() or search.lower() in j['post'].lower()]
    return results[skip : skip + limit]

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int):
    for j in MOCK_JOBS:
        if j['id'] == job_id:
            return j
    return None
