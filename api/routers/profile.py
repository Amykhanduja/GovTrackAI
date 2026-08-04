from fastapi import APIRouter

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/")
def get_profile():
    # Ready for auth architecture
    return {"name": "GovTrack User", "target": "Cyber Security", "completion": "85%"}
