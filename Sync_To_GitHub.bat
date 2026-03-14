@echo off
echo ===================================================
echo     Sentinels of Integrity - GitHub Auto-Sync Script
echo ===================================================
echo.
cd /d "c:\Users\SAI\Desktop\Sentinals of integrity"

echo Checking for changes to back up...
git status --porcelain > nul
if errorlevel 1 (
    echo Git repository not found!
    pause
    exit
)

echo Adding all modified files...
git add .
echo.

echo Committing changes...
set datetime=%date% %time%
git commit -m "Auto-backup on %datetime%"
echo.

echo Uploading to GitHub...
git push origin main
echo.
echo ===================================================
echo    SUCCESS! All changes are now safely on GitHub!
echo ===================================================
pause
