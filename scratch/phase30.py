import os

project_root = "/mnt/c/Users/khand/GovTrackAI"
app_js_path = os.path.join(project_root, "frontend", "app.js")

with open(app_js_path, "r") as f:
    lines = f.readlines()

# We will completely overwrite app.js since Tabulator changes the entire core rendering loop.
app_js_code = '''const API_BASE = '/api/v1';
let currentDomain = localStorage.getItem('govtrack_domain') || null;
let currentFilter = 'active'; 
let allJobs = [];
let chartInstances = {};
let calendar = null;
let tabulatorTable = null;

const emptyState = document.getElementById('emptyState');
const analyticsEmptyState = document.getElementById('analyticsEmptyState');
const domainDisplay = document.getElementById('currentDomainDisplay');
const searchInput = document.getElementById('globalSearch');
const bulkActionsBar = document.getElementById('bulkActions');

function calculateStatus(deadlineIso) {
    if (!deadlineIso) return { text: 'Applications Open', class: 'active' };
    const dl = new Date(deadlineIso);
    const now = new Date();
    const diffDays = (dl - now) / (1000 * 60 * 60 * 24);
    
    if (diffDays < 0) return { text: 'Closed', class: 'closed' };
    if (diffDays <= 3) return { text: 'Closing Soon', class: 'closing' };
    if (diffDays > 30) return { text: 'Upcoming', class: 'upcoming' };
    return { text: 'Applications Open', class: 'active' };
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
        if(emptyState) {
            emptyState.style.display = 'block';
            emptyState.textContent = 'Unable to connect to backend.';
        }
        const loader = document.getElementById('initialLoader');
        if(loader) loader.style.display = 'none';
        return;
    }
    renderJobs();
    const loader = document.getElementById('initialLoader');
    if(loader) loader.style.display = 'none';
}

function renderJobs() {
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
        if(emptyState) {
            emptyState.style.display = 'block';
            emptyState.textContent = 'No recruitment notifications found.';
        }
        if(tabulatorTable) tabulatorTable.clearData();
        return;
    }
    if(emptyState) emptyState.style.display = 'none';
    
    if (!tabulatorTable) {
        tabulatorTable = new Tabulator("#jobsTable", {
            data: filtered,
            layout: "fitDataFill",
            height: "100%",
            clipboard: true, // Enable Excel shortcuts (Ctrl+C)
            selectable: true,
            movableColumns: true,
            resizableColumnFit: true,
            rowAlternatingColors: true,
            rowContextMenu: [
                { label: "★ Toggle Favorite", action: (e, row) => window.toggleFav(row.getData().id) },
                { label: "👁 Hide Job", action: (e, row) => window.quickAction(row.getData().id, 'hide') },
                { label: "📦 Archive Job", action: (e, row) => window.quickAction(row.getData().id, 'archive') },
                { label: "🗑 Move to Trash", action: (e, row) => window.quickAction(row.getData().id, 'trash') },
            ],
            columns: [
                { formatter: "rowSelection", titleFormatter: "rowSelection", hozAlign: "center", headerSort: false, frozen: true, width: 40 },
                { title: "Fav", field: "fav", formatter: (c) => c.getValue() > 0 ? '<span style="color:#fbbf24; font-size:16px;">★</span>' : '<span style="color:gray; font-size:16px;">☆</span>', hozAlign: "center", width: 60, cellClick: (e, cell) => window.toggleFav(cell.getRow().getData().id) },
                { title: "Organization", field: "org", frozen: true, headerFilter: "input", width: 150 },
                { title: "Post Name", field: "post", headerFilter: "input", width: 250, formatter: "textarea" },
                { title: "Status", field: "status", width: 140, headerFilter: "select", headerFilterParams: {values:true}, formatter: (cell) => {
                    const stat = calculateStatus(cell.getRow().getData().deadline);
                    return `<span class="badge ${stat.class}">${stat.text}</span>`;
                }},
                { title: "Deadline", field: "deadline", width: 120, formatter: (c) => c.getValue() ? new Date(c.getValue()).toLocaleDateString() : 'N/A' },
                { title: "Salary (₹)", field: "salary", width: 120, formatter: "money", formatterParams: { symbol: "₹", precision: 0 } },
                { title: "Vacancies", field: "vacancies", width: 100 },
                { title: "Age Limit", field: "age_limit", width: 100 },
                { title: "Experience", field: "experience_years", width: 120, formatter: (c) => c.getValue() ? c.getValue() + ' yrs' : 'N/A' },
                { title: "Qualification", field: "qualification", width: 200, formatter: "textarea" },
                { title: "Applied", field: "applied", formatter: "tickCross", hozAlign: "center", width: 90, cellClick: (e, cell) => window.toggleApply(cell.getRow().getData().id) },
                { title: "Notes", field: "description", editor: "input", width: 200, cellEdited: async function(cell) {
                    try {
                        const id = cell.getRow().getData().id;
                        const note = cell.getValue();
                        await fetch(`${API_BASE}/jobs/${id}/note`, { method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({note: note}) });
                    } catch(e) { console.error("Failed to save note"); }
                }},
                { title: "Actions", formatter: (cell) => {
                    const id = cell.getRow().getData().id;
                    const url = cell.getRow().getData().url;
                    return `
                        <button title="Open Website/PDF" onclick="window.open('${url}')" style="background:transparent; border:none; cursor:pointer; font-size:16px; margin-right:5px">🔗</button>
                        <button title="Hide" onclick="window.quickAction(${id}, 'hide')" style="background:transparent; border:none; cursor:pointer; font-size:16px; margin-right:5px">👁</button>
                        <button title="Archive" onclick="window.quickAction(${id}, 'archive')" style="background:transparent; border:none; cursor:pointer; font-size:16px; margin-right:5px">📦</button>
                        <button title="Trash" onclick="window.quickAction(${id}, 'trash')" style="background:transparent; border:none; cursor:pointer; font-size:16px; color:#f87171">🗑</button>
                    `;
                }, width: 160, headerSort: false }
            ],
            rowSelectionChanged: function(data, rows) {
                const checked = data.length;
                if(bulkActionsBar) bulkActionsBar.style.display = checked > 0 ? 'flex' : 'none';
                const countEl = document.getElementById('selectedCount');
                if(countEl) countEl.textContent = `${checked} Selected`;
            }
        });
    } else {
        tabulatorTable.replaceData(filtered);
    }
}

// Charting
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';

function renderChart(canvasId, type, dataObj, palette) {
    if (chartInstances[canvasId]) chartInstances[canvasId].destroy();
    const ctx = document.getElementById(canvasId).getContext('2d');
    chartInstances[canvasId] = new Chart(ctx, {
        type: type,
        data: { labels: dataObj.labels, datasets: [{ data: dataObj.values, backgroundColor: palette, borderWidth: 1, borderColor: 'rgba(255,255,255,0.05)' }] },
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
            if(analyticsEmptyState) analyticsEmptyState.style.display = 'block';
            return;
        }
        document.querySelector('.analytics-grid').style.display = 'grid';
        if(analyticsEmptyState) analyticsEmptyState.style.display = 'none';
        
        const c1 = ['#3b82f6', 'rgba(255,255,255,0.1)'];
        const cMulti = ['#3b82f6', '#f59e0b', '#10b981', '#8b5cf6', '#ec4899', '#06b6d4', '#f43f5e'];
        
        renderChart('chartApplied', 'doughnut', data.applied_vs_pending, c1);
        renderChart('chartOrg', 'bar', data.jobs_by_org, '#3b82f6');
        renderChart('chartMinistry', 'pie', data.jobs_by_ministry, cMulti);
        renderChart('chartQual', 'bar', data.jobs_by_qualification, '#10b981');
        renderChart('chartSalary', 'bar', data.jobs_by_salary, '#f59e0b');
        renderChart('chartAge', 'line', data.jobs_by_age, '#8b5cf6');
        renderChart('chartExp', 'bar', data.jobs_by_experience, '#06b6d4');
        renderChart('chartDeadline', 'line', data.upcoming_deadlines, '#ec4899');
    } catch(e) {}
}

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
        renderJobs();
    } catch(e) {}
};
window.toggleFav = (id) => { const job = allJobs.find(j => j.id === id); job.fav = job.fav === 2 ? 0 : job.fav + 1; renderJobs(); };
window.quickAction = (id, action) => { const job = allJobs.find(j => j.id === id); if (action === 'trash') job.trash = 1; if (action === 'hide') job.hidden = 1; if (action === 'archive') job.archive = 1; renderJobs(); };
window.bulkAction = (action) => { 
    if(!tabulatorTable) return;
    const selected = tabulatorTable.getSelectedData();
    selected.forEach(job => {
        window.quickAction(job.id, action);
    });
    tabulatorTable.deselectRow();
};
if(searchInput) searchInput.addEventListener('input', renderJobs);

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
    if(domainDisplay) domainDisplay.textContent = localStorage.getItem('govtrack_domain_name');
    fetchJobs(); 
    if(document.getElementById('analyticsView').classList.contains('active')) fetchAnalytics();
    if(document.getElementById('calendarView').style.display === 'flex') {
        fetchCalendarFilters();
        fetchCalendarEvents();
    }
};

window.exportData = function() {
    window.location.href = `${API_BASE}/excel/export?domain=${currentDomain || ''}`;
};

window.backupData = async function() {
    try {
        await fetch(`${API_BASE}/excel/backup?domain=${currentDomain || ''}`, { method: 'POST' });
        alert("Backup generated successfully!");
    } catch(e) { alert("Backup failed."); }
};

window.uploadExcel = async function(input) {
    if (!input.files || input.files.length === 0) return;
    const formData = new FormData();
    formData.append('file', input.files[0]);
    
    try {
        const res = await fetch(`${API_BASE}/excel/import`, { method: 'POST', body: formData });
        const data = await res.json();
        alert(`Successfully synchronized ${data.updated_count} updates from Excel to SQLite.`);
        fetchJobs();
    } catch(e) {
        console.error(e);
        alert("Failed to import Excel.");
    }
    input.value = '';
};

if (!currentDomain) {
    currentDomain = 'cyber_tech';
    localStorage.setItem('govtrack_domain', currentDomain);
    localStorage.setItem('govtrack_domain_name', 'Cyber Security');
}
if(domainDisplay) domainDisplay.textContent = localStorage.getItem('govtrack_domain_name');

document.querySelectorAll('.view-container').forEach(v => { if(!v.classList.contains('active')) v.style.display = 'none'; });
fetchJobs();
'''

with open(app_js_path, "w") as f:
    f.write(app_js_code)

print("app.js rewritten for Tabulator")

# Wait! We need to add the backend route for patching Notes!
# We're writing to `description` instead of a separate `notes` column.
api_jobs_patch = '''
@router.patch("/{job_id}/note")
def update_job_note(job_id: int, note_data: dict, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.description = note_data.get('note', '')
    db.commit()
    return {"status": "success"}
'''

api_jobs_path = os.path.join(project_root, "api", "routers", "jobs.py")
with open(api_jobs_path, "a") as f:
    f.write(api_jobs_patch)

print("Jobs router patched for notes.")
