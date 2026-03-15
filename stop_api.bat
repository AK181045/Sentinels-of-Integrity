@echo off
title Sentinels - Stop API Server
echo.
echo  ==========================================
echo   Sentinels of Integrity - Stop API Server
echo  ==========================================
echo.

REM Find and kill the process running on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
    echo  [INFO] Found process on port 8000 (PID: %%a) - Stopping...
    taskkill /PID %%a /F >nul 2>&1
)

echo  [OK] API Server stopped. Port 8000 is now free.
echo.
timeout /t 3
exit /b 0
