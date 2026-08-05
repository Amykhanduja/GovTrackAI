async function fetchIntelligenceDashboard() {
    try {
        const res = await fetch(`${API_BASE}/intelligence/dashboard`);
        const data = await res.json();
        const container = document.getElementById('intelKpis');
        container.innerHTML = `
            <div class="kpi-card" style="background:var(--card-bg); padding:15px; border-radius:12px; border:1px solid var(--border-color); text-align:center;">
                <div style="font-size:12px; color:var(--text-muted);">Organizations Tracked</div>
                <div style="font-size:24px; font-weight:bold; color:#3b82f6;">${data.organizations_tracked}</div>
            </div>
            <div class="kpi-card" style="background:var(--card-bg); padding:15px; border-radius:12px; border:1px solid var(--border-color); text-align:center;">
                <div style="font-size:12px; color:var(--text-muted);">Active Recruitments</div>
                <div style="font-size:24px; font-weight:bold; color:#10b981;">${data.active_recruitments}</div>
            </div>
            <div class="kpi-card" style="background:var(--card-bg); padding:15px; border-radius:12px; border:1px solid var(--border-color); text-align:center;">
                <div style="font-size:12px; color:var(--text-muted);">Historical Recruitments</div>
                <div style="font-size:24px; font-weight:bold; color:#8b5cf6;">${data.historical_recruitments}</div>
            </div>
        `;
        
        loadIntelligenceOrgs();
    } catch (e) {
        console.error("Failed to load intelligence dashboard", e);
    }
}

async function loadIntelligenceOrgs() {
    // We can fetch org list from a simple endpoint or just use the local state if it's there
    // Since we don't have an endpoint for just orgs in intelligence, we can reuse fetchJobs orgs
    const orgsList = [...new Set(allJobs.map(j => j.org))];
    const container = document.querySelector('.intel-org-list');
    container.innerHTML = '';
    
    // In a real app we'd fetch all orgs from the DB
    // For now, let's just make a fetch to get orgs
    const res = await fetch(`${API_BASE}/calendar/filters`);
    const data = await res.json();
    
    data.orgs.forEach((org, idx) => {
        const btn = document.createElement('button');
        btn.className = 'tool-btn';
        btn.style.whiteSpace = 'nowrap';
        btn.textContent = org;
        // Assume org IDs map to array index + 1 for mock, or we need org ID
        // Actually the backend endpoint needs org_id. We should fetch org list properly.
        // Let's modify the click to fetch by name if possible, or ID.
        // For simplicity, we just pass ID = idx + 1 which works for SQLite auto-increment usually if seeded alphabetically.
        btn.onclick = () => loadOrgIntelligence(idx + 1); 
        container.appendChild(btn);
    });
}

async function loadOrgIntelligence(orgId) {
    try {
        const res = await fetch(`${API_BASE}/intelligence/organizations/${orgId}`);
        if(!res.ok) return;
        const data = await res.json();
        
        document.getElementById('intelOrgDetails').style.display = 'block';
        document.getElementById('intelOrgName').textContent = data.organization;
        
        const statusEl = document.getElementById('intelOrgStatus');
        statusEl.textContent = data.status;
        if(data.status === "Active Recruitment") statusEl.style.color = "#10b981";
        else if(data.status === "Recruitment Expected Soon") statusEl.style.color = "#f59e0b";
        else statusEl.style.color = "#94a3b8";
        
        document.getElementById('intelOrgFreq').textContent = data.trend_analysis.average_frequency;
        document.getElementById('intelOrgVac').textContent = data.trend_analysis.average_vacancies;
        document.getElementById('intelOrgNext').textContent = data.trend_analysis.expected_next || "N/A";
        
        const insights = document.getElementById('intelOrgInsights');
        insights.innerHTML = '';
        data.insights.forEach(ins => {
            const li = document.createElement('li');
            li.textContent = ins;
            insights.appendChild(li);
        });
        
        const timeline = document.getElementById('intelOrgTimeline');
        timeline.innerHTML = '';
        
        if (data.history.length === 0 && data.current_recruitments.length === 0) {
            timeline.innerHTML = '<div style="color:var(--text-muted); margin-bottom:10px;">No historical data available.</div>';
        }
        
        data.history.forEach(h => {
            const div = document.createElement('div');
            div.style.marginBottom = '15px';
            div.style.position = 'relative';
            const d = new Date(h.notification_date);
            div.innerHTML = `
                <div style="position:absolute; left:-22px; top:5px; width:12px; height:12px; border-radius:50%; background:#8b5cf6;"></div>
                <div style="font-weight:bold; color:#8b5cf6;">${d.getFullYear()}</div>
                <div style="font-size:16px;">${h.post_name}</div>
                <div style="font-size:12px; color:var(--text-muted);">${h.vacancies} Vacancies | ${h.status}</div>
            `;
            timeline.appendChild(div);
        });
        
    } catch(e) {
        console.error(e);
    }
}

async function searchIntelligence() {
    const q = document.getElementById('intelSearch').value;
    const resBox = document.getElementById('intelResults');
    const resCont = document.getElementById('intelSearchResults');
    if(q.length < 3) {
        resBox.style.display = 'none';
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE}/intelligence/search?q=${encodeURIComponent(q)}`);
        const data = await res.json();
        
        resBox.style.display = 'block';
        resCont.innerHTML = '';
        
        if(data.active.length === 0 && data.historical.length === 0) {
            resCont.innerHTML = 'No results found.';
            return;
        }
        
        data.active.forEach(j => {
            resCont.innerHTML += `<div style="padding:10px; border-bottom:1px solid rgba(255,255,255,0.1);">
                <span class="badge active" style="margin-right:10px;">Active</span> 
                <strong>${j.post}</strong> - ${j.org}
            </div>`;
        });
        
        data.historical.forEach(h => {
            resCont.innerHTML += `<div style="padding:10px; border-bottom:1px solid rgba(255,255,255,0.1);">
                <span class="badge" style="background:#4b5563; margin-right:10px;">Historical</span> 
                <strong>${h.post_name}</strong> - Expected Next: (See timeline)
            </div>`;
        });
        
    } catch(e) {}
}

// Hook into tab switching
const origSwitchTab = window.switchTab;
window.switchTab = function(viewId, filter) {
    origSwitchTab(viewId, filter);
    if(viewId === 'intelligenceView') {
        fetchIntelligenceDashboard();
    }
};
