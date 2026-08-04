from fastapi import APIRouter
from api.models.schemas import AnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/", response_model=AnalyticsResponse)
def get_analytics():
    return {
        "total_jobs": 450,
        "active_applications": 12,
        "average_salary": 85000,
        "top_skills": ["Python", "Cyber Security", "Cloud"]
    }
