@echo off
REM Complete setup from scratch - fixes all issues

echo ============================================================
echo COMPLETE APPLICATION SETUP
echo ============================================================
echo.
echo This will:
echo   1. Fix Python dependencies
echo   2. Setup Supabase database
echo   3. Restart the application
echo.
echo Press Ctrl+C to cancel, or
pause
echo.

echo [1/3] FIXING DEPENDENCIES
echo ============================================================
call scripts\fix_dependencies.bat
if errorlevel 1 (
    echo ERROR: Dependency fix failed
    pause
    exit /b 1
)
echo.

echo [2/3] SETTING UP DATABASE
echo ============================================================
call venv\Scripts\activate
python database\init_db.py
if errorlevel 1 (
    echo ERROR: Database setup failed
    echo.
    echo Common issues:
    echo   - Check .env has correct DATABASE_URL
    echo   - Check Supabase credentials
    echo   - Check internet connection
    pause
    exit /b 1
)
echo.
python database\migrate_add_pdf_fields.py
echo.

echo [3/3] TESTING DATABASE
echo ============================================================
python scripts\test_database.py
echo.

echo ============================================================
echo SETUP COMPLETE
echo ============================================================
echo.
echo Now starting the application...
echo.
pause

REM Start the app
call scripts\restart_app.bat
