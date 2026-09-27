@echo off
cd /d "C:\Users\Sanju\OneDrive\Desktop\Apps n Extensions\HOPE-Elite\HDP 1-Agentic AI\AgenticAI-Project\socratic-tutoring-system"
call venv\Scripts\activate
echo Starting backend on http://localhost:8000
echo.
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
pause
