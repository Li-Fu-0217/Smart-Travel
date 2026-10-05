@echo off
rem Smart Travel Assistant - one-click backend launcher
rem Create .venv if missing -> install deps -> run uvicorn
cd /d %~dp0

if not exist .venv (
    echo [dev] creating venv ...
    python -m venv .venv
)

echo [dev] installing dependencies ...
.venv\Scripts\python.exe -m pip install -r requirements.txt
echo [dev] starting backend http://127.0.0.1:8000 ...
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
