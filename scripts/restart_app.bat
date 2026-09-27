@echo off
REM Clean restart of entire application

echo ============================================================
echo SOCRATIC TUTORING SYSTEM - STARTING
echo ============================================================
echo.

echo [1/6] Killing existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process on port 8000
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    echo Killing process on port 5173
    taskkill /F /PID %%a 2>nul
)
echo Done
echo.

echo [2/6] Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Virtual environment not found
    pause
    exit /b 1
)
echo.

echo [3/6] Checking .env file...
if not exist .env (
    echo ERROR: .env file not found!
    pause
    exit /b 1
)
echo .env found
echo.

echo [4/6] Testing database connection...
python -c "from database.connection import engine; print('Database connected:', engine.url)" 2>nul
if errorlevel 1 (
    echo ERROR: Database connection failed
    pause
    exit /b 1
)
echo.

echo [5/6] Starting BACKEND on http://localhost:8000...
start "BACKEND - Socratic Tutor API" cmd /k "cd /d "%CD%" && call venv\Scripts\activate && echo [DATABASE] Connecting... && python -m uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000"
echo Backend starting...
timeout /t 3 /nobreak >nul
echo.

echo [6/6] Starting FRONTEND on http://localhost:5173...
start "FRONTEND - Socratic Tutor UI" cmd /k "cd /d "%CD%\frontend" && npm run dev"
echo Frontend starting...
echo.

echo ============================================================
echo APPLICATION STARTED
echo ============================================================
echo.
echo Two windows opened:
echo   1. BACKEND  - http://localhost:8000
echo   2. FRONTEND - http://localhost:5173
echo.
echo Wait 5 seconds for servers to start, then open:
echo   http://localhost:5173
echo.
echo If you see errors, check the server windows.
echo.
echo Database has 7 sample problems ready to use.
echo You can also upload PDFs (max 2 pages).
echo.
pause
