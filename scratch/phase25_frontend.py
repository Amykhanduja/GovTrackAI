import os

project_root = "/mnt/c/Users/khand/GovTrackAI"
html_path = os.path.join(project_root, "frontend", "index.html")

with open(html_path, "r") as f:
    html = f.read()

modal_html = """
    <div id="pdfViewerModal" style="display:none; position:fixed; z-index:9999; left:0; top:0; width:100%; height:100%; background-color:rgba(0,0,0,0.8);">
        <div style="display:flex; width:95%; height:95%; margin: 2.5vh auto; background:var(--bg-dark); border-radius:12px; overflow:hidden; border: 1px solid rgba(255,255,255,0.1);">
            <div style="flex:1; padding:20px; border-right:1px solid rgba(255,255,255,0.1); overflow-y:auto; background: var(--bg-dark);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 id="pvTitle" style="color:#fff; margin-top:0;">Analysis</h2>
                    <button onclick="document.getElementById('pdfViewerModal').style.display='none'" style="background:#ef4444; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer;">Close</button>
                </div>
                
                <div id="pvEligibleBadge" style="padding:10px; border-radius:5px; font-weight:bold; margin-top:10px; margin-bottom:10px;"></div>
                <div id="pvEligibleReason" style="font-size:13px; color:var(--text-muted); margin-bottom:20px;"></div>
                
                <h3 style="color:#60a5fa; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:5px;">AI Summary</h3>
                <div id="pvSummary" style="font-size:14px; line-height:1.6; margin-bottom:20px; white-space:pre-wrap;"></div>
                
                <h3 style="color:#60a5fa; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:5px;">Structured Extract</h3>
                <pre id="pvStruct" style="background:rgba(0,0,0,0.3); padding:10px; border-radius:5px; font-size:12px; overflow-x:auto;"></pre>
                
                <h3 style="color:#60a5fa; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:5px;">Tables Found</h3>
                <div id="pvTables" style="font-size:12px;"></div>
            </div>
            
            <div style="flex:2; background:#1a1a1a;">
                <iframe id="pvIframe" src="" style="width:100%; height:100%; border:none;"></iframe>
            </div>
        </div>
    </div>
"""

html = html.replace("</body>", modal_html + "\\n</body>")
with open(html_path, "w") as f:
    f.write(html)

app_js_path = os.path.join(project_root, "frontend", "app.js")
with open(app_js_path, "r") as f:
    app_js = f.read()

old_btn = "<button title=\\"Open Website/PDF\\" onclick=\\"window.open('${url}')\\" style=\\"background:transparent; border:none; cursor:pointer; font-size:16px; margin-right:5px\\">🔗</button>"
new_btn = "<button title=\\"Intelligent View\\" onclick=\\"window.openIntelligentViewer(${id}, '${url}')\\" style=\\"background:transparent; border:none; cursor:pointer; font-size:16px; margin-right:5px\\">🧠</button>"
app_js = app_js.replace(old_btn, new_btn)

viewer_js = """
window.openIntelligentViewer = async function(id, fallbackUrl) {
    document.getElementById('pvTitle').textContent = 'Loading AI Analysis...';
    document.getElementById('pvSummary').textContent = 'Extracting data...';
    document.getElementById('pvStruct').textContent = '';
    document.getElementById('pvTables').innerHTML = '';
    document.getElementById('pvEligibleBadge').textContent = '';
    document.getElementById('pvEligibleReason').textContent = '';
    document.getElementById('pvIframe').src = 'about:blank';
    
    document.getElementById('pdfViewerModal').style.display = 'block';
    
    try {
        const res = await fetch(`${API_BASE}/jobs/${id}/document`);
        const data = await res.json();
        
        if (data.status === 'found') {
            document.getElementById('pvTitle').textContent = 'Intelligent Document Analysis';
            document.getElementById('pvSummary').textContent = data.ai_summary;
            
            if(data.eligibility_status === 'Eligible') {
                document.getElementById('pvEligibleBadge').style.background = 'rgba(16, 185, 129, 0.2)';
                document.getElementById('pvEligibleBadge').style.color = '#10b981';
            } else if(data.eligibility_status === 'Not Eligible') {
                document.getElementById('pvEligibleBadge').style.background = 'rgba(239, 68, 68, 0.2)';
                document.getElementById('pvEligibleBadge').style.color = '#ef4444';
            } else {
                document.getElementById('pvEligibleBadge').style.background = 'rgba(245, 158, 11, 0.2)';
                document.getElementById('pvEligibleBadge').style.color = '#f59e0b';
            }
            
            document.getElementById('pvEligibleBadge').textContent = `Status: ${data.eligibility_status}`;
            document.getElementById('pvEligibleReason').textContent = data.eligibility_reason;
            
            document.getElementById('pvStruct').textContent = JSON.stringify(data.parsed_fields, null, 2);
            document.getElementById('pvTables').innerHTML = `Found ${data.extracted_tables.length} structured tables dynamically extracted from the PDF.`;
            
            document.getElementById('pvIframe').src = `${API_BASE}/jobs/${id}/pdf`;
        } else {
            document.getElementById('pvTitle').textContent = 'No Local PDF Available';
            document.getElementById('pvSummary').textContent = 'This notification did not contain an official PDF on the first scan, or the PDF has not been completely parsed yet. Returning to standard website.';
            document.getElementById('pvIframe').src = fallbackUrl;
        }
    } catch(e) {
        console.error(e);
        document.getElementById('pvIframe').src = fallbackUrl;
    }
};
"""

app_js += "\\n" + viewer_js

with open(app_js_path, "w") as f:
    f.write(app_js)

print("Frontend UI patched successfully")
