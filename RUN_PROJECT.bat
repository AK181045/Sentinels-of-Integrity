@echo off
setlocal enabledelayedexpansion
title Sentinels of Integrity — Launching...
color 0A

echo.
echo  ================================================================
echo    SENTINELS OF INTEGRITY  ^|  Full Project Launcher
echo  ================================================================
echo.

REM ── Locate the project root (same folder as this .bat) ──────────────────────
set "ROOT=%~dp0"
set "API_DIR=%ROOT%api"
set "LOG=%ROOT%api_server.log"
set "INDEX=%ROOT%index.html"

REM ════════════════════════════════════════════════════════════════════════════
REM  STEP 1 — Check / Install Python dependencies silently
REM ════════════════════════════════════════════════════════════════════════════
echo  [1/3] Checking dependencies...
python --version >nul 2>&1
if %errorlevel% NEQ 0 (
    echo  [ERROR] Python is not installed or not on PATH!
    echo          Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

uvicorn --version >nul 2>&1
if %errorlevel% NEQ 0 (
    echo  [INFO] Installing required packages (first run only)...
    pip install fastapi "uvicorn[standard]" pydantic-settings >nul 2>&1
    echo  [OK]  Packages installed.
) else (
    echo  [OK]  Dependencies already satisfied.
)

REM ════════════════════════════════════════════════════════════════════════════
REM  STEP 2 — Start API if not already running
REM ════════════════════════════════════════════════════════════════════════════
echo.
echo  [2/3] Starting API Server...

netstat -ano | findstr ":8000" >nul 2>&1
if %errorlevel% == 0 (
    echo  [OK]  API already running on port 8000 — skipping start.
    goto OPEN_BROWSER
)

REM Launch uvicorn hidden in background, append logs
start "" /MIN cmd /c "cd /d "%API_DIR%" && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload >> "%LOG%" 2>&1"

echo  [INFO] API process launched. Waiting for it to go ONLINE...

REM Poll health endpoint — up to 20 seconds (10 × 2s)
set /a tries=0
:WAIT_LOOP
timeout /t 2 /nobreak >nul
curl -s --max-time 2 -o nul -w "%%{http_code}" http://127.0.0.1:8000/api/v1/health 2>nul | findstr "200" >nul
if %errorlevel% == 0 (
    echo  [OK]  API is ONLINE ^|  http://127.0.0.1:8000
    goto OPEN_BROWSER
)
set /a tries+=1
if !tries! LSS 10 (
    echo  [INFO] Still starting... (!tries!/10)
    goto WAIT_LOOP
)
echo  [WARN] API is taking longer than expected. Opening browser anyway...
echo         Check log: %LOG%

REM ════════════════════════════════════════════════════════════════════════════
REM  STEP 3 — Open the project in the default browser
REM ════════════════════════════════════════════════════════════════════════════
:OPEN_BROWSER
echo.
echo  [3/3] Opening project in browser...
start "" "%INDEX%"
echo  [OK]  Browser launched ^|  %INDEX%

echo.
echo  ================================================================
echo    Project is LIVE!
echo    API  ^|  http://127.0.0.1:8000
echo    Docs ^|  http://127.0.0.1:8000/docs
echo    Log  ^|  %LOG%
echo.
echo    DO NOT close this window — it keeps the API alive.
echo    Press Ctrl+C to stop everything.
echo  ================================================================
echo.

REM ════════════════════════════════════════════════════════════════════════════
REM  WATCHDOG — keep the API alive as long as this window is open
REM ════════════════════════════════════════════════════════════════════════════
:WATCHDOG
timeout /t 15 /nobreak >nul

curl -s --max-time 3 -o nul -w "%%{http_code}" http://127.0.0.1:8000/api/v1/health 2>nul | findstr "200" >nul
if %errorlevel% == 0 (
    goto WATCHDOG
)

echo  [!] [%TIME%] API went OFFLINE — auto-restarting...

REM Kill leftover port holder
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul

REM Relaunch
start "" /MIN cmd /c "cd /d "%API_DIR%" && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload >> "%LOG%" 2>&1"

REM Wait for recovery
set /a tries=0
:RECOVER_WAIT
timeout /t 3 /nobreak >nul
curl -s --max-time 2 -o nul -w "%%{http_code}" http://127.0.0.1:8000/api/v1/health 2>nul | findstr "200" >nul
if %errorlevel% == 0 (
    echo  [OK] [%TIME%] API recovered — back ONLINE!
    goto WATCHDOG
)
set /a tries+=1
if !tries! LSS 7 goto RECOVER_WAIT

echo  [ERROR] Failed to restart API. Check: %LOG%
timeout /t 30 /nobreak >nul
goto WATCHDOG
