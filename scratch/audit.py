import os
import ast
import re

ROOT_DIR = "/mnt/c/Users/khand/GovTrackAI"
EXCLUDE_DIRS = {"venv", "scratch", ".git", ".pytest_cache", "__pycache__", "node_modules", "src-tauri"}

KEYWORDS = [
    r'\bpass\b',
    r'\.\.\.',
    r'return\s+None',
    r'return\s+\{\}',
    r'raise\s+NotImplementedError',
    r'TODO',
    r'FIXME',
    r'placeholder',
    r'stub',
    r'dummy implementation'
]

def check_function_for_keywords(func_code):
    reasons = []
    for kw in KEYWORDS:
        flags = re.IGNORECASE if kw in [r'TODO', r'FIXME', r'placeholder', r'stub', r'dummy implementation'] else 0
        if re.search(kw, func_code, flags=flags):
            reasons.append(kw.replace(r'\b', '').replace(r'\s+', ' ').replace(r'\{', '{').replace(r'\}', '}').replace('\\', ''))
    return reasons

report_lines = [
    "# Project Audit: Placeholder & Stub Functions",
    "",
    "| File | Function | Line | Reason(s) |",
    "|------|----------|------|-----------|"
]

for root, dirs, files in os.walk(ROOT_DIR):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, ROOT_DIR)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    source_lines = f.readlines()
                    source_code = "".join(source_lines)
                
                try:
                    tree = ast.parse(source_code)
                except SyntaxError:
                    continue # Skip files with syntax errors
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        start = node.lineno - 1
                        end = node.end_lineno
                        func_code = "".join(source_lines[start:end])
                        
                        reasons = check_function_for_keywords(func_code)
                        if reasons:
                            report_lines.append(f"| `{rel_path}` | `{node.name}` | {node.lineno} | {', '.join(reasons)} |")
            except Exception as e:
                print(f"Error processing {rel_path}: {e}")

report_content = "\n".join(report_lines)
with open("/home/amykhanduja_7203/.gemini/antigravity-cli/brain/fe3cc9dd-aca7-4746-ae29-9404940bed46/Placeholder_Audit_Report.md", "w", encoding="utf-8") as f:
    f.write(report_content)

print("Audit complete.")
