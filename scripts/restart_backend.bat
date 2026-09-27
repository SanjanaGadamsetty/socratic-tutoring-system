@echo off
echo Stopping old backend...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo Starting backend...
cd /d "C:\Users\Sanju\OneDrive\Desktop\Apps n Extensions\HOPE-Elite\HDP 1-Agentic AI\AgenticAI-Project\socratic-tutoring-system"
call venv\Scripts\activate
start "Backend - DO NOT CLOSE" python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

echo Done! Backend is starting...
timeout /t 3 /nobreak >nul
