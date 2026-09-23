@echo off
set "PATH=%LOCALAPPDATA%\Programs\nodejs;%PATH%"
cd /d "%~dp0frontend"
echo ===================================================
echo [OmniDraw] Dang khoi dong Frontend Dev Server...
echo Giao dien se chay tai: http://localhost:5173/
echo ===================================================
call npm run dev
pause
