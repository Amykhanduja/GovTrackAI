import os

project_root = "/mnt/c/Users/khand/GovTrackAI"

files = {
    "frontend/style.css": """@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
    --bg-color: #0f172a;
    --sidebar-bg: rgba(30, 41, 59, 0.7);
    --card-bg: rgba(30, 41, 59, 0.5);
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --border-color: rgba(255, 255, 255, 0.1);
    --primary: #3b82f6; 
    --primary-hover: #2563eb;
    --accent: #8b5cf6;
    --row-hover: rgba(255, 255, 255, 0.05);
    
    --status-active: rgba(16, 185, 129, 0.2);
    --status-active-text: #34d399;
    --status-closing: rgba(245, 158, 11, 0.2);
    --status-closing-text: #fbbf24;
    --status-closed: rgba(239, 68, 68, 0.2);
    --status-closed-text: #f87171;
    --status-upcoming: rgba(59, 130, 246, 0.2);
    --status-upcoming-text: #60a5fa;
    
    --glass-blur: blur(12px);
}

* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }
body { 
    background: var(--bg-color); 
    background-image: 
        radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.15) 0px, transparent 50%);
    color: var(--text-main); 
    font-size: 14px; 
    overflow: hidden; 
    height: 100vh;
}

/* Glassmorphism Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }

/* Layout */
.workspace-container { display: flex; height: 100vh; width: 100vw; backdrop-filter: var(--glass-blur); }

/* Sidebar */
.sidebar { 
    width: 260px; 
    background: var(--sidebar-bg); 
    border-right: 1px solid var(--border-color); 
    display: flex; 
    flex-direction: column; 
    backdrop-filter: var(--glass-blur);
    box-shadow: 4px 0 24px rgba(0,0,0,0.2);
    z-index: 20;
}
.brand { 
    font-size: 24px; 
    font-weight: 700; 
    padding: 24px; 
    background: linear-gradient(135deg, #60a5fa, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    border-bottom: 1px solid var(--border-color); 
    letter-spacing: -0.5px;
}
.domain-indicator { padding: 12px 24px; font-size: 11px; color: var(--accent); font-weight: 700; text-transform: uppercase; letter-spacing: 1px;}
nav { flex: 1; padding: 12px 0; }
.nav-btn { 
    width: calc(100% - 24px); 
    margin: 4px 12px;
    text-align: left; 
    padding: 12px 16px; 
    background: transparent; 
    border: 1px solid transparent; 
    cursor: pointer; 
    color: var(--text-muted); 
    font-size: 14px; 
    border-radius: 8px;
    transition: all 0.2s ease;
}
.nav-btn:hover { background: rgba(255, 255, 255, 0.05); color: var(--text-main); transform: translateX(4px); }
.nav-btn.active { 
    background: linear-gradient(90deg, rgba(59, 130, 246, 0.2), transparent); 
    border-left: 3px solid var(--primary);
    color: var(--text-main); 
    font-weight: 600; 
}
.sidebar-bottom { padding: 24px; border-top: 1px solid var(--border-color); display: flex; flex-direction: column; gap: 12px;}
.action-btn { 
    width: 100%; 
    padding: 12px; 
    background: var(--primary); 
    color: white;
    border: none; 
    cursor: pointer; 
    border-radius: 8px; 
    font-weight: 600;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
.action-btn:hover { background: var(--primary-hover); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4); }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none;}
#switchDomainBtn { background: transparent; border: 1px solid var(--border-color); color: var(--text-main); box-shadow: none; }
#switchDomainBtn:hover { background: rgba(255, 255, 255, 0.05); }

/* Main Content */
.main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
.toolbar { 
    display: flex; 
    justify-content: space-between; 
    padding: 20px 30px; 
    border-bottom: 1px solid var(--border-color); 
    background: rgba(15, 23, 42, 0.4); 
    backdrop-filter: var(--glass-blur);
    z-index: 10;
}
.search-bar input { 
    width: 350px; 
    padding: 10px 16px; 
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid var(--border-color); 
    border-radius: 8px; 
    color: var(--text-main);
    font-size: 14px; 
    transition: all 0.2s;
}
.search-bar input:focus { outline: none; border-color: var(--primary); background: rgba(0, 0, 0, 0.4); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2); }
.tool-select, .tool-btn { 
    padding: 10px 16px; 
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-main);
    border: 1px solid var(--border-color); 
    border-radius: 8px; 
    font-size: 14px; 
    cursor: pointer;
    transition: all 0.2s;
}
.tool-select option { background: var(--bg-color); }
.tool-btn:hover, .tool-select:hover { background: rgba(255, 255, 255, 0.1); }
.toolbar-actions { display: flex; gap: 12px; }

/* Table View */
.view-container { flex: 1; display: none; overflow: auto; padding: 30px; }
.view-container.active { display: flex; flex-direction: column; animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.table-wrapper { 
    flex: 1; 
    overflow: auto; 
    background: var(--card-bg); 
    border: 1px solid var(--border-color); 
    border-radius: 12px; 
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

.data-grid { width: 100%; border-collapse: collapse; table-layout: fixed; }
.data-grid th, .data-grid td { padding: 14px 20px; border-bottom: 1px solid var(--border-color); text-overflow: ellipsis; overflow: hidden; white-space: nowrap; }
.data-grid th { background: rgba(0, 0, 0, 0.2); position: sticky; top: 0; z-index: 10; text-align: left; font-weight: 600; color: var(--text-muted); text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px;}
.data-grid tr { transition: all 0.2s; }
.data-grid tr:hover { background: var(--row-hover); }
.data-grid tr.is-new { background: rgba(59, 130, 246, 0.05); }

.badge { padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge.active { background: var(--status-active); color: var(--status-active-text); border: 1px solid rgba(52, 211, 153, 0.3); }
.badge.closing { background: var(--status-closing); color: var(--status-closing-text); border: 1px solid rgba(251, 191, 36, 0.3); }
.badge.closed { background: var(--status-closed); color: var(--status-closed-text); border: 1px solid rgba(248, 113, 113, 0.3); }
.badge.upcoming { background: var(--status-upcoming); color: var(--status-upcoming-text); border: 1px solid rgba(96, 165, 250, 0.3); }

.quick-actions button { background: none; border: none; cursor: pointer; margin-right: 8px; font-size: 16px; opacity: 0.5; transition: all 0.2s; filter: grayscale(100%); }
.quick-actions button:hover { opacity: 1; transform: scale(1.2); filter: none; }

.fav-star { cursor: pointer; color: rgba(255,255,255,0.2); font-size: 18px; transition: all 0.2s;}
.fav-star.active { color: #fbbf24; text-shadow: 0 0 10px rgba(251, 191, 36, 0.5); }
.fav-star:hover { transform: scale(1.2); }

.empty-state { text-align: center; padding: 100px 50px; color: var(--text-muted); font-size: 16px; width: 100%; display: flex; flex-direction: column; align-items: center; gap: 15px; }

/* Checkboxes */
input[type="checkbox"] {
    appearance: none;
    width: 18px; height: 18px;
    border: 2px solid var(--text-muted);
    border-radius: 4px;
    background: transparent;
    cursor: pointer;
    position: relative;
    transition: all 0.2s;
}
input[type="checkbox"]:checked { background: var(--primary); border-color: var(--primary); }
input[type="checkbox"]:checked::after {
    content: '✓';
    position: absolute;
    color: white;
    font-size: 12px;
    font-weight: bold;
    top: -1px; left: 2px;
}

/* Bulk Actions */
.bulk-actions { padding: 12px 30px; background: rgba(59, 130, 246, 0.1); border-bottom: 1px solid var(--border-color); display: flex; gap: 15px; align-items: center; backdrop-filter: var(--glass-blur);}
.bulk-actions span { font-weight: 600; color: var(--primary); }
.bulk-actions button { padding: 6px 14px; border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.3); color: white; cursor: pointer; border-radius: 6px; transition: all 0.2s; font-size: 13px;}
.bulk-actions button:hover { background: rgba(255,255,255,0.1); }
.bulk-actions button.danger { background: rgba(239, 68, 68, 0.2); color: #f87171; border-color: rgba(239, 68, 68, 0.3); }
.bulk-actions button.danger:hover { background: rgba(239, 68, 68, 0.4); }

/* Analytics Grid */
.analytics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 24px; width: 100%; padding-bottom: 30px; }
.chart-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 24px; height: 320px; display: flex; flex-direction: column; box-shadow: 0 8px 32px rgba(0,0,0,0.15); backdrop-filter: var(--glass-blur); transition: transform 0.3s; }
.chart-card:hover { transform: translateY(-5px); border-color: rgba(255,255,255,0.2); }
.chart-card h3 { font-size: 16px; margin-bottom: 20px; color: var(--text-main); font-weight: 600; }
.chart-card canvas { flex: 1; max-height: 240px; }

/* Calendar */
.fc { background: var(--card-bg); padding: 20px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.15); border: 1px solid var(--border-color); }
.fc-theme-standard td, .fc-theme-standard th { border-color: var(--border-color) !important; }
.fc-daygrid-day-number { color: var(--text-main) !important; }
.fc-col-header-cell-cushion { color: var(--text-muted) !important; }
.fc .fc-button-primary { background: var(--primary) !important; border: none !important; }

/* Full Page Loader Overlay */
#initialLoader {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: var(--bg-color);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    color: white;
}
.spinner {
    width: 50px; height: 50px;
    border: 4px solid rgba(255,255,255,0.1);
    border-left-color: var(--primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 20px;
}
@keyframes spin { 100% { transform: rotate(360deg); } }
"""
}

for filepath, content in files.items():
    full_path = os.path.join(project_root, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)

print("Phase 27 UI Overhaul complete.")
