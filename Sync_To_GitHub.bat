@echo off
echo ===================================================
echo     Sentinels of Integrity - GitHub Auto-Sync Script
echo ===================================================
echo.
cd /d "c:\Users\SAI\Desktop\Sentinals of integrity"

set GIT_CMD="C:\Program Files\Git\cmd\git.exe"

echo Checking for changes to back up...
%GIT_CMD% status --porcelain > nul
if errorlevel 1 (
    echo Git repository not found!
    pause
    exit
)

echo Adding all modified files...
%GIT_CMD% add .
echo.

echo Committing changes...
set datetime=%date% %time%
%GIT_CMD% commit -m "Auto-backup on %datetime%"
echo.

echo Uploading to GitHub...
%GIT_CMD% push origin main
echo.
echo ===================================================
echo    SUCCESS! All changes are now safely on GitHub!
echo ===================================================
pause
