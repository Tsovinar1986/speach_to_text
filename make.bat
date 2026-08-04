@echo off
setlocal
cd /d "%~dp0"

set VENV=venv
set PY=%VENV%\Scripts\python.exe
set PIP=%VENV%\Scripts\pip.exe
if "%HOST%"=="" set HOST=0.0.0.0
if "%PORT%"=="" set PORT=8008

set TARGET=%1
if "%TARGET%"=="" set TARGET=run

if "%TARGET%"=="install" goto install
if "%TARGET%"=="run" goto run
if "%TARGET%"=="dev" goto dev
if "%TARGET%"=="stop" goto stop
if "%TARGET%"=="clean" goto clean
echo Unknown target: %TARGET%
echo Usage: make.bat [install^|run^|dev^|stop^|clean]
exit /b 1

:install
if not exist "%PY%" (
    python -m venv %VENV%
    "%PIP%" install --upgrade pip
    "%PIP%" install -r requirements.txt
)
goto :eof

:run
call :install
"%PY%" -m uvicorn app.main:app --host %HOST% --port %PORT%
goto :eof

:dev
call :install
"%PY%" -m uvicorn app.main:app --host %HOST% --port %PORT% --reload
goto :eof

:stop
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do taskkill /F /PID %%p
goto :eof

:clean
rmdir /s /q %VENV% 2>nul
rmdir /s /q app\__pycache__ 2>nul
goto :eof
