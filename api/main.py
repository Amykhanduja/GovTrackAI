from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routers import jobs, analytics, profile, calendar, excel_sync

app = FastAPI(title="GovTrack AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(calendar.router, prefix="/api/v1")
app.include_router(excel_sync.router, prefix="/api/v1")

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
