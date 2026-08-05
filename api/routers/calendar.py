from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from db.models import Job, Organization, Exam
from api.routers.jobs import get_db
import logging
from datetime import datetime

logger = logging.getLogger('app.calendar')
router = APIRouter(prefix="/calendar", tags=["Calendar"])

@router.get("/events")
def get_calendar_events(
    domain: Optional[str] = None,
    org_name: Optional[str] = None,
    status: Optional[str] = None,
    state: Optional[str] = None,
    priority: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Job, Organization.name.label("org_name")).join(
        Organization, Job.org_id == Organization.id
    ).filter(Job.is_trashed == False, Job.is_archived == False)
    
    if domain: query = query.filter(Job.domain == domain)
    if org_name: query = query.filter(Organization.name == org_name)
    if status: query = query.filter(Job.status == status)
    if state: query = query.filter(Job.state == state)
    if priority is not None: query = query.filter(Job.priority == priority)
        
    jobs = query.all()
    job_ids = [j[0].id for j in jobs]
    exams = db.query(Exam).filter(Exam.job_id.in_(job_ids)).all() if job_ids else []
    
    exam_dict = {}
    for ex in exams:
        if ex.job_id not in exam_dict: exam_dict[ex.job_id] = []
        if ex.exam_date: exam_dict[ex.job_id].append(ex.exam_date)

    events = []
    
    for job, org in jobs:
        base_title = f"{org} - {job.title}"
        url = job.url or "#"
        
        if job.start_date:
            events.append({"id": f"s_{job.id}", "title": f"OPEN: {base_title}", "start": job.start_date.isoformat(), "color": "#107c10", "url": url})
        if job.deadline:
            events.append({"id": f"c_{job.id}", "title": f"DEADLINE: {base_title}", "start": job.deadline.isoformat(), "color": "#d83b01", "url": url})
        if job.id in exam_dict:
            for i, edate in enumerate(exam_dict[job.id]):
                events.append({"id": f"e_{job.id}_{i}", "title": f"EXAM: {base_title}", "start": edate.isoformat(), "color": "#0078d4", "url": url})
        if job.interview_date:
            events.append({"id": f"i_{job.id}", "title": f"INTERVIEW: {base_title}", "start": job.interview_date.isoformat(), "color": "#5c2d91", "url": url})
        if job.result_date:
            events.append({"id": f"r_{job.id}", "title": f"RESULT: {base_title}", "start": job.result_date.isoformat(), "color": "#ffb900", "url": url})
        if job.joining_date:
            events.append({"id": f"j_{job.id}", "title": f"JOINING: {base_title}", "start": job.joining_date.isoformat(), "color": "#008272", "url": url})

    return events

@router.get("/filters")
def get_calendar_filters(domain: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Job, Organization.name.label("org_name")).join(Organization, Job.org_id == Organization.id).filter(Job.is_trashed == False)
    if domain: q = q.filter(Job.domain == domain)
        
    jobs = q.all()
    orgs = list(set([org_name for j, org_name in jobs if org_name]))
    states = list(set([j[0].state for j in jobs if j[0].state]))
    statuses = list(set([j[0].status for j in jobs if j[0].status]))
    priorities = list(set([j[0].priority for j in jobs if j[0].priority is not None]))
    
    return {
        "orgs": sorted(orgs),
        "states": sorted(states),
        "statuses": sorted(statuses),
        "priorities": sorted(priorities)
    }
