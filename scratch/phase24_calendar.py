import os

project_root = "/mnt/c/Users/khand/GovTrackAI"

files = {
    "api/routers/calendar.py": """from fastapi import APIRouter, Depends, Query
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
    job_ids = [j.Job.id for j in jobs]
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
    states = list(set([j.Job.state for j, _ in jobs if j.Job.state]))
    statuses = list(set([j.Job.status for j, _ in jobs if j.Job.status]))
    priorities = list(set([j.Job.priority for j, _ in jobs if j.Job.priority is not None]))
    
    return {
        "orgs": sorted(orgs),
        "states": sorted(states),
        "statuses": sorted(statuses),
        "priorities": sorted(priorities)
    }
""",

    "api/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routers import jobs, analytics, profile, calendar

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

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
""",

    "frontend/index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GovTrack AI - Recruitment Workspace</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="domain_modal.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.15/index.global.min.js"></script>
</head>
<body>
    <div class="workspace-container">
        <!-- Sidebar Navigation -->
        <aside class="sidebar">
            <div class="brand">GovTrack AI</div>
            <div class="domain-indicator" id="currentDomainDisplay">Loading Domain...</div>
            <nav>
                <button class="nav-btn active" onclick="switchTab('tableView', 'active')">Active Jobs</button>
                <button class="nav-btn" onclick="switchTab('tableView', 'recent')">Recently Added</button>
                <button class="nav-btn" onclick="switchTab('tableView', 'favorites')">Favorites ★</button>
                <button class="nav-btn" onclick="switchTab('analyticsView', 'analytics')">📊 Analytics</button>
                <button class="nav-btn" onclick="switchTab('calendarView', 'calendar')">📅 Calendar</button>
                <button class="nav-btn" onclick="switchTab('tableView', 'hidden')">Hidden Jobs</button>
                <button class="nav-btn" onclick="switchTab('tableView', 'archived')">Archived</button>
                <button class="nav-btn" onclick="switchTab('tableView', 'trash')">Trash 🗑</button>
            </nav>
            <div class="sidebar-bottom">
                <button id="refreshBtn" class="action-btn">Refresh Data</button>
                <button id="switchDomainBtn" class="action-btn">Switch Domain</button>
            </div>
        </aside>

        <main class="main-content">
            <header class="toolbar">
                <div class="search-bar">
                    <input type="text" id="globalSearch" placeholder="Search Database...">
                </div>
                <div class="toolbar-actions">
                    <select id="statusFilter" class="tool-select">
                        <option value="active">Active & Upcoming</option>
                        <option value="all">All Recruitments</option>
                        <option value="closed">Closed Only</option>
                    </select>
                    <button class="tool-btn" onclick="exportData()">Export Excel</button>
                </div>
            </header>

            <div class="bulk-actions" id="bulkActions" style="display: none;">
                <span id="selectedCount">0 Selected</span>
                <button onclick="bulkAction('favorite')">★ Favorite</button>
                <button onclick="bulkAction('archive')">📦 Archive</button>
                <button onclick="bulkAction('hide')">👁 Hide</button>
                <button onclick="bulkAction('trash')" class="danger">🗑 Trash</button>
            </div>

            <!-- Stats Modal Overlay -->
            <div id="statsModal" class="stats-modal" style="display:none;">
                <div class="stats-content">
                    <h3>Refresh Complete</h3>
                    <div class="stat-row"><span>Organizations Scanned:</span> <span id="statOrgs">0</span></div>
                    <div class="stat-row"><span>Jobs Added:</span> <span id="statAdded" style="color: green; font-weight: bold;">0</span></div>
                    <div class="stat-row"><span>Jobs Updated:</span> <span id="statUpdated">0</span></div>
                    <div class="stat-row"><span>Jobs Auto-Archived:</span> <span id="statArchived" style="color: #d83b01;">0</span></div>
                    <div class="stat-row"><span>Scraping Duration:</span> <span id="statDuration">0s</span></div>
                    <div class="stat-row"><span>Failed Organizations:</span> <span id="statFailed" style="color: red;">None</span></div>
                    <div class="stat-row"><span>Last Successful Refresh:</span> <span id="statLast">N/A</span></div>
                    <button class="tool-btn" onclick="document.getElementById('statsModal').style.display='none'" style="margin-top: 15px; width: 100%;">Close</button>
                </div>
            </div>

            <!-- Table View -->
            <div class="view-container active" id="tableView">
                <div class="table-wrapper">
                    <table class="data-grid" id="jobsTable">
                        <thead>
                            <tr>
                                <th style="width: 40px;"><input type="checkbox" id="selectAll"></th>
                                <th style="width: 50px;">Fav</th>
                                <th>Org</th>
                                <th>Post</th>
                                <th>Salary</th>
                                <th>Deadline</th>
                                <th>Status</th>
                                <th style="width: 70px;">Applied</th>
                                <th>Quick Actions</th>
                            </tr>
                        </thead>
                        <tbody id="jobsTableBody">
                        </tbody>
                    </table>
                    <div id="emptyState" class="empty-state" style="display: none;">
                        No recruitment notifications found.
                    </div>
                </div>
            </div>

            <!-- Analytics View -->
            <div class="view-container" id="analyticsView">
                <div class="analytics-grid">
                    <div class="chart-card">
                        <h3>Applied vs Pending</h3>
                        <canvas id="chartApplied"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Jobs by Organization</h3>
                        <canvas id="chartOrg"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Jobs by Ministry</h3>
                        <canvas id="chartMinistry"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Jobs by Qualification</h3>
                        <canvas id="chartQual"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Jobs by Salary</h3>
                        <canvas id="chartSalary"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Jobs by Age Limit</h3>
                        <canvas id="chartAge"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Jobs by Experience</h3>
                        <canvas id="chartExp"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Upcoming Deadlines</h3>
                        <canvas id="chartDeadline"></canvas>
                    </div>
                </div>
                <div id="analyticsEmptyState" class="empty-state" style="display: none;">
                    No data available in the database to generate charts.
                </div>
            </div>
            
            <!-- Calendar View -->
            <div class="view-container" id="calendarView" style="flex-direction:column; padding:15px; height: 100%;">
                <div class="calendar-toolbar" style="margin-bottom:15px; display:flex; gap:10px;">
                    <select id="calFilterOrg" class="tool-select"><option value="">All Orgs</option></select>
                    <select id="calFilterState" class="tool-select"><option value="">All States</option></select>
                    <select id="calFilterStatus" class="tool-select"><option value="">All Statuses</option></select>
                    <select id="calFilterPriority" class="tool-select"><option value="">All Priorities</option></select>
                    <button class="tool-btn" onclick="fetchCalendarEvents()">Apply Filters</button>
                </div>
                <div id="calendarEl" style="flex:1; background:#fff; padding:10px; border-radius:6px; border:1px solid var(--border-color); min-height: 500px;"></div>
            </div>
        </main>
    </div>
    
    <script src="desktop_bridge.js"></script>
    <script src="app.js"></script>
</body>
</html>
""",

    "frontend/app.js": """const API_BASE = '/api/v1';
let currentDomain = localStorage.getItem('govtrack_domain') || null;
let currentFilter = 'active'; 
let allJobs = [];
let chartInstances = {};
let calendar = null;

const jobsTableBody = document.getElementById('jobsTableBody');
const emptyState = document.getElementById('emptyState');
const analyticsEmptyState = document.getElementById('analyticsEmptyState');
const domainDisplay = document.getElementById('currentDomainDisplay');
const searchInput = document.getElementById('globalSearch');
const selectAllCb = document.getElementById('selectAll');
const bulkActionsBar = document.getElementById('bulkActions');

function calculateStatus(deadlineIso) {
    if (!deadlineIso) return { text: 'Unknown', class: 'upcoming' };
    const dl = new Date(deadlineIso);
    const now = new Date();
    const diffDays = (dl - now) / (1000 * 60 * 60 * 24);
    
    if (diffDays < 0) return { text: 'Closed', class: 'closed' };
    if (diffDays <= 3) return { text: 'Closing Soon', class: 'closing' };
    if (diffDays > 30) return { text: 'Upcoming', class: 'upcoming' };
    return { text: 'Active', class: 'active' };
}

function isNew(addedIso) {
    if (!addedIso) return false;
    const added = new Date(addedIso);
    const diffHours = (new Date() - added) / (1000 * 60 * 60);
    return diffHours <= 24;
}

window.switchTab = function(viewId, filter) {
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    document.querySelectorAll('.view-container').forEach(v => { v.classList.remove('active'); v.style.display = 'none'; });
    const tgt = document.getElementById(viewId);
    tgt.classList.add('active');
    if(viewId === 'calendarView') tgt.style.display = 'flex';
    else tgt.style.display = viewId === 'tableView' ? 'flex' : 'block';
    
    if (viewId === 'tableView') {
        currentFilter = filter;
        renderJobs();
    } else if (viewId === 'analyticsView') {
        fetchAnalytics();
    } else if (viewId === 'calendarView') {
        fetchCalendarFilters();
        fetchCalendarEvents();
        setTimeout(() => { if (calendar) calendar.render(); }, 100);
    }
};

async function fetchJobs() {
    if (!currentDomain) return;
    try {
        const response = await fetch(`${API_BASE}/jobs/?domain=${currentDomain}`);
        if (!response.ok) throw new Error('API Error');
        allJobs = await response.json();
    } catch (e) {
        console.error("API Connection Error", e);
        allJobs = [];
        emptyState.style.display = 'block';
        emptyState.textContent = 'Unable to connect to backend.';
        jobsTableBody.innerHTML = '';
        return;
    }
    renderJobs();
}

function renderJobs() {
    jobsTableBody.innerHTML = '';
    const search = searchInput.value.toLowerCase();
    
    let filtered = allJobs.filter(job => {
        if (search && !job.org.toLowerCase().includes(search) && !job.post.toLowerCase().includes(search)) return false;
        if (currentFilter === 'trash') return job.trash === 1;
        if (currentFilter === 'hidden') return job.hidden === 1 && job.trash === 0;
        if (currentFilter === 'archived') return job.archive === 1 && job.trash === 0;
        if (currentFilter === 'favorites') return job.fav > 0 && job.trash === 0;
        if (currentFilter === 'recent') return isNew(job.added_at) && job.trash === 0;
        if (currentFilter === 'active') {
            if (job.trash || job.hidden || job.archive) return false;
            if (calculateStatus(job.deadline).text === 'Closed') return false; 
        }
        return true;
    });
    
    filtered.sort((a, b) => new Date(a.deadline) - new Date(b.deadline));

    if (filtered.length === 0) {
        emptyState.style.display = 'block';
        emptyState.textContent = 'No recruitment notifications found.';
        return;
    }
    emptyState.style.display = 'none';
    
    filtered.forEach(job => {
        const stat = calculateStatus(job.deadline);
        const newClass = isNew(job.added_at) && currentFilter !== 'recent' ? 'is-new' : '';
        const favClass = job.fav > 0 ? 'active' : '';
        const favIcon = job.fav === 2 ? '★★' : (job.fav === 1 ? '★' : '☆');
        
        const tr = document.createElement('tr');
        tr.className = newClass;
        tr.innerHTML = `
            <td><input type="checkbox" class="row-cb" value="${job.id}" onclick="updateBulkBar()"></td>
            <td class="fav-star ${favClass}" onclick="toggleFav(${job.id})">${favIcon}</td>
            <td><strong>${job.org}</strong> ${newClass ? '<span style="color:var(--primary);font-size:10px;">(NEW)</span>' : ''}</td>
            <td>${job.post}</td>
            <td>₹${job.salary ? job.salary.toLocaleString() : 'N/A'}</td>
            <td>${job.deadline ? new Date(job.deadline).toLocaleDateString() : 'N/A'}</td>
            <td><span class="badge ${stat.class}">${stat.text}</span></td>
            <td><input type="checkbox" onclick="event.stopPropagation(); toggleApply(${job.id})" ${job.applied ? 'checked' : ''}></td>
            <td class="quick-actions">
                <button title="Apply/View" onclick="window.open('${job.url || '#'}')">🔗</button>
                <button title="Hide" onclick="quickAction(${job.id}, 'hide')">👁</button>
                <button title="Archive" onclick="quickAction(${job.id}, 'archive')">📦</button>
                <button title="Move to Trash" onclick="quickAction(${job.id}, 'trash')">🗑</button>
            </td>
        `;
        jobsTableBody.appendChild(tr);
    });
}

// Charting
function renderChart(canvasId, type, dataObj, palette) {
    if (chartInstances[canvasId]) chartInstances[canvasId].destroy();
    const ctx = document.getElementById(canvasId).getContext('2d');
    chartInstances[canvasId] = new Chart(ctx, {
        type: type,
        data: { labels: dataObj.labels, datasets: [{ data: dataObj.values, backgroundColor: palette, borderWidth: 1 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: type === 'doughnut' || type === 'pie' } } }
    });
}

async function fetchAnalytics() {
    if (!currentDomain) return;
    try {
        const res = await fetch(`${API_BASE}/analytics/?domain=${currentDomain}`);
        const data = await res.json();
        if (data.total_jobs === 0) {
            document.querySelector('.analytics-grid').style.display = 'none';
            analyticsEmptyState.style.display = 'block';
            return;
        }
        document.querySelector('.analytics-grid').style.display = 'grid';
        analyticsEmptyState.style.display = 'none';
        
        const c1 = ['#0078d4', '#e0e0e0'];
        const cMulti = ['#0078d4', '#d83b01', '#107c10', '#ffb900', '#5c2d91', '#008272', '#a80000'];
        
        renderChart('chartApplied', 'doughnut', data.applied_vs_pending, c1);
        renderChart('chartOrg', 'bar', data.jobs_by_org, '#0078d4');
        renderChart('chartMinistry', 'pie', data.jobs_by_ministry, cMulti);
        renderChart('chartQual', 'bar', data.jobs_by_qualification, '#107c10');
        renderChart('chartSalary', 'bar', data.jobs_by_salary, '#d83b01');
        renderChart('chartAge', 'line', data.jobs_by_age, '#5c2d91');
        renderChart('chartExp', 'bar', data.jobs_by_experience, '#008272');
        renderChart('chartDeadline', 'line', data.upcoming_deadlines, '#ffb900');
    } catch(e) {}
}

// Calendar Logic
window.fetchCalendarFilters = async function() {
    try {
        const res = await fetch(`${API_BASE}/calendar/filters?domain=${currentDomain || ''}`);
        const data = await res.json();
        
        const orgSel = document.getElementById('calFilterOrg');
        orgSel.innerHTML = '<option value="">All Orgs</option>';
        data.orgs.forEach(o => { orgSel.innerHTML += `<option value="${o}">${o}</option>`; });
        
        const stSel = document.getElementById('calFilterState');
        stSel.innerHTML = '<option value="">All States</option>';
        data.states.forEach(s => { stSel.innerHTML += `<option value="${s}">${s}</option>`; });
        
        const statSel = document.getElementById('calFilterStatus');
        statSel.innerHTML = '<option value="">All Statuses</option>';
        data.statuses.forEach(s => { statSel.innerHTML += `<option value="${s}">${s}</option>`; });
        
        const priSel = document.getElementById('calFilterPriority');
        priSel.innerHTML = '<option value="">All Priorities</option>';
        data.priorities.forEach(p => { priSel.innerHTML += `<option value="${p}">${p}</option>`; });
    } catch(e) {}
};

window.fetchCalendarEvents = async function() {
    const org = document.getElementById('calFilterOrg').value;
    const state = document.getElementById('calFilterState').value;
    const status = document.getElementById('calFilterStatus').value;
    const pri = document.getElementById('calFilterPriority').value;
    
    let url = `${API_BASE}/calendar/events?domain=${currentDomain || ''}`;
    if(org) url += `&org_name=${encodeURIComponent(org)}`;
    if(state) url += `&state=${encodeURIComponent(state)}`;
    if(status) url += `&status=${encodeURIComponent(status)}`;
    if(pri) url += `&priority=${pri}`;
    
    try {
        const res = await fetch(url);
        const events = await res.json();
        
        if(!calendar) {
            const calendarEl = document.getElementById('calendarEl');
            calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                events: events,
                height: '100%',
                eventClick: function(info) {
                    if(info.event.url && info.event.url !== '#') {
                        info.jsEvent.preventDefault();
                        window.open(info.event.url);
                    }
                }
            });
            calendar.render();
        } else {
            calendar.removeAllEvents();
            calendar.addEventSource(events);
        }
    } catch(e) {}
};

// UI Interactions
window.toggleApply = async function(jobId) {
    try {
        await fetch(`${API_BASE}/jobs/${jobId}/apply`, { method: 'PATCH' });
        const job = allJobs.find(j => j.id === jobId);
        if (job) job.applied = job.applied ? 0 : 1;
    } catch(e) {}
};
window.toggleFav = (id) => { const job = allJobs.find(j => j.id === id); job.fav = job.fav === 2 ? 0 : job.fav + 1; renderJobs(); };
window.quickAction = (id, action) => { const job = allJobs.find(j => j.id === id); if (action === 'trash') job.trash = 1; if (action === 'hide') job.hidden = 1; if (action === 'archive') job.archive = 1; renderJobs(); };
window.updateBulkBar = () => { const checked = document.querySelectorAll('.row-cb:checked').length; bulkActionsBar.style.display = checked > 0 ? 'flex' : 'none'; document.getElementById('selectedCount').textContent = `${checked} Selected`; };
selectAllCb.onclick = (e) => { document.querySelectorAll('.row-cb').forEach(cb => cb.checked = e.target.checked); updateBulkBar(); };
window.bulkAction = (action) => { document.querySelectorAll('.row-cb:checked').forEach(cb => { quickAction(parseInt(cb.value), action); cb.checked = false; }); selectAllCb.checked = false; updateBulkBar(); };
searchInput.addEventListener('input', renderJobs);

document.getElementById('refreshBtn').onclick = async () => {
    const btn = document.getElementById('refreshBtn');
    btn.textContent = 'Scraping...';
    btn.disabled = true;
    try {
        const res = await fetch(`${API_BASE}/jobs/refresh`, { method: 'POST' });
        const data = await res.json();
        
        document.getElementById('statOrgs').textContent = data.stats.organizations_scanned;
        document.getElementById('statAdded').textContent = data.stats.jobs_added;
        document.getElementById('statUpdated').textContent = data.stats.jobs_updated;
        document.getElementById('statArchived').textContent = data.stats.jobs_archived;
        document.getElementById('statDuration').textContent = data.stats.duration_seconds + 's';
        document.getElementById('statFailed').textContent = data.stats.failed_orgs.length > 0 ? data.stats.failed_orgs.join(', ') : 'None';
        document.getElementById('statLast').textContent = data.stats.last_successful_refresh;
        document.getElementById('statsModal').style.display = 'block';
        
        fetchJobs(); 
        if(document.getElementById('analyticsView').classList.contains('active')) fetchAnalytics();
        if(document.getElementById('calendarView').style.display === 'flex') fetchCalendarEvents();
    } catch(e) {
        console.error("Scraping failed", e);
    }
    btn.textContent = 'Refresh Data';
    btn.disabled = false;
};

document.getElementById('switchDomainBtn').onclick = () => {
    currentDomain = currentDomain === 'cyber_tech' ? 'foreign_lang' : 'cyber_tech';
    localStorage.setItem('govtrack_domain', currentDomain);
    localStorage.setItem('govtrack_domain_name', currentDomain === 'cyber_tech' ? 'Cyber Security' : 'Languages');
    domainDisplay.textContent = localStorage.getItem('govtrack_domain_name');
    fetchJobs(); 
    if(document.getElementById('analyticsView').classList.contains('active')) fetchAnalytics();
    if(document.getElementById('calendarView').style.display === 'flex') {
        fetchCalendarFilters();
        fetchCalendarEvents();
    }
};

window.exportData = async function() { await fetch(`${API_BASE}/analytics/export_excel`, { method: 'POST' }); };

if (!currentDomain) {
    currentDomain = 'cyber_tech';
    localStorage.setItem('govtrack_domain', currentDomain);
    localStorage.setItem('govtrack_domain_name', 'Cyber Security');
}
domainDisplay.textContent = localStorage.getItem('govtrack_domain_name');

// Hide inactive views initially
document.querySelectorAll('.view-container').forEach(v => { if(!v.classList.contains('active')) v.style.display = 'none'; });
fetchJobs();
"""
}

# Apply files
for filepath, content in files.items():
    full_path = os.path.join(project_root, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)

print("Phase 24 Calendar Backend and UI Complete.")
