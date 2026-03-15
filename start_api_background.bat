@echo off
title Sentinels of Integrity - API Launcher
echo.
echo  ==========================================
echo   Sentinels of Integrity - API Server
echo  ==========================================
echo.

REM Check if server is already running on port 8000
netstat -ano | findstr ":8000" >nul 2>&1
if %errorlevel% == 0 (
    echo  [OK] API Server is already running on port 8000!
    echo  --> http://127.0.0.1:8000
    echo  --> http://127.0.0.1:8000/docs
    timeout /t 4
    exit /b 0
)

echo  [INFO] Starting API Server in background...
echo  [INFO] Port: 8000

REM Start uvicorn in a hidden background window
start "" /MIN cmd /c "cd /d "%~dp0api" && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload > "%~dp0api_server.log" 2>&1"

REM Wait a moment for server to boot
timeout /t 3 /nobreak >nul

echo.
echo  [OK] API Server started successfully!
echo  --> API:  http://127.0.0.1:8000
echo  --> Docs: http://127.0.0.1:8000/docs
echo  --> Logs: api_server.log (in project root)
echo.
echo  To STOP the server, run: stop_api.bat
echo.
timeout /t 5
exit /b 0
