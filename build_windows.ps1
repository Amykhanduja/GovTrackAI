# PowerShell Build Script for GovTrack AI (Tauri + FastAPI)
Write-Host "======================================"
Write-Host "  GovTrack AI - Production Compiler   "
Write-Host "======================================"

# 1. Setup Python Environment & PyInstaller
Write-Host "[1/4] Freezing FastAPI Backend..."
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pyinstaller

# Compile the sidecar. We use --onedir or --onefile. 
# --onefile is cleaner for Tauri sidecars.
pyinstaller --onefile desktop_entry.py --name govtrack-api-x86_64-pc-windows-msvc

# Move the compiled sidecar into the Tauri bin directory
New-Item -ItemType Directory -Force -Path "src-tauri\bin"
Move-Item -Path "dist\govtrack-api-x86_64-pc-windows-msvc.exe" -Destination "src-tauri\bin\govtrack-api-x86_64-pc-windows-msvc.exe" -Force
Write-Host "[OK] Backend Sidecar Compiled."

# 2. Setup Frontend
Write-Host "[2/4] Building Frontend..."
npm install
npm run build
Write-Host "[OK] Frontend Compiled."

# 3. Build Tauri Desktop App
Write-Host "[3/4] Compiling Rust Tauri Wrapper (This may take a few minutes)..."
npm run tauri build

Write-Host "======================================"
Write-Host " Compilation Complete!"
Write-Host " Your installer is located at:"
Write-Host " src-tauri\target\release\bundle\msi\"
Write-Host "======================================"
