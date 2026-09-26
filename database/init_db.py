"""
Database initialization script.

Run this file to:
1. Create all tables in the database
2. Seed initial sample data (problems)
"""

import sys
import os

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Base, Problem, DifficultyLevel
from database.connection import engine, SessionLocal


def create_tables():
    """
    Create all database tables.

    Flow:
        1. Read all model classes (Problem, Session, Turn, etc.)
        2. Generate CREATE TABLE SQL for each
        3. Execute SQL on database
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


def seed_sample_problems():
    """
    Add sample problems to the database.

    These are test problems for development/demo.
    """
    print("\nSeeding sample problems...")

    db = SessionLocal()

    try:
        # Check if problems already exist
        existing_count = db.query(Problem).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} problems. Skipping seed.")
            return

        # Sample problems for testing
        problems = [
            Problem(
                title="Basic Multiplication",
                problem_text="What is 15 multiplied by 8?",
                correct_answer="120",
                topic="Mathematics - Multiplication",
                difficulty=DifficultyLevel.EASY
            ),
            Problem(
                title="Fraction Addition",
                problem_text="What is 1/4 + 1/3? Express as a simplified fraction.",
                correct_answer="7/12",
                topic="Mathematics - Fractions",
                difficulty=DifficultyLevel.MEDIUM
            ),
            Problem(
                title="Quadratic Equation",
                problem_text="Solve for x: x² - 5x + 6 = 0",
                correct_answer="x = 2 or x = 3",
                topic="Algebra - Quadratic Equations",
                difficulty=DifficultyLevel.MEDIUM
            ),
            Problem(
                title="Pythagorean Theorem",
                problem_text="A right triangle has legs of length 3 and 4. What is the length of the hypotenuse?",
                correct_answer="5",
                topic="Geometry - Pythagorean Theorem",
                difficulty=DifficultyLevel.EASY
            ),
            Problem(
                title="Systems of Equations",
                problem_text="Solve the system: 2x + y = 10 and x - y = 2",
                correct_answer="x = 4, y = 2",
                topic="Algebra - Systems of Equations",
                difficulty=DifficultyLevel.HARD
            ),
            Problem(
                title="Percentage Calculation",
                problem_text="What is 15% of 80?",
                correct_answer="12",
                topic="Mathematics - Percentages",
                difficulty=DifficultyLevel.EASY
            ),
            Problem(
                title="Area of Circle",
                problem_text="What is the area of a circle with radius 5? Use π = 3.14",
                correct_answer="78.5",
                topic="Geometry - Circles",
                difficulty=DifficultyLevel.MEDIUM
            ),
        ]

        # Add all problems to session
        for problem in problems:
            db.add(problem)

        # Commit (save) to database
        db.commit()

        print(f"Successfully seeded {len(problems)} sample problems!")

        # Show what was added
        print("\nProblems added:")
        for problem in problems:
            print(f"  - [{problem.difficulty.value.upper()}] {problem.title}")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()

    finally:
        db.close()


def main():
    """
    Main initialization function.
    """
    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)

    # Step 1: Create tables
    create_tables()

    # Step 2: Seed sample data
    seed_sample_problems()

    print("\n" + "=" * 60)
    print("DATABASE READY!")
    print("=" * 60)
    print("\nYou can now:")
    print("  1. Run the API server")
    print("  2. Start tutoring sessions")
    print("  3. View the database file: socratic_tutoring.db")


if __name__ == "__main__":
    main()


# ===== EXPLANATION =====

"""
WHAT HAPPENS WHEN YOU RUN THIS FILE:

Step 1: create_tables()
    ┌─────────────────┐
    │  models.py      │
    │  (5 classes)    │
    └────────┬────────┘
             │
             v
    Base.metadata.create_all()
             │
             v
    ┌─────────────────┐
    │ SQLite Database │
    │  5 tables       │
    │  created        │
    └─────────────────┘

Step 2: seed_sample_problems()
    ┌─────────────────┐
    │ Python objects  │
    │ Problem(...)    │
    │ Problem(...)    │
    └────────┬────────┘
             │
             | db.add()
             v
    ┌─────────────────┐
    │ Session         │
    │ (shopping cart) │
    └────────┬────────┘
             │
             | db.commit()
             v
    ┌─────────────────┐
    │ Database        │
    │ INSERT INTO...  │
    │ 7 problems      │
    └─────────────────┘

FLOW OF DATA:
    Python Code (Problem objects)
        |
        | session.add()
        v
    Session Buffer (in memory)
        |
        | session.commit()
        v
    SQLAlchemy (generates SQL)
        |
        | INSERT INTO problems...
        v
    SQLite Database (on disk)

WHY CHECK existing_count?
    Prevents duplicate data if you run this script twice!
"""
