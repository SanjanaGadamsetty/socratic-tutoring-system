@echo off
REM Setup Supabase database with tables and sample data

echo ============================================================
echo SUPABASE DATABASE SETUP
echo ============================================================
echo.

echo [Step 1/3] Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Done
echo.

echo [Step 2/3] Creating tables and seeding sample problems...
python database\init_db.py
if errorlevel 1 (
    echo ERROR: Database initialization failed
    pause
    exit /b 1
)
echo.

echo [Step 3/3] Running PDF migration (add title/description fields)...
python database\migrate_add_pdf_fields.py
echo.

echo ============================================================
echo DATABASE SETUP COMPLETE
echo ============================================================
echo.
echo Your Supabase database now has:
echo   - All required tables
echo   - 7 sample problems
echo   - PDF document fields
echo.
echo Next: Start the application
echo   scripts\restart_app.bat
echo.
pause
