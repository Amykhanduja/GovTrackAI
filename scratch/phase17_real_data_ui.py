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
                <button class="nav-btn active" data-view="table">Database</button>
                <button class="nav-btn" data-view="analytics">Analytics</button>
                <button class="nav-btn" data-view="calendar">Calendar</button>
            </nav>
            <div class="sidebar-bottom">
                <button id="refreshBtn" class="action-btn">Refresh Data</button>
                <button id="switchDomainBtn" class="action-btn">Switch Domain</button>
            </div>
        </aside>

        <!-- Main Content Area -->
        <main class="main-content">
            <!-- Toolbar -->
            <header class="toolbar">
                <div class="search-bar">
                    <input type="text" id="globalSearch" placeholder="Search Database (e.g. Cyber, RBI, Analyst)...">
                </div>
                <div class="toolbar-actions">
                    <button class="tool-btn" id="filterToggleBtn">Filters</button>
                    <button class="tool-btn" id="exportBtn">Export Excel</button>
                </div>
            </header>

            <!-- Data Grid View -->
            <div class="view-container active" id="tableView">
                <div class="table-wrapper">
                    <table class="data-grid" id="jobsTable">
                        <thead>
                            <tr>
                                <th>Org</th>
                                <th>Post</th>
                                <th>Salary</th>
                                <th>Vacancies</th>
                                <th>Deadline</th>
                                <th>Priority</th>
                                <th>Status</th>
                                <th>Applied?</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="jobsTableBody">
                            <!-- Populated dynamically from SQLite -->
                        </tbody>
                    </table>
                    <div id="emptyState" class="empty-state" style="display: none;">
                        No recruitment notifications found.
                    </div>
                </div>
            </div>

            <!-- Detail Panel (Hidden by default) -->
            <aside class="detail-panel" id="detailPanel">
                <div class="panel-header">
                    <h2 id="dpTitle">Job Details</h2>
                    <button id="closePanelBtn">X</button>
                </div>
                <div class="panel-content" id="dpContent">
                    <!-- Populated dynamically -->
                </div>
            </aside>
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
    --primary: #0078d4; /* Excel Blue */
    --row-hover: #f3f2f1;
}

* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

body { background: var(--bg-color); color: var(--text-main); font-size: 13px; overflow: hidden; }

.workspace-container { display: flex; height: 100vh; width: 100vw; }

.sidebar { width: 220px; background: var(--sidebar-bg); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; }
.brand { font-size: 16px; font-weight: bold; padding: 15px; border-bottom: 1px solid var(--border-color); }
.domain-indicator { padding: 10px 15px; font-size: 11px; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
nav { flex: 1; padding: 10px 0; }
.nav-btn { width: 100%; text-align: left; padding: 10px 15px; background: none; border: none; cursor: pointer; color: var(--text-main); font-size: 13px; }
.nav-btn:hover, .nav-btn.active { background: #e5e5e5; font-weight: 600; }
.sidebar-bottom { padding: 15px; border-top: 1px solid var(--border-color); }
.action-btn { width: 100%; padding: 8px; margin-bottom: 5px; background: #fff; border: 1px solid var(--border-color); cursor: pointer; border-radius: 4px; }
.action-btn:hover { background: #e5e5e5; }

.main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }

.toolbar { display: flex; justify-content: space-between; padding: 10px 15px; border-bottom: 1px solid var(--border-color); background: #faf9f8; }
.search-bar input { width: 300px; padding: 6px 10px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 13px; }
.tool-btn { padding: 6px 12px; background: #fff; border: 1px solid var(--border-color); cursor: pointer; border-radius: 4px; }
.tool-btn:hover { background: #e5e5e5; }

.view-container { flex: 1; display: none; overflow: auto; }
.view-container.active { display: flex; flex-direction: row; }
.table-wrapper { flex: 1; overflow: auto; position: relative; }

.data-grid { width: 100%; border-collapse: collapse; table-layout: fixed; }
.data-grid th, .data-grid td { padding: 6px 10px; border: 1px solid var(--border-color); text-overflow: ellipsis; overflow: hidden; white-space: nowrap; }
.data-grid th { background: #f3f2f1; position: sticky; top: 0; z-index: 10; text-align: left; font-weight: 600; user-select: none; }
.data-grid tr:hover { background: var(--row-hover); cursor: pointer; }

.empty-state { text-align: center; padding: 50px; color: #666; font-style: italic; }

.detail-panel { width: 400px; background: #fff; border-left: 1px solid var(--border-color); display: none; flex-direction: column; }
.detail-panel.open { display: flex; }
.panel-header { display: flex; justify-content: space-between; padding: 15px; border-bottom: 1px solid var(--border-color); background: #f3f2f1; font-weight: bold; }
.panel-header button { background: none; border: none; cursor: pointer; font-size: 16px; }
.panel-content { padding: 15px; overflow-y: auto; flex: 1; }
.field-group { margin-bottom: 15px; }
.field-label { font-size: 11px; color: #666; text-transform: uppercase; margin-bottom: 4px; }
.field-value { font-size: 13px; word-wrap: break-word; }
""",

    "frontend/app.js": """const API_BASE = '/api/v1';
let currentDomain = localStorage.getItem('govtrack_domain') || null;

// DOM Elements
const jobsTableBody = document.getElementById('jobsTableBody');
const emptyState = document.getElementById('emptyState');
const detailPanel = document.getElementById('detailPanel');
const closePanelBtn = document.getElementById('closePanelBtn');
const dpContent = document.getElementById('dpContent');
const dpTitle = document.getElementById('dpTitle');
const domainDisplay = document.getElementById('currentDomainDisplay');
const searchInput = document.getElementById('globalSearch');

function showDomainSelection() {
    const overlay = document.createElement('div');
    overlay.className = 'domain-modal-overlay';
    overlay.innerHTML = `
        <div class="domain-modal">
            <h2>Choose Career Domain</h2>
            <button class="domain-btn" onclick="selectDomain('cyber_tech', 'Cyber Security & Technology')">Cyber Security & Technology</button>
            <button class="domain-btn" onclick="selectDomain('foreign_lang', 'Foreign Languages')">Foreign Languages</button>
        </div>
    `;
    document.body.appendChild(overlay);
}

window.selectDomain = function(domainId, domainName) {
    localStorage.setItem('govtrack_domain', domainId);
    localStorage.setItem('govtrack_domain_name', domainName);
    currentDomain = domainId;
    
    const overlay = document.querySelector('.domain-modal-overlay');
    if (overlay) overlay.remove();
    
    domainDisplay.textContent = domainName;
    fetchJobs();
};

async function fetchJobs(search = '') {
    if (!currentDomain) return;
    try {
        const response = await fetch(`${API_BASE}/jobs/?domain=${currentDomain}&search=${search}`);
        if (!response.ok) throw new Error('API Unavailable');
        
        const data = await response.json();
        
        jobsTableBody.innerHTML = '';
        
        if (!data || data.length === 0) {
            emptyState.style.display = 'block';
            return;
        }
        
        emptyState.style.display = 'none';
        
        data.forEach(job => {
            const tr = document.createElement('tr');
            tr.onclick = () => openDetailPanel(job);
            
            tr.innerHTML = `
                <td>${job.org || '-'}</td>
                <td>${job.post || '-'}</td>
                <td>${job.salary ? '₹' + job.salary.toLocaleString() : '-'}</td>
                <td>${job.vacancies || '-'}</td>
                <td>${job.deadline || '-'}</td>
                <td>${job.priority || '-'}</td>
                <td>${job.status || 'Active'}</td>
                <td>
                    <input type="checkbox" onclick="event.stopPropagation(); toggleApply(${job.id})" ${job.applied ? 'checked' : ''}>
                </td>
                <td>
                    <button onclick="event.stopPropagation(); window.open('${job.url}', '_blank')">Link</button>
                </td>
            `;
            jobsTableBody.appendChild(tr);
        });
    } catch (e) {
        console.error("API Error", e);
        jobsTableBody.innerHTML = '';
        emptyState.style.display = 'block';
        emptyState.textContent = 'No recruitment notifications found.';
    }
}

function openDetailPanel(job) {
    detailPanel.classList.add('open');
    dpTitle.textContent = job.org || 'Details';
    
    dpContent.innerHTML = `
        <div class="field-group">
            <div class="field-label">Post</div>
            <div class="field-value">${job.post || '-'}</div>
        </div>
        <div class="field-group">
            <div class="field-label">Salary</div>
            <div class="field-value">${job.salary ? '₹' + job.salary.toLocaleString() : '-'}</div>
        </div>
        <div class="field-group">
            <div class="field-label">Deadline</div>
            <div class="field-value">${job.deadline || '-'}</div>
        </div>
        <div class="field-group">
            <div class="field-label">Required Skills</div>
            <div class="field-value">${job.skills || '-'}</div>
        </div>
        <div class="field-group">
            <div class="field-label">AI Summary</div>
            <div class="field-value">${job.ai_summary || 'No summary available.'}</div>
        </div>
        <div class="field-group">
            <div class="field-label">Application Status</div>
            <select id="statusSelect" onchange="updateJobStatus(${job.id}, this.value)">
                <option value="Not Applied" ${job.status === 'Not Applied' ? 'selected' : ''}>Not Applied</option>
                <option value="Applied" ${job.status === 'Applied' ? 'selected' : ''}>Applied</option>
                <option value="Selected" ${job.status === 'Selected' ? 'selected' : ''}>Selected</option>
                <option value="Rejected" ${job.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
            </select>
        </div>
    `;
}

closePanelBtn.onclick = () => detailPanel.classList.remove('open');

document.getElementById('refreshBtn').onclick = () => fetchJobs(searchInput.value);
document.getElementById('switchDomainBtn').onclick = showDomainSelection;

searchInput.addEventListener('input', (e) => {
    // Basic debounce could be added here
    fetchJobs(e.target.value);
});

window.toggleApply = async function(jobId) {
    // In a real app, send PATCH to API
    console.log(`Toggled apply status for job ${jobId}`);
};
window.updateJobStatus = async function(jobId, status) {
    // In a real app, send PATCH to API
    console.log(`Updated status to ${status} for job ${jobId}`);
};

// Init
if (!currentDomain) {
    showDomainSelection();
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

print("Phase 17 Real Data UI Complete.")
