async function runDiagnostics() {
    document.getElementById('runDiagBtn').disabled = true;
    document.getElementById('runDiagBtn').textContent = "Running...";
    document.getElementById('diagLoading').style.display = 'block';
    document.getElementById('diagResults').style.display = 'none';
    
    try {
        const res = await fetch(`${API_BASE}/diagnostics/run`, { method: 'POST' });
        const data = await res.json();
        const diags = data.diagnostics;
        
        // Render KPIs
        const total = diags.length;
        const success = diags.filter(d => d.success && d.parsed > 0).length;
        const zeroActive = diags.filter(d => d.success && d.parsed === 0 && !d.errors.length).length;
        const failed = diags.filter(d => !d.success || d.errors.length > 0).length;
        
        document.getElementById('diagKpis').innerHTML = `
            <div class="kpi-card" style="padding:15px; background:rgba(255,255,255,0.02); border:1px solid var(--border-color); border-radius:8px; text-align:center;">
                <div style="font-size:12px; color:var(--text-muted); margin-bottom:5px;">Orgs Scanned</div>
                <div style="font-size:24px; font-weight:bold; color:#3b82f6;">${total}</div>
            </div>
            <div class="kpi-card" style="padding:15px; background:rgba(255,255,255,0.02); border:1px solid var(--border-color); border-radius:8px; text-align:center;">
                <div style="font-size:12px; color:var(--text-muted); margin-bottom:5px;">Recruiting</div>
                <div style="font-size:24px; font-weight:bold; color:#10b981;">${success}</div>
            </div>
            <div class="kpi-card" style="padding:15px; background:rgba(255,255,255,0.02); border:1px solid var(--border-color); border-radius:8px; text-align:center;">
                <div style="font-size:12px; color:var(--text-muted); margin-bottom:5px;">No Active</div>
                <div style="font-size:24px; font-weight:bold; color:#f59e0b;">${zeroActive}</div>
            </div>
            <div class="kpi-card" style="padding:15px; background:rgba(255,255,255,0.02); border:1px solid var(--border-color); border-radius:8px; text-align:center;">
                <div style="font-size:12px; color:var(--text-muted); margin-bottom:5px;">Failed</div>
                <div style="font-size:24px; font-weight:bold; color:#ef4444;">${failed}</div>
            </div>
        `;
        
        // Render Table
        const tbody = document.getElementById('diagTableBody');
        tbody.innerHTML = '';
        
        diags.forEach(d => {
            const tr = document.createElement('tr');
            
            let statusHtml = '';
            if (!d.success) statusHtml = `<span class="badge" style="background:#ef4444;">Failed</span>`;
            else if (d.parsed === 0) statusHtml = `<span class="badge" style="background:#f59e0b;">Zero Rec</span>`;
            else statusHtml = `<span class="badge" style="background:#10b981;">Success</span>`;
            
            let reasonStr = d.errors.join(", ");
            if (!reasonStr && d.zero_reason) reasonStr = d.zero_reason;
            
            const ignoredDetails = Object.entries(d.ignored_reasons).map(([k,v]) => `${k}:${v}`).join('; ');
            
            tr.innerHTML = `
                <td>
                    <div style="font-weight:bold;">${d.organization}</div>
                    <div style="font-size:11px; color:var(--text-muted); max-width:200px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"><a href="${d.url}" target="_blank" style="color:var(--text-muted);">${d.url}</a></div>
                </td>
                <td>${statusHtml} <br><span style="font-size:11px;">HTTP ${d.status_code || 'N/A'}</span></td>
                <td>${d.links_found}</td>
                <td><strong style="color:#10b981;">${d.parsed}</strong><br><span style="font-size:10px;">(+${d.added} ↻${d.updated})</span></td>
                <td title="${ignoredDetails}">${d.ignored}</td>
                <td style="color:${d.errors.length ? '#ef4444' : 'var(--text-muted)'}; font-size:12px; max-width:250px;">${reasonStr || '-'}</td>
                <td>${d.execution_time_sec}s</td>
            `;
            tbody.appendChild(tr);
        });
        
        document.getElementById('diagResults').style.display = 'block';
    } catch (e) {
        alert("Failed to run diagnostics: " + e);
    } finally {
        document.getElementById('diagLoading').style.display = 'none';
        document.getElementById('runDiagBtn').disabled = false;
        document.getElementById('runDiagBtn').textContent = "Run Diagnostics";
    }
}
