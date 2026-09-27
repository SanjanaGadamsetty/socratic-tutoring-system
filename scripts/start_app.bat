@echo off
echo ================================
echo Socratic Tutoring System Startup
echo ================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Warning: Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    echo Virtual environment found
    call venv\Scripts\activate
)

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules\" (
    echo Warning: Frontend dependencies not found. Installing...
    cd frontend
    call npm install
    cd ..
) else (
    echo Frontend dependencies found
)

echo.
echo Starting services...
echo.

REM Start backend
echo Starting FastAPI backend on http://localhost:8000
start "FastAPI Backend" cmd /k "venv\Scripts\activate && python -m uvicorn app.api.main:app --reload"

REM Wait for backend to start
timeout /t 5 /nobreak

REM Start frontend
echo Starting React frontend on http://localhost:5173
cd frontend
call npm run dev
