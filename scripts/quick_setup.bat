@echo off
REM Quick setup - Fixed for psycopg2

echo ============================================================
echo QUICK SETUP - SOCRATIC TUTORING SYSTEM
echo ============================================================
echo.

echo [1/4] Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Virtual environment not found
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
)
echo Done
echo.

echo [2/4] Installing Python packages...
pip install --upgrade pip
pip install psycopg2-binary --force-reinstall
pip install -r requirements.txt
echo Done
echo.

echo [3/4] Setting up database...
python database\init_db.py
if errorlevel 1 (
    echo.
    echo ERROR: Database setup failed
    echo.
    echo Please check:
    echo   1. .env file exists with DATABASE_URL
    echo   2. Supabase credentials are correct
    echo   3. Internet connection is working
    echo.
    pause
    exit /b 1
)
echo.

echo [4/4] Running PDF migration...
python database\migrate_add_pdf_fields.py
echo.

echo ============================================================
echo SETUP COMPLETE
echo ============================================================
echo.
echo Database is ready with:
echo   - All tables created
echo   - Sample problems loaded
echo   - PDF fields configured
echo.
echo Next steps:
echo   1. Close any running backend/frontend
echo   2. Run: scripts\restart_app.bat
echo.
pause
