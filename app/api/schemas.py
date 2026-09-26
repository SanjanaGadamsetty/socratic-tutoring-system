"""
Pydantic schemas for API request/response validation.

These define the shape of data going in/out of the API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ===== ENUMS =====

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SessionStatus(str, Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Speaker(str, Enum):
    TUTOR = "tutor"
    STUDENT = "student"


# ===== REQUEST SCHEMAS =====

class SessionStartRequest(BaseModel):
    """Request to start a new tutoring session"""
    problem_id: int = Field(..., description="ID of the problem to work on", gt=0)
    student_id: str = Field(..., description="Student identifier", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "problem_id": 1,
                "student_id": "student123"
            }
        }


class TurnSubmitRequest(BaseModel):
    """Request to submit a student's answer/response"""
    student_answer: str = Field(..., description="What the student said", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "student_answer": "I think the answer is 120"
            }
        }


# ===== RESPONSE SCHEMAS =====

class ProblemResponse(BaseModel):
    """Information about a problem"""
    id: int
    title: str
    problem_text: str
    topic: str
    difficulty: DifficultyLevel

    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models


class TurnResponse(BaseModel):
    """A single conversation turn"""
    id: int
    turn_number: int
    speaker: Speaker
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True


class HintResponse(BaseModel):
    """A hint that was given"""
    id: int
    hint_level: int
    hint_text: str
    given_at: datetime

    class Config:
        from_attributes = True


class VerifierFlagResponse(BaseModel):
    """A rejection by the verifier agent"""
    id: int
    rejected_message: str
    reason: str
    flagged_at: datetime

    class Config:
        from_attributes = True


class SessionStartResponse(BaseModel):
    """Response when starting a new session"""
    session_id: int
    problem: ProblemResponse
    first_question: str
    status: SessionStatus


class TurnSubmitResponse(BaseModel):
    """Response after submitting a student turn"""
    session_id: int
    tutor_question: str
    is_correct: Optional[bool] = None
    hints_used: int
    session_status: SessionStatus


class TranscriptResponse(BaseModel):
    """Full session transcript"""
    session_id: int
    problem: ProblemResponse
    status: SessionStatus
    started_at: datetime
    ended_at: Optional[datetime]
    turns: List[TurnResponse]
    hints_given: List[HintResponse]
    verifier_flags: List[VerifierFlagResponse]


class ProblemsListResponse(BaseModel):
    """List of all available problems"""
    problems: List[ProblemResponse]
    total: int


# ===== ERROR RESPONSES =====

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Problem not found",
                "detail": "No problem exists with ID 999"
            }
        }


# ===== EXPLANATION =====

"""
WHAT ARE PYDANTIC SCHEMAS?

They define the "contract" for API data:
    - What fields are required
    - What types they must be
    - Validation rules

Example:
    class SessionStartRequest(BaseModel):
        problem_id: int = Field(..., gt=0)
        student_id: str = Field(..., min_length=1)

    This means:
        - problem_id MUST be an integer greater than 0
        - student_id MUST be a non-empty string

    If client sends invalid data:
        {"problem_id": -1, "student_id": ""}

    FastAPI automatically returns:
        400 Bad Request
        {
            "detail": [
                {"loc": ["body", "problem_id"], "msg": "ensure this value is greater than 0"},
                {"loc": ["body", "student_id"], "msg": "ensure this value has at least 1 characters"}
            ]
        }

WHY SEPARATE REQUEST/RESPONSE SCHEMAS?

Request (what comes IN):
    - Contains only what user needs to send
    - Example: SessionStartRequest has problem_id + student_id

Response (what goes OUT):
    - Contains full data including generated fields
    - Example: SessionStartResponse has session_id (auto-generated)

This prevents:
    - Users sending fake IDs
    - Confusion about what's required

FLOW:
    Client Sends JSON
        |
        | FastAPI validates against schema
        v
    Valid? -> Continue to endpoint
    Invalid? -> Return 400 error with details
        |
        v
    Endpoint processes request
        |
        v
    Build response object
        |
        | FastAPI converts to JSON
        v
    Client Receives JSON
"""
