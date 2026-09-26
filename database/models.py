"""
Database models for Socratic Tutoring System

These classes define our database tables using SQLAlchemy ORM.
Each class = one table in the database.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import declarative_base, relationship
import enum


# Base class for all models
Base = declarative_base()


class DifficultyLevel(enum.Enum):
    """Enum for problem difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SessionStatus(enum.Enum):
    """Enum for session status"""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Speaker(enum.Enum):
    """Who is speaking in a turn"""
    TUTOR = "tutor"
    STUDENT = "student"


class JobStatus(enum.Enum):
    """Status of background jobs"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ===== TABLE 1: PROBLEMS =====
class Problem(Base):
    """
    Stores tutoring problems/questions.
    Instructors create these ahead of time.
    """
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    problem_text = Column(Text, nullable=False)
    correct_answer = Column(String(500), nullable=False)
    topic = Column(String(100), nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sessions = relationship("Session", back_populates="problem")

    def __repr__(self):
        return f"<Problem(id={self.id}, title='{self.title}', difficulty={self.difficulty.value})>"


# ===== TABLE 2: SESSIONS =====
class Session(Base):
    """
    Tracks each tutoring session.
    One student working on one problem = one session.
    """
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    student_id = Column(String(100), nullable=False)  # Could be user ID or name
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.STARTED)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    problem = relationship("Problem", back_populates="sessions")
    turns = relationship("Turn", back_populates="session", cascade="all, delete-orphan")
    hints_given = relationship("HintGiven", back_populates="session", cascade="all, delete-orphan")
    verifier_flags = relationship("VerifierFlag", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session(id={self.id}, student='{self.student_id}', status={self.status.value})>"


# ===== TABLE 3: TURNS =====
class Turn(Base):
    """
    Each back-and-forth in the conversation.
    Tutor asks question -> Student responds = 2 turns
    """
    __tablename__ = "turns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    turn_number = Column(Integer, nullable=False)  # 1, 2, 3...
    speaker = Column(SQLEnum(Speaker), nullable=False)  # tutor or student
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="turns")
    verifier_flags = relationship("VerifierFlag", back_populates="turn", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Turn(id={self.id}, session={self.session_id}, speaker={self.speaker.value}, turn={self.turn_number})>"


# ===== TABLE 4: HINTS GIVEN =====
class HintGiven(Base):
    """
    Tracks when hints were given to the student.
    Used for hint escalation ladder (level 1 -> 2 -> 3)
    """
    __tablename__ = "hints_given"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    hint_level = Column(Integer, nullable=False)  # 1, 2, or 3
    hint_text = Column(Text, nullable=False)
    given_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="hints_given")

    def __repr__(self):
        return f"<HintGiven(id={self.id}, session={self.session_id}, level={self.hint_level})>"


# ===== TABLE 5: VERIFIER FLAGS =====
class VerifierFlag(Base):
    """
    When verifier agent rejects a tutor response.
    Tracks attempted answer leaks and rejections.
    """
    __tablename__ = "verifier_flags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    turn_id = Column(Integer, ForeignKey("turns.id"), nullable=True)  # Which turn was flagged
    rejected_message = Column(Text, nullable=False)  # What the tutor tried to say
    reason = Column(Text, nullable=False)  # Why it was rejected
    flagged_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="verifier_flags")
    turn = relationship("Turn", back_populates="verifier_flags")

    def __repr__(self):
        return f"<VerifierFlag(id={self.id}, session={self.session_id}, reason='{self.reason[:30]}...')>"


# ===== TABLE 6: JOBS (Day 3) =====
class Job(Base):
    """
    Background job tracking for durable execution.
    Handles long-running agent operations.
    """
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_type = Column(String(100), nullable=False)  # e.g., "start_session", "submit_turn"
    status = Column(SQLEnum(JobStatus), default=JobStatus.QUEUED)
    idempotency_key = Column(String(255), unique=True, nullable=True)  # Prevent duplicates

    # Input data (JSON)
    input_data = Column(Text, nullable=False)  # JSON string

    # Output data (JSON)
    result_data = Column(Text, nullable=True)  # JSON string
    error_message = Column(Text, nullable=True)

    # Retry tracking
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Worker tracking (optional - for heartbeat)
    worker_id = Column(String(100), nullable=True)
    last_heartbeat = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Job(id={self.id}, type='{self.job_type}', status={self.status.value})>"


# ===== EXPLANATION OF KEY CONCEPTS =====

"""
WHAT IS AN ORM (Object-Relational Mapping)?
    Instead of writing SQL:
        CREATE TABLE problems (id INTEGER PRIMARY KEY, title TEXT...);
        INSERT INTO problems VALUES (1, 'Math Problem', ...);

    We write Python:
        problem = Problem(title='Math Problem', ...)
        session.add(problem)
        session.commit()

    SQLAlchemy translates Python -> SQL automatically!

WHAT ARE RELATIONSHIPS?
    relationships tell SQLAlchemy how tables connect:

    problem.sessions -> Get all sessions for this problem
    session.problem -> Get the problem this session is working on
    session.turns -> Get all conversation turns in this session

    It's like having navigation links between tables!

WHAT IS CASCADE?
    cascade="all, delete-orphan" means:
    If you delete a session, automatically delete all its turns/hints/flags

    Without cascade:
        Delete session -> turns stay in database (orphaned)

    With cascade:
        Delete session -> turns automatically deleted too (clean!)
"""
