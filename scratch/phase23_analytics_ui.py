import os

project_root = "/mnt/c/Users/khand/GovTrackAI"

files = {
    "frontend/index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GovTrack AI - Recruitment Workspace</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="domain_modal.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
        </main>
    </div>
    
    <script src="desktop_bridge.js"></script>
    <script src="app.js"></script>
</body>
</html>
""",

    "frontend/style.css": """
:root {
    --bg-color: #ffffff;
    --text-main: #333333;
    --border-color: #e0e0e0;
    --sidebar-bg: #f5f5f5;
    --primary: #0078d4; 
    --row-hover: #f3f2f1;
    --status-active: #107c10;
    --status-closing: #d83b01;
    --status-closed: #a80000;
    --status-upcoming: #0078d4;
    --row-new: #e6f2fa;
}

* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
body { background: var(--bg-color); color: var(--text-main); font-size: 13px; overflow: hidden; }

.workspace-container { display: flex; height: 100vh; width: 100vw; }
.sidebar { width: 220px; background: var(--sidebar-bg); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; }
.brand { font-size: 16px; font-weight: bold; padding: 15px; border-bottom: 1px solid var(--border-color); }
.domain-indicator { padding: 10px 15px; font-size: 11px; color: #666; font-weight: 600; text-transform: uppercase; }
nav { flex: 1; padding: 10px 0; }
.nav-btn { width: 100%; text-align: left; padding: 10px 15px; background: none; border: none; cursor: pointer; color: var(--text-main); font-size: 13px; }
.nav-btn:hover, .nav-btn.active { background: #e5e5e5; font-weight: 600; }
.sidebar-bottom { padding: 15px; border-top: 1px solid var(--border-color); }
.action-btn { width: 100%; padding: 8px; margin-bottom: 5px; background: #fff; border: 1px solid var(--border-color); cursor: pointer; border-radius: 4px; font-weight: bold;}
.action-btn:hover { background: #e5e5e5; }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
.toolbar { display: flex; justify-content: space-between; padding: 10px 15px; border-bottom: 1px solid var(--border-color); background: #faf9f8; }
.search-bar input { width: 300px; padding: 6px 10px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 13px; }
.tool-select, .tool-btn { padding: 6px 10px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 13px; background: #fff; cursor: pointer;}
.tool-btn:hover, .tool-select:hover { background: #e5e5e5; }

.bulk-actions { padding: 10px 15px; background: #e1dfdd; border-bottom: 1px solid var(--border-color); display: flex; gap: 10px; align-items: center; }
.bulk-actions button { padding: 5px 10px; border: 1px solid var(--border-color); background: #fff; cursor: pointer; border-radius: 4px; }
.bulk-actions button:hover { background: #f3f2f1; }
.bulk-actions button.danger { color: #a80000; }

.view-container { flex: 1; display: none; overflow: auto; padding: 10px; }
.view-container.active { display: flex; flex-direction: column; }
.table-wrapper { flex: 1; overflow: auto; position: relative; }

.data-grid { width: 100%; border-collapse: collapse; table-layout: fixed; }
.data-grid th, .data-grid td { padding: 6px 10px; border: 1px solid var(--border-color); text-overflow: ellipsis; overflow: hidden; white-space: nowrap; }
.data-grid th { background: #f3f2f1; position: sticky; top: 0; z-index: 10; text-align: left; font-weight: 600; }
.data-grid tr:hover { background: var(--row-hover); }
.data-grid tr.is-new { background: var(--row-new); font-weight: 600; }
.data-grid tr.is-new td { border-left: 2px solid var(--primary); }

.badge { padding: 3px 6px; border-radius: 10px; font-size: 11px; font-weight: bold; color: #fff; }
.badge.active { background: var(--status-active); }
.badge.closing { background: var(--status-closing); }
.badge.closed { background: var(--status-closed); }
.badge.upcoming { background: var(--status-upcoming); }

.quick-actions button { background: none; border: none; cursor: pointer; margin-right: 5px; font-size: 14px; opacity: 0.6; }
.quick-actions button:hover { opacity: 1; transform: scale(1.1); }

.fav-star { cursor: pointer; color: #ccc; font-size: 16px; }
.fav-star.active { color: #ffb900; }

.empty-state { text-align: center; padding: 50px; color: #666; font-style: italic; width: 100%; }

/* Stats Modal */
.stats-modal { position: absolute; top: 50px; right: 20px; background: #fff; border: 1px solid var(--border-color); box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 100; border-radius: 6px; width: 300px; }
.stats-content { padding: 15px; }
.stats-content h3 { margin-bottom: 15px; font-size: 14px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
.stat-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 12px; }

/* Analytics Grid */
.analytics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; width: 100%; padding-bottom: 30px; }
.chart-card { background: #fff; border: 1px solid var(--border-color); border-radius: 6px; padding: 15px; height: 250px; display: flex; flex-direction: column; }
.chart-card h3 { font-size: 13px; margin-bottom: 10px; color: #555; text-align: center; }
.chart-card canvas { flex: 1; max-height: 200px; }
""",

    "frontend/app.js": """const API_BASE = '/api/v1';
let currentDomain = localStorage.getItem('govtrack_domain') || null;
let currentFilter = 'active'; 
let allJobs = [];
let chartInstances = {};

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
    
    document.querySelectorAll('.view-container').forEach(v => v.classList.remove('active'));
    document.getElementById(viewId).classList.add('active');
    
    if (viewId === 'tableView') {
        currentFilter = filter;
        renderJobs();
    } else if (viewId === 'analyticsView') {
        fetchAnalytics();
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

// Chart Render Helper
function renderChart(canvasId, type, dataObj, palette) {
    if (chartInstances[canvasId]) chartInstances[canvasId].destroy();
    
    const ctx = document.getElementById(canvasId).getContext('2d');
    chartInstances[canvasId] = new Chart(ctx, {
        type: type,
        data: {
            labels: dataObj.labels,
            datasets: [{
                data: dataObj.values,
                backgroundColor: palette,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: type === 'doughnut' || type === 'pie' } }
        }
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
        
    } catch(e) {
        console.error("Failed to load analytics", e);
    }
}

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
};
window.exportData = async function() {
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

print("Phase 23 Analytics UI Complete.")
