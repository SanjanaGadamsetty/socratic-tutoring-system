"""
Job management API endpoints.

Handles background job creation, status checking, and cancellation.
"""

import sys
import os
import json
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from database.models import Job, JobStatus, Problem
from database.connection import get_db
from app.api.schemas import SessionStartRequest, TurnSubmitRequest


router = APIRouter()


# Response schemas
class JobResponse(BaseModel):
    job_id: int
    job_type: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    retry_count: int

    class Config:
        from_attributes = True


# ===== ENDPOINT 1: Create Start Session Job =====

@router.post("/jobs/sessions/start", response_model=JobResponse, status_code=202)
def create_start_session_job(
    request: SessionStartRequest,
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = None
):
    """
    Create a background job to start a session.

    Returns immediately with job ID.
    Client can poll job status to get result.

    Supports idempotency - same key returns same job.
    """
    # Check if problem exists
    problem = db.query(Problem).filter(Problem.id == request.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Check idempotency
    if idempotency_key:
        existing_job = db.query(Job).filter(Job.idempotency_key == idempotency_key).first()
        if existing_job:
            # Return existing job (idempotent)
            return JobResponse(
                job_id=existing_job.id,
                job_type=existing_job.job_type,
                status=existing_job.status.value,
                result=json.loads(existing_job.result_data) if existing_job.result_data else None,
                error=existing_job.error_message,
                created_at=str(existing_job.created_at),
                started_at=str(existing_job.started_at) if existing_job.started_at else None,
                completed_at=str(existing_job.completed_at) if existing_job.completed_at else None,
                retry_count=existing_job.retry_count
            )

    # Create new job
    job = Job(
        job_type="start_session",
        status=JobStatus.QUEUED,
        input_data=json.dumps({
            "problem_id": request.problem_id,
            "student_id": request.student_id
        }),
        idempotency_key=idempotency_key or f"start-{uuid.uuid4().hex[:16]}",
        max_retries=3
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return JobResponse(
        job_id=job.id,
        job_type=job.job_type,
        status=job.status.value,
        result=None,
        error=None,
        created_at=str(job.created_at),
        started_at=None,
        completed_at=None,
        retry_count=0
    )


# ===== ENDPOINT 2: Create Submit Turn Job =====

@router.post("/jobs/sessions/{session_id}/turn", response_model=JobResponse, status_code=202)
def create_submit_turn_job(
    session_id: int,
    request: TurnSubmitRequest,
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = None
):
    """
    Create a background job to submit a student turn.

    Returns immediately with job ID.
    Client can poll job status to get result.
    """
    # Check idempotency
    if idempotency_key:
        existing_job = db.query(Job).filter(Job.idempotency_key == idempotency_key).first()
        if existing_job:
            return JobResponse(
                job_id=existing_job.id,
                job_type=existing_job.job_type,
                status=existing_job.status.value,
                result=json.loads(existing_job.result_data) if existing_job.result_data else None,
                error=existing_job.error_message,
                created_at=str(existing_job.created_at),
                started_at=str(existing_job.started_at) if existing_job.started_at else None,
                completed_at=str(existing_job.completed_at) if existing_job.completed_at else None,
                retry_count=existing_job.retry_count
            )

    # Create new job
    job = Job(
        job_type="submit_turn",
        status=JobStatus.QUEUED,
        input_data=json.dumps({
            "session_id": session_id,
            "student_answer": request.student_answer
        }),
        idempotency_key=idempotency_key or f"turn-{session_id}-{uuid.uuid4().hex[:16]}",
        max_retries=3
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return JobResponse(
        job_id=job.id,
        job_type=job.job_type,
        status=job.status.value,
        result=None,
        error=None,
        created_at=str(job.created_at),
        started_at=None,
        completed_at=None,
        retry_count=0
    )


# ===== ENDPOINT 3: Get Job Status =====

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """
    Get the current status and result of a job.

    Status values:
    - queued: Job is waiting to be processed
    - running: Job is currently being processed
    - completed: Job finished successfully (check result)
    - failed: Job failed after retries (check error)
    - cancelled: Job was cancelled
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse(
        job_id=job.id,
        job_type=job.job_type,
        status=job.status.value,
        result=json.loads(job.result_data) if job.result_data else None,
        error=job.error_message,
        created_at=str(job.created_at),
        started_at=str(job.started_at) if job.started_at else None,
        completed_at=str(job.completed_at) if job.completed_at else None,
        retry_count=job.retry_count
    )


# ===== ENDPOINT 4: Cancel Job =====

@router.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: int, db: Session = Depends(get_db)):
    """
    Cancel a queued job.

    Can only cancel jobs that are queued (not yet started).
    Running jobs cannot be cancelled mid-execution.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == JobStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel running job. Wait for completion or let it timeout."
        )

    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
        raise HTTPException(
            status_code=400,
            detail=f"Job already in terminal state: {job.status.value}"
        )

    job.status = JobStatus.CANCELLED
    db.commit()

    return {
        "message": f"Job {job_id} cancelled",
        "job_id": job_id,
        "status": job.status.value
    }


# ===== ENDPOINT 5: List Jobs =====

@router.get("/jobs", response_model=list)
def list_jobs(
    limit: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List recent jobs, optionally filtered by status.
    """
    query = db.query(Job).order_by(Job.created_at.desc())

    if status:
        try:
            status_enum = JobStatus(status)
            query = query.filter(Job.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    jobs = query.limit(limit).all()

    return [
        {
            "job_id": job.id,
            "job_type": job.job_type,
            "status": job.status.value,
            "created_at": str(job.created_at),
            "retry_count": job.retry_count
        }
        for job in jobs
    ]


# ===== EXPLANATION =====

"""
DURABLE EXECUTION FLOW:

1. CLIENT CREATES JOB:
    POST /jobs/sessions/start
        |
        v
    Job created with status=QUEUED
        |
        v
    Return job_id immediately (202 Accepted)

2. WORKER PROCESSES JOB:
    Worker polls for queued jobs
        |
        v
    Picks up job, sets status=RUNNING
        |
        v
    Executes agent logic
        |
        |-- Success: status=COMPLETED, save result
        |
        |-- Failure: retry_count++
                |
                |-- retry_count < max_retries: status=QUEUED (retry)
                |
                |-- retry_count >= max_retries: status=FAILED

3. CLIENT POLLS STATUS:
    GET /jobs/{job_id}
        |
        v
    Returns current status + result (if completed)

IDEMPOTENCY:
    Client sends idempotency_key
        |
        v
    Server checks if job with that key exists
        |
        |-- Exists? Return existing job (no duplicate)
        |
        |-- New? Create job

    This prevents:
    - User clicks "Start" twice -> only 1 session created
    - Network retry -> doesn't duplicate operation

FLOW DIAGRAM:

    User                API                 Database            Worker
     |                  |                      |                  |
     | POST /jobs/...   |                      |                  |
     |----------------->|                      |                  |
     |                  | INSERT job           |                  |
     |                  |--------------------->|                  |
     |                  |                      |                  |
     | 202 {job_id: 1}  |                      |                  |
     |<-----------------|                      |                  |
     |                  |                      |                  |
     |                  |                      | Poll for jobs    |
     |                  |                      |<-----------------|
     |                  |                      |                  |
     |                  |                      | Job 1 (QUEUED)   |
     |                  |                      |----------------->|
     |                  |                      |                  |
     |                  |                      | UPDATE status    | Process job
     |                  |                      |<-----------------| (RUNNING)
     |                  |                      |                  |
     | GET /jobs/1      |                      |                  |
     |----------------->|                      |                  |
     |                  | SELECT job           |                  |
     |                  |--------------------->|                  |
     |                  |                      |                  |
     | {status:RUNNING} |                      |                  |
     |<-----------------|                      |                  |
     |                  |                      |                  |
     |                  |                      | UPDATE result    |
     |                  |                      |<-----------------|
     |                  |                      | (COMPLETED)      |
     |                  |                      |                  |
     | GET /jobs/1      |                      |                  |
     |----------------->|                      |                  |
     |                  | SELECT job           |                  |
     |                  |--------------------->|                  |
     |                  |                      |                  |
     | {status:COMPLETED, result:{...}}        |                  |
     |<-----------------|                      |                  |
"""
