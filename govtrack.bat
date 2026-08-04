@echo off
echo ======================================
echo     GovTrack AI - Setup ^& CLI
echo ======================================

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate
echo Installing dependencies...
pip install -r requirements.txt -q

echo Launching GovTrack CLI...
python govtrack_cli.py %*
