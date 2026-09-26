"""
Database connection management.

This file handles:
- Creating the database engine (connection to Supabase PostgreSQL)
- Creating sessions (for querying/inserting data)
- Providing easy access to the database
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to local SQLite for development
    import pathlib
    db_path = pathlib.Path(__file__).parent / "socratic_tutoring.db"
    DATABASE_URL = f"sqlite:///{db_path}"
    print(f"[DATABASE] Using local SQLite: {db_path}")

# Create engine (the connection to the database)
# echo=True means SQLAlchemy will print all SQL queries (helpful for learning!)
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see SQL queries
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Connection pool size
    max_overflow=20  # Extra connections if needed
)

# Session factory (creates new database sessions)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Get a database session.

    Usage in code:
        db = next(get_db())
        problems = db.query(Problem).all()
        db.close()

    Or with context manager (auto-closes):
        with next(get_db()) as db:
            problems = db.query(Problem).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===== EXPLANATION =====

"""
WHAT IS AN ENGINE?
    The engine is like a phone line to the database.
    It handles the connection, sends queries, gets results.

WHAT IS A SESSION?
    A session is like a shopping cart.
    You add items (database changes):
        session.add(problem)
        session.add(session_obj)

    Then checkout (save to database):
        session.commit()

    Or cancel (don't save):
        session.rollback()

WHY USE get_db()?
    It's a generator that:
    1. Creates a session
    2. Lets you use it
    3. Automatically closes it when done

    This prevents database connection leaks!

FLOW:
    Your Code
        |
        | get_db()
        v
    Session Created
        |
        | session.query(...)
        v
    Engine -> Database -> Results
        |
        v
    Session Closed (automatic)
"""
