"""
Database connection management.

This file handles:
- Creating the database engine (connection to SQLite)
- Creating sessions (for querying/inserting data)
- Providing easy access to the database
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator


# Database file path (SQLite stores everything in one file)
DATABASE_URL = "sqlite:///./socratic_tutoring.db"

# Create engine (the connection to the database)
# echo=True means SQLAlchemy will print all SQL queries (helpful for learning!)
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see SQL queries
    connect_args={"check_same_thread": False}  # Needed for SQLite threading
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
