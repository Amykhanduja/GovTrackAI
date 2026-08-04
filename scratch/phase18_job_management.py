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
            <!-- Toolbar -->
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
                    <button class="tool-btn" onclick="exportData()">Export</button>
                </div>
            </header>

            <!-- Bulk Actions Bar -->
            <div class="bulk-actions" id="bulkActions" style="display: none;">
                <span id="selectedCount">0 Selected</span>
                <button onclick="bulkAction('favorite')">★ Favorite</button>
                <button onclick="bulkAction('archive')">📦 Archive</button>
                <button onclick="bulkAction('hide')">👁 Hide</button>
                <button onclick="bulkAction('trash')" class="danger">🗑 Trash</button>
            </div>

            <!-- Data Grid View -->
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
                                <th>Quick Actions</th>
                            </tr>
                        </thead>
                        <tbody id="jobsTableBody">
                            <!-- Populated dynamically -->
                        </tbody>
                    </table>
                    <div id="emptyState" class="empty-state" style="display: none;">
                        No active recruitment notifications are currently available.
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
.action-btn { width: 100%; padding: 8px; margin-bottom: 5px; background: #fff; border: 1px solid var(--border-color); cursor: pointer; border-radius: 4px; }
.action-btn:hover { background: #e5e5e5; }

.main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
.toolbar { display: flex; justify-content: space-between; padding: 10px 15px; border-bottom: 1px solid var(--border-color); background: #faf9f8; }
.search-bar input { width: 300px; padding: 6px 10px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 13px; }
.tool-select, .tool-btn { padding: 6px 10px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 13px; background: #fff; cursor: pointer;}
.tool-btn:hover, .tool-select:hover { background: #e5e5e5; }

.bulk-actions { padding: 10px 15px; background: #e1dfdd; border-bottom: 1px solid var(--border-color); display: flex; gap: 10px; align-items: center; }
.bulk-actions button { padding: 5px 10px; border: 1px solid var(--border-color); background: #fff; cursor: pointer; border-radius: 4px; }
.bulk-actions button:hover { background: #f3f2f1; }
.bulk-actions button.danger { color: #a80000; }

.view-container { flex: 1; display: none; overflow: auto; }
.view-container.active { display: flex; flex-direction: row; }
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

.empty-state { text-align: center; padding: 50px; color: #666; font-style: italic; }
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

// Mock Data structure for testing the rich UI
const mockDbJobs = [
    { id: 1, org: 'NIC', post: 'Scientist B', salary: 120000, deadline: new Date(Date.now() + 86400000*2).toISOString(), added_at: new Date().toISOString(), fav: 1, hidden: 0, trash: 0, archive: 0, url: '#' },
    { id: 2, org: 'ISRO', post: 'Technical Assistant', salary: 65000, deadline: new Date(Date.now() - 86400000).toISOString(), added_at: new Date(Date.now() - 86400000*10).toISOString(), fav: 0, hidden: 0, trash: 0, archive: 0, url: '#' },
    { id: 3, org: 'CERT-In', post: 'Cyber Security Analyst', salary: 90000, deadline: new Date(Date.now() + 86400000*15).toISOString(), added_at: new Date().toISOString(), fav: 2, hidden: 0, trash: 0, archive: 0, url: '#' }
];

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
    // In production, this hits fetch(`${API_BASE}/jobs/`);
    // Using mock data to demonstrate the complex UI logic immediately
    allJobs = [...mockDbJobs];
    renderJobs();
}

function renderJobs() {
    jobsTableBody.innerHTML = '';
    const search = searchInput.value.toLowerCase();
    
    let filtered = allJobs.filter(job => {
        // Search
        if (search && !job.org.toLowerCase().includes(search) && !job.post.toLowerCase().includes(search)) return false;
        
        // Navigation Filters
        if (currentFilter === 'trash') return job.trash === 1;
        if (currentFilter === 'hidden') return job.hidden === 1 && job.trash === 0;
        if (currentFilter === 'archived') return job.archive === 1 && job.trash === 0;
        if (currentFilter === 'favorites') return job.fav > 0 && job.trash === 0;
        if (currentFilter === 'recent') return isNew(job.added_at) && job.trash === 0;
        
        // Default 'active' ignores trash, hidden, archived, and closed
        if (currentFilter === 'active') {
            if (job.trash || job.hidden || job.archive) return false;
            if (calculateStatus(job.deadline).text === 'Closed') return false; // Auto-hide closed
        }
        return true;
    });
    
    // Default Sorting: Nearest Deadline, then Priority
    filtered.sort((a, b) => new Date(a.deadline) - new Date(b.deadline));

    if (filtered.length === 0) {
        emptyState.style.display = 'block';
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
            <td>₹${job.salary.toLocaleString()}</td>
            <td>${new Date(job.deadline).toLocaleDateString()}</td>
            <td><span class="badge ${stat.class}">${stat.text}</span></td>
            <td class="quick-actions">
                <button title="Apply/View" onclick="window.open('${job.url}')">🔗</button>
                <button title="Hide" onclick="quickAction(${job.id}, 'hide')">👁</button>
                <button title="Archive" onclick="quickAction(${job.id}, 'archive')">📦</button>
                <button title="Move to Trash" onclick="quickAction(${job.id}, 'trash')">🗑</button>
            </td>
        `;
        jobsTableBody.appendChild(tr);
    });
}

window.toggleFav = (id) => {
    const job = allJobs.find(j => j.id === id);
    job.fav = job.fav === 2 ? 0 : job.fav + 1; // Cycle 0 -> 1 -> 2 -> 0
    renderJobs();
};

window.quickAction = (id, action) => {
    const job = allJobs.find(j => j.id === id);
    if (action === 'trash') job.trash = 1;
    if (action === 'hide') job.hidden = 1;
    if (action === 'archive') job.archive = 1;
    renderJobs();
};

window.updateBulkBar = () => {
    const checked = document.querySelectorAll('.row-cb:checked').length;
    bulkActionsBar.style.display = checked > 0 ? 'flex' : 'none';
    document.getElementById('selectedCount').textContent = `${checked} Selected`;
};

selectAllCb.onclick = (e) => {
    document.querySelectorAll('.row-cb').forEach(cb => cb.checked = e.target.checked);
    updateBulkBar();
};

window.bulkAction = (action) => {
    document.querySelectorAll('.row-cb:checked').forEach(cb => {
        quickAction(parseInt(cb.value), action);
        cb.checked = false;
    });
    selectAllCb.checked = false;
    updateBulkBar();
};

searchInput.addEventListener('input', renderJobs);

// Init
if (!currentDomain) {
    document.body.innerHTML = '<h2>Domain not selected. Please run Phase 17 first.</h2>';
} else {
    domainDisplay.textContent = localStorage.getItem('govtrack_domain_name') || currentDomain;
    fetchJobs();
}
"""
}

# Apply files
for filepath, content in files.items():
    full_path = os.path.join(project_root, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)

print("Phase 18 Active Recruitment Management UI Complete.")
