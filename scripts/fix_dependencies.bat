@echo off
REM Fix missing dependencies

echo ============================================================
echo FIXING DEPENDENCIES
echo ============================================================
echo.

echo [Step 1/3] Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Please create venv first: python -m venv venv
    pause
    exit /b 1
)
echo Done
echo.

echo [Step 2/3] Installing PostgreSQL driver...
echo Installing psycopg2-binary...
pip install psycopg2-binary --force-reinstall
echo.

echo [Step 3/3] Installing all requirements...
pip install -r requirements.txt
echo.

echo ============================================================
echo DEPENDENCIES FIXED
echo ============================================================
echo.
echo Now try starting the backend:
echo   python -m uvicorn app.api.main:app --reload
echo.
pause
