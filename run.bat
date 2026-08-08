@echo off
setlocal
cd /d "%~dp0"

if not exist venv (
    python -m venv venv
    venv\Scripts\python.exe -m pip install -r requirements.txt
)

if "%HOST%"=="" set HOST=0.0.0.0
if "%PORT%"=="" set PORT=8008

venv\Scripts\python.exe -m uvicorn app.main:app --host %HOST% --port %PORT%
