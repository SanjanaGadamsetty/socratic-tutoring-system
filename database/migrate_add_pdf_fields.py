"""
Migration: Add title and description fields to pdf_documents table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database.connection import engine

def migrate():
    """Add title and description columns to pdf_documents table"""

    migration_sql = """
    -- Add title column if it doesn't exist
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='pdf_documents' AND column_name='title'
        ) THEN
            ALTER TABLE pdf_documents ADD COLUMN title VARCHAR(255);
        END IF;
    END $$;

    -- Add description column if it doesn't exist
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='pdf_documents' AND column_name='description'
        ) THEN
            ALTER TABLE pdf_documents ADD COLUMN description TEXT;
        END IF;
    END $$;
    """

    try:
        with engine.connect() as conn:
            print("Running migration...")
            conn.execute(text(migration_sql))
            conn.commit()
            print("Migration completed successfully!")
            print("- Added 'title' column to pdf_documents")
            print("- Added 'description' column to pdf_documents")
    except Exception as e:
        print(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    print("="*60)
    print("PDF DOCUMENTS TABLE MIGRATION")
    print("="*60)
    print()
    migrate()
    print()
    print("You can now upload PDFs with title and description!")
