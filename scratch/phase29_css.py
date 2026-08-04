import os
import re

css_path = "/mnt/c/Users/khand/GovTrackAI/frontend/style.css"
with open(css_path, "r") as f:
    css = f.read()

# Add Archived and Applied Status Variables
if "--status-archived" not in css:
    vars_inject = """    --status-archived: rgba(156, 163, 175, 0.2);
    --status-archived-text: #9ca3af;
    --status-applied: rgba(167, 139, 250, 0.2);
    --status-applied-text: #a78bfa;
    --grid-bg: #1e1e1e;
    --grid-alt: #252526;
    --grid-header: #181818;
    --grid-hover: #2a2d2e;
    --grid-selected: #37373d;
    --grid-border: #2b2b2b;
"""
    css = css.replace("--glass-blur: blur(12px);", vars_inject + "    --glass-blur: blur(12px);")

# Badges update
if ".badge.archived" not in css:
    badges = """
.badge.archived { background: var(--status-archived); color: var(--status-archived-text); border: 1px solid rgba(156, 163, 175, 0.3); }
.badge.applied { background: var(--status-applied); color: var(--status-applied-text); border: 1px solid rgba(167, 139, 250, 0.3); }
"""
    css = css.replace(".badge.upcoming { background: var(--status-upcoming); color: var(--status-upcoming-text); border: 1px solid rgba(96, 165, 250, 0.3); }", 
                     ".badge.upcoming { background: var(--status-upcoming); color: var(--status-upcoming-text); border: 1px solid rgba(96, 165, 250, 0.3); }" + badges)

# Scrollbars update to thin dark
scrollbar_css = """/* Data Grid Scrollbar */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--grid-bg, #1e1e1e); }
::-webkit-scrollbar-thumb { background: #424242; border-radius: 6px; border: 2px solid var(--grid-bg, #1e1e1e); }
::-webkit-scrollbar-thumb:hover { background: #4f4f4f; }
::-webkit-scrollbar-corner { background: var(--grid-bg, #1e1e1e); }"""
css = re.sub(r"/\* Glassmorphism Scrollbar \*/.*?/\* Layout \*/", scrollbar_css + "\n\n/* Layout */", css, flags=re.DOTALL)

# Tabulator comprehensive overhaul
tabulator_new = """/* Tabulator Overrides for Dashboard Integration */
.table-wrapper { background: var(--grid-bg); border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); overflow: hidden; border: 1px solid var(--border-color); padding: 0; }
.tabulator { background: var(--grid-bg) !important; border: none !important; font-family: 'Outfit', sans-serif; }
.tabulator-header { background: var(--grid-header) !important; color: var(--text-main) !important; font-weight: 700 !important; letter-spacing: 0.5px; border-bottom: 1px solid var(--grid-border) !important; padding-top: 5px; padding-bottom: 5px; }
.tabulator .tabulator-header .tabulator-col { background: var(--grid-header) !important; border-right: 1px solid var(--grid-border) !important; }
.tabulator .tabulator-header .tabulator-col.tabulator-sortable:hover { background: #222222 !important; }
.tabulator-row { font-size: 13px !important; color: var(--text-main) !important; background: var(--grid-bg) !important; border-bottom: 1px solid var(--grid-border) !important; transition: background 0.15s ease !important; min-height: 48px; }
.tabulator-row.tabulator-row-even { background: var(--grid-alt) !important; }
.tabulator-row.tabulator-row-odd { background: var(--grid-bg) !important; }
.tabulator-row:hover, .tabulator-row.tabulator-row-even:hover, .tabulator-row.tabulator-row-odd:hover { background: var(--grid-hover) !important; cursor: pointer; }
.tabulator-row.tabulator-selected { background: var(--grid-selected) !important; }
.tabulator-row.tabulator-selected:hover { background: #3f3f46 !important; }
.tabulator-cell { border-right: 1px solid var(--grid-border) !important; padding: 12px 16px !important; display: flex; align-items: center; }
.tabulator-cell a { color: var(--primary); text-decoration: none; }
.tabulator-cell a:hover { text-decoration: underline; }
.tabulator-footer { background: var(--grid-header) !important; border-top: 1px solid var(--grid-border) !important; color: var(--text-muted) !important; padding: 10px !important; }
.tabulator-footer .tabulator-page { background: #2d2d2d !important; border: 1px solid #3d3d3d !important; color: var(--text-main) !important; border-radius: 6px; margin: 0 4px; transition: all 0.2s; }
.tabulator-footer .tabulator-page:hover { background: var(--primary) !important; border-color: var(--primary) !important; }
.tabulator-footer .tabulator-page.active { background: var(--primary) !important; border-color: var(--primary) !important; font-weight: bold; }
"""
css = re.sub(r"/\* Tabulator Overrides for Dashboard Integration \*/.*", tabulator_new, css, flags=re.DOTALL)

# Search bar Update
search_css = """
.search-bar { position: relative; }
.search-bar input { 
    width: 380px; 
    padding: 10px 16px 10px 40px; 
    background: #1e1e1e;
    border: 1px solid var(--border-color); 
    border-radius: 20px; 
    color: var(--text-main);
    font-size: 14px; 
    transition: all 0.2s;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'%3E%3C/circle%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'%3E%3C/line%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: 14px center;
}
.search-bar input:focus { outline: none; border-color: var(--primary); background-color: #252526; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2); }
.tool-select, .tool-btn { 
    padding: 10px 18px; 
    background: #1e1e1e;
    color: var(--text-main);
    border: 1px solid var(--border-color); 
    border-radius: 8px; 
    font-size: 14px; 
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 500;
}
.tool-btn { box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
.tool-btn:hover, .tool-select:hover { background: #2a2d2e; transform: translateY(-1px); }
"""
# Replace lines from `.search-bar input {` up to `.toolbar-actions { display: flex; gap: 12px; }`
css = re.sub(r"\.search-bar input \{.*?\.(tool-btn:hover, \.tool-select:hover) \{.*?\}", search_css.strip(), css, flags=re.DOTALL)

with open(css_path, "w") as f:
    f.write(css)
print("CSS Updated!")
