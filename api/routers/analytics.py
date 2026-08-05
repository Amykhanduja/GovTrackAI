from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from datetime import datetime, timedelta
from db.models import Job, Organization
from api.models.schemas import AnalyticsResponse, ChartData
from api.routers.jobs import get_db
import logging

logger = logging.getLogger('app.analytics')
router = APIRouter(prefix="/analytics", tags=["Analytics"])

def make_chart(query_res, default_label="Unknown"):
    labels = []
    values = []
    for row in query_res:
        label, val = row
        labels.append(str(label) if label else default_label)
        values.append(val or 0)
    return ChartData(labels=labels, values=values)

@router.get("/", response_model=AnalyticsResponse)
def get_analytics(
    domain: str = None, 
    org_name: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    q_base = db.query(Job)
    if domain: q_base = q_base.filter(Job.domain == domain)
    if org_name: q_base = q_base.join(Organization).filter(Organization.name == org_name)
    if status: q_base = q_base.filter(Job.status == status)
    
    now = datetime.now()
    
    total = q_base.count()
    applied = q_base.filter(Job.is_applied == True).count()
    pending = total - applied
    
    salaries = q_base.filter(Job.salary > 0).all()
    avg_sal = sum(s.salary for s in salaries) / len(salaries) if salaries else 0
    max_sal = max((s.salary for s in salaries), default=0)
    min_sal = min((s.salary for s in salaries), default=0)
    
    bookmarks = q_base.filter(Job.priority > 0).count()
    hidden = q_base.filter(Job.is_hidden == True).count()
    archived = q_base.filter(Job.is_archived == True).count()
    trash = q_base.filter(Job.is_trashed == True).count()
    
    today = now.date()
    end_of_week = today + timedelta(days=7)
    end_of_month = today + timedelta(days=30)
    
    jobs_today = q_base.filter(func.date(Job.deadline) == today).count()
    jobs_week = q_base.filter(func.date(Job.deadline) >= today, func.date(Job.deadline) <= end_of_week).count()
    jobs_month = q_base.filter(func.date(Job.deadline) >= today, func.date(Job.deadline) <= end_of_month).count()

    # Active jobs only for most charts
    q_act = q_base.filter(Job.is_trashed == False)
    
    org_apps = db.query(Organization.name, func.count(Job.id)).join(Job).filter(Job.is_applied == True).group_by(Organization.name).all()
    min_apps = db.query(Organization.category, func.count(Job.id)).join(Job).filter(Job.is_applied == True).group_by(Organization.category).all()
    
    domain_jobs = db.query(Job.domain, func.count(Job.id)).filter(Job.is_trashed == False).group_by(Job.domain).all()
    qual_jobs = db.query(Job.qualification, func.count(Job.id)).filter(Job.is_trashed == False).group_by(Job.qualification).order_by(func.count(Job.id).desc()).limit(10).all()
    
    sal_ranges = db.query(
        case((Job.salary < 50000, '< 50k'), (Job.salary < 100000, '50k - 1L'), (Job.salary >= 100000, '> 1L'), else_='Unknown').label('bracket'),
        func.count(Job.id)
    ).filter(Job.salary > 0).group_by('bracket').all()
    
    age_jobs = db.query(Job.age_limit, func.count(Job.id)).filter(Job.age_limit > 0).group_by(Job.age_limit).all()
    exp_jobs = db.query(Job.experience_years, func.count(Job.id)).group_by(Job.experience_years).all()
    
    monthly = db.query(func.strftime('%Y-%m', Job.created_at), func.count(Job.id)).group_by(func.strftime('%Y-%m', Job.created_at)).all()
    
    deadlines = db.query(func.strftime('%Y-%m-%d', Job.deadline), func.count(Job.id)).filter(Job.deadline > now).group_by(func.strftime('%Y-%m-%d', Job.deadline)).limit(10).all()
    
    fav_orgs = db.query(Organization.name, func.count(Job.id)).join(Job).filter(Job.priority > 0).group_by(Organization.name).limit(5).all()
    most_app_orgs = db.query(Organization.name, func.count(Job.id)).join(Job).filter(Job.is_applied == True).group_by(Organization.name).order_by(func.count(Job.id).desc()).limit(5).all()
    
    top_orgs = db.query(Organization.name, func.count(Job.id)).join(Job).group_by(Organization.name).order_by(func.count(Job.id).desc()).limit(10).all()
    top_paying = db.query(Organization.name, func.max(Job.salary)).join(Job).group_by(Organization.name).order_by(func.max(Job.salary).desc()).limit(10).all()

    return AnalyticsResponse(
        total_jobs=total, active_applications=applied, average_salary=int(avg_sal), highest_salary=max_sal, lowest_salary=min_sal,
        bookmarks=bookmarks, hidden_jobs=hidden, archived_jobs=archived, trash_jobs=trash,
        jobs_closing_today=jobs_today, jobs_closing_this_week=jobs_week, jobs_closing_this_month=jobs_month,
        
        applied_vs_pending=make_chart([("Applied", applied), ("Pending", pending)]),
        applications_by_org=make_chart(org_apps, "Unknown"),
        applications_by_ministry=make_chart(min_apps, "Unknown"),
        jobs_by_domain=make_chart(domain_jobs, "Uncategorized"),
        jobs_by_qual=make_chart(qual_jobs, "Not Specified"),
        jobs_by_salary=make_chart(sal_ranges, "Unknown"),
        jobs_by_age=make_chart(age_jobs, "Any Age"),
        jobs_by_exp=make_chart(exp_jobs, "Fresher"),
        monthly_trend=make_chart(monthly, "Unknown Date"),
        upcoming_deadlines=make_chart(deadlines, "Unknown"),
        favorite_orgs=make_chart(fav_orgs, "Unknown"),
        most_applied_orgs=make_chart(most_app_orgs, "Unknown"),
        top_recruiting_orgs=make_chart(top_orgs, "Unknown"),
        top_paying_orgs=make_chart(top_paying, "Unknown")
    )
