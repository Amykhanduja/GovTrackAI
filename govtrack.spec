# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 1. Hidden Imports
# Include any dynamic imports that PyInstaller might miss.
hiddenimports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'starlette',
    'sqlalchemy',
    'sqlalchemy.ext.baked',
    'openpyxl',
    'jinja2',
    'pydantic',
    'dateparser',
    'pdfplumber',
    'fitz',  # PyMuPDF
    'bs4',   # BeautifulSoup
    'lxml',
    'requests',
    'httpx',
    'schedule',
    'apscheduler',
    'sqlite3',
    'passlib',
    'passlib.handlers.bcrypt',
    'jose',
    'python-multipart'
]

# 2. Data Files
# Format: ('source_path', 'destination_folder_in_bundle')
datas = [
    ('frontend', 'frontend'),
    ('config', 'config'),
    ('excel', 'excel'),
    ('scrapers', 'scrapers'),
    ('db', 'db'),
    ('api', 'api'),
    ('parsers', 'parsers'),
    ('scheduler', 'scheduler'),
    ('notifications', 'notifications'),
    ('logger', 'logger'),
    ('utils', 'utils'),
    ('security', 'security'),
    ('storage', 'storage'),
    ('career', 'career'),
    ('core', 'core'),
    ('downloads', 'downloads'),
    ('exceptions', 'exceptions'),
    ('icons', 'icons'),
    ('assets', 'assets'),
    ('templates', 'templates'),
    ('static', 'static')
]

# Note: We omit 'data', '__pycache__', 'logs', 'venv', 'src-tauri' because they are dynamic or irrelevant.

a = Analysis(
    ['desktop_entry.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='govtrack-api-x86_64-pc-windows-msvc',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, # Set to False to hide the console window when run independently, but Tauri sidecar hides it anyway.
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
