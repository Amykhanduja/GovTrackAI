import os

project_root = "/mnt/c/Users/khand/GovTrackAI"
schemas_path = os.path.join(project_root, "api", "models", "schemas.py")
analytics_path = os.path.join(project_root, "api", "routers", "analytics.py")
index_path = os.path.join(project_root, "frontend", "index.html")
app_js_path = os.path.join(project_root, "frontend", "app.js")

# 1. Update Schemas
with open(schemas_path, "r") as f:
    schemas = f.read()

schemas = schemas.replace(
"""class AnalyticsResponse(BaseModel):
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
    upcoming_deadlines: ChartData""",
"""class AnalyticsResponse(BaseModel):
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
    top_paying_orgs: ChartData"""
)

with open(schemas_path, "w") as f:
    f.write(schemas)


# 2. Update Analytics Router
analytics_code = '''from fastapi import APIRouter, Depends, Query
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
    
    bookmarks = q_base.filter(Job.fav > 0).count()
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
    
    fav_orgs = db.query(Organization.name, func.count(Job.id)).join(Job).filter(Job.fav > 0).group_by(Organization.name).limit(5).all()
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
'''
with open(analytics_path, "w") as f:
    f.write(analytics_code)


# 3. Update HTML
import re
with open(index_path, "r") as f:
    html = f.read()

analytics_html = '''<!-- Analytics View -->
            <div class="view-container" id="analyticsView">
                <div class="analytics-toolbar" style="display:flex; gap:10px; margin-bottom: 20px;">
                    <select id="anFilterDomain" class="tool-select"><option value="">All Domains</option><option value="foreign_lang">Foreign Lang</option><option value="cyber_tech">Cyber Tech</option></select>
                    <select id="anFilterStatus" class="tool-select"><option value="">All Statuses</option><option value="Applications Open">Open</option><option value="Closed">Closed</option></select>
                    <button class="tool-btn" onclick="fetchAnalytics()">Filter Dashboard</button>
                </div>
                
                <div class="kpi-grid" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:15px; margin-bottom: 30px;">
                    <div class="kpi-card" style="background:var(--card-bg); padding:15px; border-radius:12px; border:1px solid var(--border-color); text-align:center;">
                        <div style="font-size:12px; color:var(--text-muted);">Avg Salary</div>
                        <div id="kpiAvgSal" style="font-size:24px; font-weight:bold; color:#10b981;">₹0</div>
                    </div>
                    <div class="kpi-card" style="background:var(--card-bg); padding:15px; border-radius:12px; border:1px solid var(--border-color); text-align:center;">
                        <div style="font-size:12px; color:var(--text-muted);">High Salary</div>
                        <div id="kpiHighSal" style="font-size:24px; font-weight:bold; color:#f59e0b;">₹0</div>
                    </div>
                    <div class="kpi-card" style="background:var(--card-bg); padding:15px; border-radius:12px; border:1px solid var(--border-color); text-align:center;">
                        <div style="font-size:12px; color:var(--text-muted);">Bookmarks</div>
                        <div id="kpiBooks" style="font-size:24px; font-weight:bold; color:#8b5cf6;">0</div>
                    </div>
                    <div class="kpi-card" style="background:var(--card-bg); padding:15px; border-radius:12px; border:1px solid var(--border-color); text-align:center;">
                        <div style="font-size:12px; color:var(--text-muted);">Closing Week</div>
                        <div id="kpiWeek" style="font-size:24px; font-weight:bold; color:#ef4444;">0</div>
                    </div>
                </div>

                <div class="analytics-grid">
                    <div class="chart-card"><h3>Applied vs Pending</h3><canvas id="chartApplied"></canvas></div>
                    <div class="chart-card"><h3>Apps by Org</h3><canvas id="chartAppOrg"></canvas></div>
                    <div class="chart-card"><h3>Apps by Ministry</h3><canvas id="chartAppMin"></canvas></div>
                    <div class="chart-card"><h3>Jobs by Domain</h3><canvas id="chartDomain"></canvas></div>
                    <div class="chart-card"><h3>Jobs by Qual</h3><canvas id="chartQual"></canvas></div>
                    <div class="chart-card"><h3>Jobs by Salary</h3><canvas id="chartSal"></canvas></div>
                    <div class="chart-card"><h3>Jobs by Age</h3><canvas id="chartAge"></canvas></div>
                    <div class="chart-card"><h3>Jobs by Exp</h3><canvas id="chartExp"></canvas></div>
                    <div class="chart-card"><h3>Monthly Trend</h3><canvas id="chartTrend"></canvas></div>
                    <div class="chart-card"><h3>Upcoming Deadlines</h3><canvas id="chartDeadlines"></canvas></div>
                    <div class="chart-card"><h3>Favorite Orgs</h3><canvas id="chartFav"></canvas></div>
                    <div class="chart-card"><h3>Most Applied Orgs</h3><canvas id="chartMostApp"></canvas></div>
                    <div class="chart-card"><h3>Top Recruiting Orgs</h3><canvas id="chartTopOrg"></canvas></div>
                    <div class="chart-card"><h3>Top Paying Orgs</h3><canvas id="chartTopPay"></canvas></div>
                </div>
                <div id="analyticsEmptyState" class="empty-state" style="display: none;">No data available.</div>
            </div>'''
            
html = re.sub(r'<!-- Analytics View -->.*?</div>\s+<!-- Calendar View -->', analytics_html + '\n            <!-- Calendar View -->', html, flags=re.DOTALL)
with open(index_path, "w") as f:
    f.write(html)

# 4. Update app.js
with open(app_js_path, "r") as f:
    app_js = f.read()

app_js_analytics = '''async function fetchAnalytics() {
    try {
        const dom = document.getElementById('anFilterDomain').value;
        const stat = document.getElementById('anFilterStatus').value;
        let url = `${API_BASE}/analytics/?`;
        if (dom) url += `domain=${dom}&`;
        else if (currentDomain) url += `domain=${currentDomain}&`;
        if (stat) url += `status=${encodeURIComponent(stat)}&`;
        
        const res = await fetch(url);
        const data = await res.json();
        
        if (data.total_jobs === 0) {
            document.querySelector('.analytics-grid').style.display = 'none';
            document.querySelector('.kpi-grid').style.display = 'none';
            if(analyticsEmptyState) analyticsEmptyState.style.display = 'block';
            return;
        }
        document.querySelector('.analytics-grid').style.display = 'grid';
        document.querySelector('.kpi-grid').style.display = 'grid';
        if(analyticsEmptyState) analyticsEmptyState.style.display = 'none';
        
        document.getElementById('kpiAvgSal').textContent = '₹' + data.average_salary.toLocaleString();
        document.getElementById('kpiHighSal').textContent = '₹' + data.highest_salary.toLocaleString();
        document.getElementById('kpiBooks').textContent = data.bookmarks;
        document.getElementById('kpiWeek').textContent = data.jobs_closing_this_week;
        
        const c1 = ['#3b82f6', 'rgba(255,255,255,0.1)'];
        const cMulti = ['#3b82f6', '#f59e0b', '#10b981', '#8b5cf6', '#ec4899', '#06b6d4', '#f43f5e', '#6366f1', '#14b8a6', '#84cc16'];
        
        renderChart('chartApplied', 'doughnut', data.applied_vs_pending, c1);
        renderChart('chartAppOrg', 'bar', data.applications_by_org, '#3b82f6');
        renderChart('chartAppMin', 'pie', data.applications_by_ministry, cMulti);
        renderChart('chartDomain', 'pie', data.jobs_by_domain, cMulti);
        renderChart('chartQual', 'bar', data.jobs_by_qual, '#10b981');
        renderChart('chartSal', 'bar', data.jobs_by_salary, '#f59e0b');
        renderChart('chartAge', 'line', data.jobs_by_age, '#8b5cf6');
        renderChart('chartExp', 'bar', data.jobs_by_exp, '#06b6d4');
        renderChart('chartTrend', 'line', data.monthly_trend, '#ec4899');
        renderChart('chartDeadlines', 'bar', data.upcoming_deadlines, '#ef4444');
        renderChart('chartFav', 'bar', data.favorite_orgs, '#f59e0b');
        renderChart('chartMostApp', 'bar', data.most_applied_orgs, '#10b981');
        renderChart('chartTopOrg', 'bar', data.top_recruiting_orgs, '#3b82f6');
        renderChart('chartTopPay', 'bar', data.top_paying_orgs, '#8b5cf6');
    } catch(e) { console.error(e); }
}'''

app_js = re.sub(r'async function fetchAnalytics\(\) \{.*?\n\}', app_js_analytics, app_js, flags=re.DOTALL)
with open(app_js_path, "w") as f:
    f.write(app_js)

print("Phase 31 completed successfully")
