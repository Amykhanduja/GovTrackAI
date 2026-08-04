const API_BASE = '/api/v1';
let currentDomain = localStorage.getItem('govtrack_domain') || null;

function showDomainSelection() {
    const overlay = document.createElement('div');
    overlay.className = 'domain-modal-overlay';
    overlay.innerHTML = `
        <div class="domain-modal">
            <h2>Choose Career Domain</h2>
            <button class="domain-btn" onclick="selectDomain('cyber_tech')">Cyber Security & Technology</button>
            <button class="domain-btn" onclick="selectDomain('foreign_lang')">Foreign Languages</button>
        </div>
    `;
    document.body.appendChild(overlay);
}

function selectDomain(domainId) {
    localStorage.setItem('govtrack_domain', domainId);
    currentDomain = domainId;
    document.querySelector('.domain-modal-overlay').remove();
    // Refresh all views
    fetchAnalytics();
    fetchJobs();
}

async function fetchAnalytics() {
    if (!currentDomain) return;
    try {
        const response = await fetch(`${API_BASE}/analytics/?domain=${currentDomain}`);
        const data = await response.json();
        const grid = document.getElementById('kpiGrid');
        if (grid) {
            grid.innerHTML = `
                <div class="kpi-card"><h3>Total Active Jobs</h3><div class="value">${data.total_jobs}</div></div>
                <div class="kpi-card"><h3>Applications Pending</h3><div class="value highlighted">${data.active_applications}</div></div>
            `;
        }
    } catch (e) { console.error("API Error", e); }
}

async function fetchJobs(search = '') {
    if (!currentDomain) return;
    try {
        const response = await fetch(`${API_BASE}/jobs/?domain=${currentDomain}&search=${search}`);
        const data = await response.json();
        const tbody = document.getElementById('jobsTableBody');
        if (tbody) {
            tbody.innerHTML = '';
            data.forEach(job => {
                tbody.innerHTML += `
                    <tr>
                        <td><strong>${job.org}</strong></td>
                        <td>${job.post}</td>
                        <td>₹${(job.salary||0).toLocaleString()}</td>
                        <td>${job.priority}/100</td>
                        <td><span class="badge new">${job.status}</span></td>
                    </tr>
                `;
            });
        }
    } catch (e) { console.error("API Error", e); }
}

// Init
if (!currentDomain) {
    showDomainSelection();
} else {
    fetchAnalytics();
    fetchJobs();
}
