@echo off
title Sentinels - Stop API Server
echo.
echo  ==========================================
echo   Sentinels of Integrity - Stop API Server
echo  ==========================================
echo.

set found=0

REM ── Kill by port 8000 ────────────────────────────────────────────────────────
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" 2^>nul') do (
    if NOT "%%a"=="" (
        echo  [INFO] Found process on port 8000 (PID: %%a) — Stopping...
        taskkill /PID %%a /F >nul 2>&1
        set found=1
    )
)

REM ── Also kill any lingering uvicorn processes ─────────────────────────────────
tasklist | findstr /i "uvicorn" >nul 2>&1
if %errorlevel% == 0 (
    echo  [INFO] Killing leftover uvicorn processes...
    taskkill /IM python.exe /FI "WINDOWTITLE eq Sentinels*" /F >nul 2>&1
    set found=1
)

if "%found%"=="0" (
    echo  [INFO] No API process found running on port 8000.
) else (
    echo  [OK] API Server stopped. Port 8000 is now free.
)

echo.
timeout /t 3
exit /b 0
