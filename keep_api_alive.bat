@echo off
title Sentinels Watchdog - API Keep-Alive (DO NOT CLOSE)
color 0A

echo.
echo  ============================================================
echo    Sentinels of Integrity - API WATCHDOG (Keep-Alive)
echo    This window keeps the API running 24/7. DO NOT CLOSE IT.
echo  ============================================================
echo.
echo  Press Ctrl+C to stop the watchdog and kill the API.
echo.

:WATCHDOG_LOOP
REM ─── Check if API responds to health check ───────────────────────────────────
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8000/api/v1/health 2>nul | findstr "200" >nul
if %errorlevel% == 0 (
    echo  [%TIME%] [OK] API is ONLINE at http://127.0.0.1:8000
    timeout /t 15 /nobreak >nul
    goto WATCHDOG_LOOP
)

REM ─── API is down — attempt to (re)start ──────────────────────────────────────
echo  [%TIME%] [WARN] API is OFFLINE! Attempting restart...

REM Kill any leftover process on port 8000 first
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)

REM Small gap to let the port release
timeout /t 2 /nobreak >nul

REM Launch uvicorn fresh
start "" /MIN cmd /c "cd /d "%~dp0api" && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload >> "%~dp0api_server.log" 2>&1"

echo  [%TIME%] [INFO] Restarted API process. Waiting for it to come online...

REM Wait up to 20s for the server to respond
set /a tries=0
:RESTART_WAIT
timeout /t 3 /nobreak >nul
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8000/api/v1/health 2>nul | findstr "200" >nul
if %errorlevel% == 0 (
    echo  [%TIME%] [OK] API restarted SUCCESSFULLY — back ONLINE!
    goto WATCHDOG_LOOP
)
set /a tries+=1
if %tries% LSS 7 (
    echo  [%TIME%] [INFO] Still starting... (%tries%/7)
    goto RESTART_WAIT
)

echo  [%TIME%] [ERROR] Could not restart API after 7 attempts.
echo             Check api_server.log for errors:
echo             %~dp0api_server.log
echo.
echo  Retrying full cycle in 30 seconds...
timeout /t 30 /nobreak >nul
goto WATCHDOG_LOOP
