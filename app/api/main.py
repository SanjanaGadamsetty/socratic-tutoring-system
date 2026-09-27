"""
FastAPI Application - Main API Server

This file defines all HTTP endpoints for the tutoring system.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app.api.schemas import (
    SessionStartRequest, SessionStartResponse,
    TurnSubmitRequest, TurnSubmitResponse,
    TranscriptResponse, ProblemsListResponse,
    ProblemResponse, ErrorResponse
)
from database.models import (
    Problem, Session as DBSession, Turn, HintGiven,
    VerifierFlag, SessionStatus, Speaker, PDFDocument
)
from database.connection import get_db
from app.agents.handoff import HandoffController
from app.api.streaming import router as streaming_router
from app.api.jobs import router as jobs_router
from app.api.pdfs import router as pdfs_router


# Create FastAPI app
app = FastAPI(
    title="Socratic Tutoring System API",
    description="Multi-agent tutoring system with Socratic questioning",
    version="1.0.0"
)

# Add CORS middleware (allows frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include streaming router
app.include_router(streaming_router, tags=["Streaming"])

# Include jobs router (Day 3 - Background jobs)
app.include_router(jobs_router, tags=["Background Jobs"])

# Include PDFs router (PDF Feature)
app.include_router(pdfs_router, tags=["PDF Documents"])


# ===== ENDPOINT 1: GET /problems =====

@app.get(
    "/problems",
    response_model=ProblemsListResponse,
    tags=["Problems"],
    summary="List all available problems"
)
def list_problems(db: Session = Depends(get_db)):
    """
    Get all tutoring problems available in the system.

    Returns:
        List of problems with title, difficulty, topic
    """
    problems = db.query(Problem).all()

    return ProblemsListResponse(
        problems=[ProblemResponse.from_orm(p) for p in problems],
        total=len(problems)
    )


# ===== ENDPOINT 2: POST /sessions/start =====

@app.post(
    "/sessions/start",
    response_model=SessionStartResponse,
    tags=["Sessions"],
    summary="Start a new tutoring session",
    status_code=201
)
def start_session(
    request: SessionStartRequest,
    db: Session = Depends(get_db)
):
    """
    Start a new tutoring session for a student on a specific problem or PDF.

    Flow:
        1. Validate problem or PDF exists
        2. Create session in database
        3. Initialize agent with context
        4. Generate first Socratic question
        5. Save first turn to database
        6. Return session ID + first question

    Args:
        request: Contains problem_id or pdf_document_id, and student_id

    Returns:
        Session ID, context details, and first tutor question
    """
    # Validate: must have either problem_id or pdf_document_id
    if not request.problem_id and not request.pdf_document_id:
        raise HTTPException(
            status_code=400,
            detail="Must provide either problem_id or pdf_document_id"
        )

    if request.problem_id and request.pdf_document_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot provide both problem_id and pdf_document_id"
        )

    problem = None
    pdf_doc = None

    # Step 1: Check if problem or PDF exists
    if request.problem_id:
        problem = db.query(Problem).filter(Problem.id == request.problem_id).first()
        if not problem:
            raise HTTPException(
                status_code=404,
                detail=f"Problem with ID {request.problem_id} not found"
            )

    if request.pdf_document_id:
        pdf_doc = db.query(PDFDocument).filter(PDFDocument.id == request.pdf_document_id).first()
        if not pdf_doc:
            raise HTTPException(
                status_code=404,
                detail=f"PDF document with ID {request.pdf_document_id} not found"
            )

    # Step 2: Create session
    session = DBSession(
        problem_id=request.problem_id,
        pdf_document_id=request.pdf_document_id,
        student_id=request.student_id,
        status=SessionStatus.IN_PROGRESS
    )
    db.add(session)
    db.commit()
    db.refresh(session)  # Get auto-generated ID

    # Step 3: Generate first Socratic question
    # Use simple template for now (fast and reliable)
    print("[INFO] Generating first question...")

    if problem:
        # Problem-based: Ask about what they know about the topic
        topic_words = problem.topic.split()[-1] if problem.topic else "this topic"
        first_question = f"Let's work through this together! Before we start, what do you already know about {topic_words}?"
    else:
        # PDF-based: Ask what interests them
        first_question = "I see you've uploaded study material. What topic from this document would you like to explore first?"

    print(f"[INFO] First question ready: {first_question[:50]}...")

    # Step 5: Save first turn
    turn = Turn(
        session_id=session.id,
        turn_number=1,
        speaker=Speaker.TUTOR,
        message=first_question
    )
    db.add(turn)
    db.commit()

    # Step 6: Return response
    # Create a mock problem response for PDF sessions
    if problem:
        problem_response = ProblemResponse.from_orm(problem)
    else:
        problem_response = ProblemResponse(
            id=pdf_doc.id,
            title=pdf_doc.title,
            problem_text=pdf_doc.description or "PDF-based tutoring",
            topic="PDF Document",
            difficulty="medium"
        )

    return SessionStartResponse(
        session_id=session.id,
        problem=problem_response,
        first_question=first_question,
        status=session.status
    )


# ===== ENDPOINT 3: POST /sessions/{session_id}/turn =====

@app.post(
    "/sessions/{session_id}/turn",
    response_model=TurnSubmitResponse,
    tags=["Sessions"],
    summary="Submit student response and get next question"
)
def submit_turn(
    session_id: int,
    request: TurnSubmitRequest,
    db: Session = Depends(get_db)
):
    """
    Submit a student's response and get the next tutor question.

    Flow:
        1. Validate session exists
        2. Save student's turn
        3. Check if answer is correct
        4. If correct -> end session
        5. If incorrect -> generate next question
        6. Save tutor's turn
        7. Return response

    Args:
        session_id: The session ID
        request: Contains student_answer

    Returns:
        Next tutor question, correctness check, session status
    """
    # Step 1: Get session
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    problem = session.problem
    pdf_doc = session.pdf_document

    # Step 2: Save student turn
    turn_number = db.query(Turn).filter(Turn.session_id == session_id).count() + 1

    student_turn = Turn(
        session_id=session_id,
        turn_number=turn_number,
        speaker=Speaker.STUDENT,
        message=request.student_answer
    )
    db.add(student_turn)
    db.commit()

    # Step 3: Get conversation history
    previous_turns = db.query(Turn).filter(
        Turn.session_id == session_id
    ).order_by(Turn.turn_number).all()

    history = "\n".join([
        f"{turn.speaker.value.upper()}: {turn.message}"
        for turn in previous_turns
    ])

    # Step 4: Check if answer is correct (only for problem-based sessions)
    is_correct = None
    if problem:
        is_correct = request.student_answer.strip().lower() == problem.correct_answer.strip().lower()

        if is_correct:
            # Student got it right! End session
            session.status = SessionStatus.COMPLETED
            db.commit()

            tutor_response = "Excellent! You got it right! Great work using logical thinking to solve this problem."
        else:
            # Generate next Socratic question using TutorAgent (fast!)
            try:
                from app.agents.tutor_agent import TutorAgent
                tutor = TutorAgent()

                context = {
                    "student_last_response": request.student_answer,
                    "conversation_history": history,
                    "problem_text": problem.problem_text,
                    "correct_answer": problem.correct_answer
                }

                tutor_response = tutor.generate_response(context)

                # Fallback if empty
                if not tutor_response or len(tutor_response.strip()) < 10:
                    tutor_response = "That's an interesting approach. Can you explain your thinking step by step?"

            except Exception as e:
                print(f"[WARNING] Tutor generation failed: {e}")
                tutor_response = "Let me guide you with a question: What's the first step you would take to solve this?"
    else:
        # PDF-based session - no correct answer to check
        try:
            from app.agents.tutor_agent import TutorAgent
            tutor = TutorAgent()

            context = {
                "student_last_response": request.student_answer,
                "conversation_history": history,
                "pdf_content": pdf_doc.extracted_text
            }

            tutor_response = tutor.generate_response(context)

            # Fallback if empty
            if not tutor_response or len(tutor_response.strip()) < 10:
                tutor_response = "That's interesting! Can you explain more about what you learned from the material?"

        except Exception as e:
            print(f"[WARNING] Tutor generation failed: {e}")
            tutor_response = "That's a good observation. What else stood out to you in the reading?"

    # Save tutor turn
    tutor_turn = Turn(
        session_id=session_id,
        turn_number=turn_number + 1,
        speaker=Speaker.TUTOR,
        message=tutor_response
    )
    db.add(tutor_turn)
    db.commit()

    # Count hints used
    hints_count = db.query(HintGiven).filter(HintGiven.session_id == session_id).count()

    return TurnSubmitResponse(
        session_id=session_id,
        tutor_question=tutor_response,
        is_correct=is_correct,
        hints_used=hints_count,
        session_status=session.status
    )


# ===== ENDPOINT 4: GET /sessions/{session_id}/transcript =====

@app.get(
    "/sessions/{session_id}/transcript",
    response_model=TranscriptResponse,
    tags=["Sessions"],
    summary="Get full session transcript"
)
def get_transcript(session_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the full conversation transcript for a session.

    Includes:
        - All turns (tutor and student)
        - Hints given
        - Verifier flags (rejections)

    Args:
        session_id: The session ID

    Returns:
        Complete session history
    """
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return TranscriptResponse(
        session_id=session.id,
        problem=ProblemResponse.from_orm(session.problem),
        status=session.status,
        started_at=session.started_at,
        ended_at=session.ended_at,
        turns=session.turns,
        hints_given=session.hints_given,
        verifier_flags=session.verifier_flags
    )


# ===== ROOT ENDPOINT =====

@app.get("/", tags=["Health"])
def root():
    """API health check"""
    return {
        "status": "online",
        "service": "Socratic Tutoring System",
        "version": "1.0.0"
    }


# ===== EXPLANATION =====

"""
HOW FASTAPI ENDPOINTS WORK:

1. DECORATOR DEFINES ROUTE:
    @app.post("/sessions/start")

    This means: "When someone POSTs to /sessions/start, call this function"

2. PYDANTIC VALIDATES INPUT:
    def start_session(request: SessionStartRequest, ...):

    FastAPI automatically:
        - Parses JSON body
        - Validates against schema
        - Returns 400 if invalid
        - Passes valid data to function

3. DEPENDENCY INJECTION:
    db: Session = Depends(get_db)

    FastAPI automatically:
        - Calls get_db()
        - Injects database session
        - Closes it after function completes

4. FUNCTION PROCESSES REQUEST:
    - Query database
    - Call agent
    - Save results
    - Build response

5. FASTAPI CONVERTS RESPONSE:
    return SessionStartResponse(...)

    FastAPI automatically:
        - Converts to JSON
        - Validates against schema
        - Returns with correct status code

FLOW FOR /sessions/start:
    Client POST /sessions/start
        |
        | JSON: {"problem_id": 1, "student_id": "alice"}
        v
    FastAPI validates against SessionStartRequest
        |
        v
    Valid -> call start_session()
        |
        v
    Query problem from DB
        |
        v
    Create session
        |
        v
    Call agent to generate first question
        |
        v
    Save turn to DB
        |
        v
    Build SessionStartResponse
        |
        | JSON: {"session_id": 1, "first_question": "..."}
        v
    Return to client
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
