@echo off
title Sentinels of Integrity - API Launcher
echo.
echo  ==========================================
echo   Sentinels of Integrity - API Server
echo  ==========================================
echo.

REM ── Check if server is already running on port 8000 ──────────────────────────
netstat -ano | findstr ":8000" >nul 2>&1
if %errorlevel% == 0 (
    echo  [OK] API Server is already running on port 8000!
    echo  --> http://127.0.0.1:8000
    echo  --> http://127.0.0.1:8000/docs
    timeout /t 3
    exit /b 0
)

REM ── Check uvicorn is installed ────────────────────────────────────────────────
uvicorn --version >nul 2>&1
if %errorlevel% NEQ 0 (
    echo  [ERROR] uvicorn not found! Installing dependencies...
    pip install fastapi uvicorn[standard] pydantic-settings >nul 2>&1
    echo  [INFO] Dependencies installed. Retrying launch...
)

echo  [INFO] Starting API Server on 0.0.0.0:8000 (background)...

REM ── Launch uvicorn in a minimised background window ──────────────────────────
start "" /MIN cmd /c "cd /d "%~dp0api" && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "%~dp0api_server.log" 2>&1"

REM ── Wait up to 15 s for the API to respond ───────────────────────────────────
set /a tries=0
:WAIT_LOOP
timeout /t 2 /nobreak >nul
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8000/api/v1/health 2>nul | findstr "200" >nul
if %errorlevel% == 0 goto READY
set /a tries+=1
if %tries% LSS 7 (
    echo  [INFO] Waiting for API to start... (attempt %tries%/7)
    goto WAIT_LOOP
)

echo.
echo  [WARN] API may still be starting up. Check api_server.log for details.
echo  --> Log: %~dp0api_server.log
goto DONE

:READY
echo.
echo  [OK] API Server is UP and responding!
echo  --> API:  http://127.0.0.1:8000
echo  --> Docs: http://127.0.0.1:8000/docs
echo  --> Logs: %~dp0api_server.log

:DONE
echo.
echo  To STOP the server, run: stop_api.bat
echo  To keep it alive 24/7,  run: keep_api_alive.bat
echo.
timeout /t 5
exit /b 0
