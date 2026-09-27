"""
Test database connection and check tables exist
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import engine, SessionLocal
from database.models import Problem, PDFDocument
from sqlalchemy import inspect

def test_database():
    print("="*60)
    print("DATABASE CONNECTION TEST")
    print("="*60)
    print()

    # Test 1: Connection
    print("[1/4] Testing database connection...")
    try:
        with engine.connect() as conn:
            print("    SUCCESS: Connected to database")
    except Exception as e:
        print(f"    FAILED: {e}")
        return False

    print()

    # Test 2: Check tables exist
    print("[2/4] Checking if tables exist...")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        required_tables = ['problems', 'sessions', 'turns', 'hints_given',
                          'verifier_flags', 'pdf_documents']

        missing_tables = [t for t in required_tables if t not in tables]

        if missing_tables:
            print(f"    FAILED: Missing tables: {missing_tables}")
            print("    Run: scripts\\setup_database.bat")
            return False
        else:
            print(f"    SUCCESS: All {len(required_tables)} tables exist")

    except Exception as e:
        print(f"    FAILED: {e}")
        return False

    print()

    # Test 3: Check problems table
    print("[3/4] Checking problems table...")
    try:
        db = SessionLocal()
        problem_count = db.query(Problem).count()
        db.close()

        if problem_count == 0:
            print("    WARNING: No problems found")
            print("    Run: python database\\init_db.py")
        else:
            print(f"    SUCCESS: Found {problem_count} problems")

    except Exception as e:
        print(f"    FAILED: {e}")

    print()

    # Test 4: Check PDF fields exist
    print("[4/4] Checking PDF document fields...")
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('pdf_documents')]

        if 'title' in columns and 'description' in columns:
            print("    SUCCESS: PDF fields (title, description) exist")
        else:
            print("    WARNING: PDF fields missing")
            print("    Run: python database\\migrate_add_pdf_fields.py")

    except Exception as e:
        print(f"    FAILED: {e}")

    print()
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print()
    print("If all tests passed:")
    print("  Your database is ready!")
    print("  Start the app: scripts\\restart_app.bat")
    print()
    print("If tests failed:")
    print("  Run setup: scripts\\setup_database.bat")
    print()

    return True

if __name__ == "__main__":
    test_database()
