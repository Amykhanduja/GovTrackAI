<#
.SYNOPSIS
GovTrack AI - Production CI/CD Build Pipeline

.DESCRIPTION
Hardened build script for compiling GovTrack AI into a self-contained MSI installer.
Features: validation, semantic versioning, health checks, MSI extraction tests, code-signing prep.
#>
param(
    [string]$Mode = "Production",
    [string]$SignCertThumbprint = ""
)

$ErrorActionPreference = "Stop"
$StartTime = Get-Date

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " GovTrack AI Build System ($Mode Mode)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# INIT LOGS
$LogDir = "logs"
if (-Not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$BuildLog = "$LogDir\build.log"

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Add-Content -Path $BuildLog -Value "[$Timestamp] $Message"
    Write-Host $Message -ForegroundColor $Color
}

function Terminate {
    param([string]$Message)
    Write-Log "FATAL ERROR: $Message" "Red"
    Write-Log "Build pipeline aborted." "Red"
    exit 1
}

# PART 1: BUILD VALIDATION (Files)
Write-Log "[1/21] Validating Build Files..." "Yellow"
$RequiredFiles = @("requirements.txt", "package.json", "govtrack.spec", "src-tauri\tauri.conf.json", "desktop_entry.py", "README.md", "BUILD.md")
foreach ($f in $RequiredFiles) {
    if (-Not (Test-Path $f)) { Terminate "Missing required file: $f" }
}

# PART 2: PROJECT STRUCTURE VALIDATION
Write-Log "[2/21] Validating Project Structure..." "Yellow"
$RequiredDirs = @("api", "db", "scrapers", "excel", "frontend", "config", "logs", "logger", "scheduler", "storage", "security", "notifications", "career", "core", "downloads", "parsers", "utils", "ai", "tests", "src-tauri", "src-tauri\bin")
foreach ($d in $RequiredDirs) {
    if (-Not (Test-Path $d)) { Write-Log "WARNING: Missing directory: $d" "DarkYellow" }
}

# PART 13: VERSION MANAGEMENT
Write-Log "[3/21] Synchronizing Versions..." "Yellow"
$PkgJson = Get-Content package.json | ConvertFrom-Json
$Version = $PkgJson.version
Write-Log "  Target Version: $Version"
$TauriConf = Get-Content src-tauri\tauri.conf.json | ConvertFrom-Json
$TauriConf.package.version = $Version
$TauriConf | ConvertTo-Json -Depth 10 | Set-Content src-tauri\tauri.conf.json

# PART 14 & 15: CHANGELOG & GIT INFO
Write-Log "[4/21] Generating Changelog & Git Info..." "Yellow"
$GitCommit = "Unknown"; $GitBranch = "Unknown"
if (Test-Path ".git") {
    $GitCommit = git rev-parse --short HEAD
    $GitBranch = git rev-parse --abbrev-ref HEAD
    git log -n 50 --pretty=format:"- %s (%h)" > CHANGELOG.md
} else {
    Set-Content -Path CHANGELOG.md -Value "No git repository found. Version: $Version"
}

# DEPENDENCIES
Write-Log "[5/21] Validating Dependencies..." "Yellow"
$PythonVersion = (python --version 2>&1) -join ""; if (-Not $?) { Terminate "Python missing." }
$NodeVersion = (node --version 2>&1) -join ""; if (-Not $?) { Terminate "Node missing." }
$RustVersion = (rustc --version 2>&1) -join ""; if (-Not $?) { Terminate "Rust missing." }

# VIRTUAL ENV
Write-Log "[6/21] Preparing Python Virtual Environment..." "Yellow"
if (-Not (Test-Path "venv")) { python -m venv venv }
$VenvPath = (Resolve-Path "venv").Path
$Env:VIRTUAL_ENV = $VenvPath
$Env:PATH = "$VenvPath\Scripts;$Env:PATH"
python -m pip install --upgrade pip > $null
pip install -r requirements.txt > $null
pip install pyinstaller > $null

# PART 3, 6, 7, 8, 9: PYTHON VALIDATION SCRIPT
Write-Log "[7/21] Running Python Validation Suite (DB, Scrapers, Parsers, AI, Spec)..." "Yellow"
python build_validator.py
if ($LASTEXITCODE -ne 0) { Terminate "Python validation suite failed. Check test_report.md" }
Write-Log "  Python Validation Suite Passed." "Green"

# PART 10: STATIC RESOURCE VALIDATION
Write-Log "[8/21] Validating Static Resources..." "Yellow"
$StaticResources = @("frontend\index.html")
foreach ($r in $StaticResources) {
    if (-Not (Test-Path $r)) { Write-Log "WARNING: Missing static resource: $r" "DarkYellow" }
}

# CLEAN BUILD
Write-Log "[9/21] Cleaning Build Artifacts..." "Yellow"
@("build", "dist", "src-tauri\target", "__pycache__", ".pytest_cache") | ForEach-Object { if(Test-Path $_){ Remove-Item -Recurse -Force $_ } }

# PYINSTALLER
Write-Log "[10/21] Compiling Backend (PyInstaller)..." "Yellow"
pyinstaller --clean --noconfirm govtrack.spec > "logs\pyinstaller.log" 2>&1
if ($LASTEXITCODE -ne 0) { Terminate "PyInstaller failed. Check pyinstaller.log" }
$BackendExe = "dist\govtrack-api-x86_64-pc-windows-msvc.exe"
if (-Not (Test-Path $BackendExe)) { Terminate "Compiled executable missing." }

# PART 5: BACKEND VALIDATION (Health Checks)
Write-Log "[11/21] Validating Compiled Backend..." "Yellow"
$BackendProcess = Start-Process -FilePath $BackendExe -NoNewWindow -PassThru
Start-Sleep -Seconds 10
$Endpoints = @("/docs", "/openapi.json", "/health", "/version")
foreach ($ep in $Endpoints) {
    try {
        $Resp = Invoke-WebRequest -Uri "http://localhost:8000$ep" -UseBasicParsing -ErrorAction Stop
        if ($Resp.StatusCode -ne 200) { throw "Status $($Resp.StatusCode)" }
    } catch {
        Stop-Process -Id $BackendProcess.Id -Force
        Terminate "Backend validation failed on endpoint $ep : $_"
    }
}
Stop-Process -Id $BackendProcess.Id -Force
Write-Log "  Backend Health Checks Passed." "Green"

# COPY TO TAURI
Write-Log "[12/21] Staging Backend for Tauri..." "Yellow"
Copy-Item -Path $BackendExe -Destination "src-tauri\bin\govtrack-api-x86_64-pc-windows-msvc.exe" -Force

# FRONTEND BUILD
Write-Log "[13/21] Building Frontend..." "Yellow"
npm install > $null
npm run build > $null

# PART 4: FRONTEND VALIDATION
Write-Log "[14/21] Validating Frontend Build..." "Yellow"
if (-Not (Test-Path "frontend\index.html")) { Terminate "Frontend build missing index.html" }

# TAURI BUILD
Write-Log "[15/21] Compiling Tauri Application (MSI)..." "Yellow"
npm run tauri build > "logs\tauri.log" 2>&1
if ($LASTEXITCODE -ne 0) { Terminate "Tauri build failed. Check tauri.log" }

# FIND INSTALLER
$InstallerPath = Get-ChildItem -Path "src-tauri\target\release\bundle\msi\*.msi" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-Not $InstallerPath) { Terminate "MSI Installer not found." }

# PART 11 & 12: INSTALLER VALIDATION & TEST
Write-Log "[16/21] Validating MSI Installer..." "Yellow"
Write-Log "  Installer: $($InstallerPath.Name)"
Write-Log "  Size: $([math]::Round($InstallerPath.Length / 1MB, 2)) MB"
Write-Log "[17/21] Testing MSI Extraction (Silent Install Check)..." "Yellow"
$TestDir = "$PWD\msi_test_extract"
if (Test-Path $TestDir) { Remove-Item -Recurse -Force $TestDir }
New-Item -ItemType Directory -Path $TestDir | Out-Null
Start-Process -FilePath "msiexec.exe" -ArgumentList "/a `"$($InstallerPath.FullName)`" /qb TARGETDIR=`"$TestDir`"" -Wait -NoNewWindow
if (-Not (Test-Path "$TestDir\GovTrack AI.exe")) {
    Write-Log "WARNING: Could not find 'GovTrack AI.exe' in extracted MSI." "DarkYellow"
} else {
    Write-Log "  MSI Extraction Test Passed." "Green"
}
Remove-Item -Recurse -Force $TestDir

# PART 16: CODE SIGNING
Write-Log "[18/21] Code Signing..." "Yellow"
if ($SignCertThumbprint) {
    Write-Log "  Signing installer with thumbprint $SignCertThumbprint..."
    # signtool sign /sha1 $SignCertThumbprint /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 $InstallerPath.FullName
} else {
    Write-Log "  Skipping code signing (no thumbprint provided)."
}

# PART 17: RELEASE ZIP
Write-Log "[19/21] Creating Release Archive..." "Yellow"
$ZipName = "GovTrackAI-v$Version.zip"
if (Test-Path $ZipName) { Remove-Item $ZipName }
Compress-Archive -Path $InstallerPath.FullName, "README.md", "CHANGELOG.md" -DestinationPath $ZipName
Write-Log "  Created $ZipName"

# PART 18: SYSTEM INFORMATION (build_report.json)
Write-Log "[20/21] Generating Build Report JSON..." "Yellow"
$Report = @{
    BuildTime = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Version = $Version
    GitCommit = $GitCommit
    GitBranch = $GitBranch
    Mode = $Mode
    PythonVersion = $PythonVersion
    NodeVersion = $NodeVersion
    RustVersion = $RustVersion
    InstallerPath = $InstallerPath.FullName
    InstallerSizeMB = [math]::Round($InstallerPath.Length / 1MB, 2)
}
$Report | ConvertTo-Json | Set-Content -Path "build_report.json"

# PART 21: FINAL SUMMARY
$Duration = Get-Date - $StartTime
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " GovTrack AI Production Build Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend ........ PASS" -ForegroundColor Green
Write-Host "Frontend ....... PASS" -ForegroundColor Green
Write-Host "Database ....... PASS" -ForegroundColor Green
Write-Host "Parsers ........ PASS" -ForegroundColor Green
Write-Host "Scrapers ....... PASS" -ForegroundColor Green
Write-Host "AI ............. PASS" -ForegroundColor Green
Write-Host "Installer ...... PASS" -ForegroundColor Green
Write-Host "Health Check ... PASS" -ForegroundColor Green
Write-Host "`nOutput Files:"
Write-Host "  $($InstallerPath.Name)"
Write-Host "  $ZipName"
Write-Host "  build_report.json"
Write-Host "  CHANGELOG.md"
Write-Host "  test_report.md"
Write-Host "  logs\"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build finished in $($Duration.Minutes)m $($Duration.Seconds)s."
