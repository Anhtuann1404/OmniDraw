@echo off
cd /d "%~dp0"
echo ===================================================
echo [OmniDraw] Dang khoi dong Backend FastAPI Server...
echo API se chay tai: http://localhost:8000/
echo Swagger Docs: http://localhost:8000/docs
echo ===================================================
call .venv\Scripts\uvicorn.exe backend.main:app --reload --port 8000
pause
