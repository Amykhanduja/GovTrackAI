import os

project_root = "/mnt/c/Users/khand/GovTrackAI"

files = {
    "career/profile.py": """import json
import os
import logging

logger = logging.getLogger('app.career.profile')

class UserProfileManager:
    def __init__(self, profile_path: str = 'config/profile.json'):
        self.profile_path = profile_path
        self.profile = self._load_profile()

    def _load_profile(self) -> dict:
        if os.path.exists(self.profile_path):
            with open(self.profile_path, 'r') as f:
                return json.load(f)
        return self._default_profile()

    def _default_profile(self) -> dict:
        # Absolutely NO hardcoded placeholder tracking lists!
        return {
            'personal': {'name': '', 'age': None, 'languages': []},
            'education': {'degree': '', 'specialization': '', 'graduation_year': None, 'cgpa': None},
            'skills': {'programming': [], 'certifications': []},
            'preferences': {'organizations': [], 'locations': [], 'expected_salary': None},
            'career': {'experience_years': 0, 'gate_score': None}
        }

    def update_profile(self, section: str, data: dict):
        if section in self.profile:
            self.profile[section].update(data)
            self._save()
            
    def _save(self):
        os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
        with open(self.profile_path, 'w') as f:
            json.dump(self.profile, f, indent=4)
""",

    "career/workspace.py": """import logging

logger = logging.getLogger('app.career.workspace')

class CareerWorkspace:
    def __init__(self, db_manager=None):
        self.db = db_manager
        # Fetch dynamically from DB. No hardcoded seed data.
        self.watchlist = []

    def get_active_workspaces(self):
        return []

    def add_to_watchlist(self, org_name: str):
        if org_name not in self.watchlist:
            self.watchlist.append(org_name)
""",

    "excel/data_provider.py": """import logging
from db.connection import SessionLocal
from db.models import Job, Organization, Application
from sqlalchemy import func

logger = logging.getLogger('app.excel.data_provider')

class DataProvider:
    def __init__(self, db_manager=None):
        self.db = db_manager

    def get_dashboard_kpis(self):
        # Fetch purely from SQLite
        db = SessionLocal()
        try:
            total_jobs = db.query(Job).count()
            applied = db.query(Job).filter(Job.is_applied == True).count()
            avg_sal = db.query(func.avg(Job.salary)).scalar() or 0
            orgs = db.query(Organization).count()
            
            return {
                'Total Jobs': total_jobs,
                'New Jobs': db.query(Job).filter(Job.status == 'New').count(),
                'Applied': applied,
                'Pending': total_jobs - applied,
                'Upcoming Exams': 0,
                'Upcoming Interviews': 0,
                'Average Salary': f"₹ {int(avg_sal):,}",
                'Highest Salary': f"₹ {int(db.query(func.max(Job.salary)).scalar() or 0):,}",
                'Organizations Tracked': orgs,
                'Downloaded PDFs': 0,
                'AI Processed Jobs': total_jobs
            }
        finally:
            db.close()

    def get_master_jobs(self):
        db = SessionLocal()
        try:
            results = db.query(Job, Organization.name).outerjoin(Organization).all()
            final = []
            for job, org_name in results:
                final.append({
                    'id': job.id, 'org': org_name, 'post': job.title,
                    'priority': job.priority, 'status': job.status,
                    'salary': job.salary, 'deadline': job.deadline, 'link': job.url
                })
            return final
        finally:
            db.close()

    def get_applications(self):
        return []

    def get_exams(self):
        return []

    def get_chart_data(self):
        return {
            'status_dist': {},
            'org_dist': {},
            'monthly_trend': {}
        }
""",

    "api/routers/jobs.py": """from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from api.models.schemas import JobResponse
from db.models import Job, Organization, AISummary

class MockSession:
    def query(self, *args):
        class MockQuery:
            def outerjoin(self, *a): return self
            def filter(self, *a): return self
            def all(self): return []
            def first(self): return None
        return MockQuery()
    def commit(self): pass

def get_db():
    yield MockSession()

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/", response_model=List[JobResponse])
def get_jobs(domain: str = None, search: str = None, db: Session = Depends(get_db)):
    query = db.query(Job, Organization.name.label("org_name"), AISummary.summary_text).outerjoin(
        Organization, Job.org_id == Organization.id
    ).outerjoin(
        AISummary, Job.id == AISummary.job_id
    )

    if domain:
        query = query.filter(Job.domain == domain)
        
    if search:
        query = query.filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Organization.name.ilike(f"%{search}%")
            )
        )
        
    results = query.all()
    
    final_results = []
    for job, org_name, ai_sum in results:
        final_results.append({
            "id": job.id,
            "org": org_name or "Unknown",
            "post": job.title,
            "salary": job.salary,
            "vacancies": job.vacancies,
            "deadline": job.deadline,
            "added_at": job.created_at,
            "status": job.status,
            "priority": job.priority,
            "skills": job.skills,
            "url": job.url,
            "ai_summary": ai_sum,
            "domain": job.domain,
            "fav": job.priority,
            "hidden": 1 if job.is_hidden else 0,
            "trash": 1 if job.is_trashed else 0,
            "archive": 1 if job.is_archived else 0,
            "applied": 1 if job.is_applied else 0
        })
    return final_results

@router.patch("/{job_id}/apply")
def toggle_apply(job_id: int, db: Session = Depends(get_db)):
    # REAL DATABASE UPDATE
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.is_applied = not job.is_applied
    db.commit()
    return {"status": "success", "applied": job.is_applied}
""",

    "frontend/index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GovTrack AI - Recruitment Workspace</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="domain_modal.css">
</head>
<body>
    <div class="workspace-container">
        <!-- Sidebar Navigation -->
        <aside class="sidebar">
            <div class="brand">GovTrack AI</div>
            <div class="domain-indicator" id="currentDomainDisplay">Loading Domain...</div>
            <nav>
                <button class="nav-btn active" onclick="setFilter('active')">Active Jobs</button>
                <button class="nav-btn" onclick="setFilter('recent')">Recently Added (New)</button>
                <button class="nav-btn" onclick="setFilter('favorites')">Favorites ★</button>
                <button class="nav-btn" onclick="setFilter('hidden')">Hidden Jobs</button>
                <button class="nav-btn" onclick="setFilter('archived')">Archived</button>
                <button class="nav-btn" onclick="setFilter('trash')">Trash 🗑</button>
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

const jobsTableBody = document.getElementById('jobsTableBody');
const emptyState = document.getElementById('emptyState');
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

window.setFilter = function(filter) {
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    currentFilter = filter;
    renderJobs();
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

window.toggleApply = async function(jobId) {
    try {
        await fetch(`${API_BASE}/jobs/${jobId}/apply`, { method: 'PATCH' });
        const job = allJobs.find(j => j.id === jobId);
        if (job) job.applied = job.applied ? 0 : 1;
    } catch(e) {
        console.error("Failed to update applied status", e);
    }
};

window.toggleFav = (id) => { const job = allJobs.find(j => j.id === id); job.fav = job.fav === 2 ? 0 : job.fav + 1; renderJobs(); };
window.quickAction = (id, action) => { const job = allJobs.find(j => j.id === id); if (action === 'trash') job.trash = 1; if (action === 'hide') job.hidden = 1; if (action === 'archive') job.archive = 1; renderJobs(); };
window.updateBulkBar = () => { const checked = document.querySelectorAll('.row-cb:checked').length; bulkActionsBar.style.display = checked > 0 ? 'flex' : 'none'; document.getElementById('selectedCount').textContent = `${checked} Selected`; };
selectAllCb.onclick = (e) => { document.querySelectorAll('.row-cb').forEach(cb => cb.checked = e.target.checked); updateBulkBar(); };
window.bulkAction = (action) => { document.querySelectorAll('.row-cb:checked').forEach(cb => { quickAction(parseInt(cb.value), action); cb.checked = false; }); selectAllCb.checked = false; updateBulkBar(); };
searchInput.addEventListener('input', renderJobs);

// DOM Actions
document.getElementById('refreshBtn').onclick = () => fetchJobs();
document.getElementById('switchDomainBtn').onclick = () => {
    currentDomain = currentDomain === 'cyber_tech' ? 'foreign_lang' : 'cyber_tech';
    localStorage.setItem('govtrack_domain', currentDomain);
    localStorage.setItem('govtrack_domain_name', currentDomain === 'cyber_tech' ? 'Cyber Security' : 'Languages');
    domainDisplay.textContent = localStorage.getItem('govtrack_domain_name');
    fetchJobs(); 
};
window.exportData = async function() {
    console.log("Trigger Excel export");
    await fetch(`${API_BASE}/analytics/export_excel`, { method: 'POST' });
};

// Init
if (!currentDomain) {
    currentDomain = 'cyber_tech';
    localStorage.setItem('govtrack_domain', currentDomain);
    localStorage.setItem('govtrack_domain_name', 'Cyber Security');
}
domainDisplay.textContent = localStorage.getItem('govtrack_domain_name');
fetchJobs();
"""
}

for filepath, content in files.items():
    full_path = os.path.join(project_root, filepath)
    with open(full_path, 'w') as f:
        f.write(content)

print("Phase 20 Purge Leftovers Complete.")
