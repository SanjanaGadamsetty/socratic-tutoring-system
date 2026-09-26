"""
Background worker for processing jobs.

This handles long-running agent operations asynchronously.
"""

import sys
import os
import json
import time
import uuid
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import and_
from database.models import Job, JobStatus, Problem, Session as DBSession, Turn, Speaker, SessionStatus
from database.connection import SessionLocal
from app.agent import TutoringAgent


class Worker:
    """
    Background worker that processes jobs from the queue.
    """

    def __init__(self, worker_id: str = None):
        self.worker_id = worker_id or f"worker-{uuid.uuid4().hex[:8]}"
        self.running = True
        print(f"Worker {self.worker_id} initialized")

    def process_start_session_job(self, job: Job, db):
        """
        Process a start_session job.
        """
        input_data = json.loads(job.input_data)
        problem_id = input_data['problem_id']
        student_id = input_data['student_id']

        # Get problem
        problem = db.query(Problem).filter(Problem.id == problem_id).first()
        if not problem:
            raise Exception(f"Problem {problem_id} not found")

        # Create session
        session = DBSession(
            problem_id=problem_id,
            student_id=student_id,
            status=SessionStatus.IN_PROGRESS
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # Generate first question
        agent = TutoringAgent()
        prompt = f"""You are starting a Socratic tutoring session.

Problem: {problem.problem_text}
Correct Answer (DO NOT REVEAL): {problem.correct_answer}

Generate your first Socratic question to guide the student toward understanding.
Remember: ASK questions, don't give answers!"""

        first_question = agent.run(prompt, max_iterations=2)

        # Save turn
        turn = Turn(
            session_id=session.id,
            turn_number=1,
            speaker=Speaker.TUTOR,
            message=first_question
        )
        db.add(turn)
        db.commit()

        # Return result
        return {
            "session_id": session.id,
            "problem_id": problem.id,
            "problem_title": problem.title,
            "first_question": first_question,
            "status": session.status.value
        }

    def process_submit_turn_job(self, job: Job, db):
        """
        Process a submit_turn job.
        """
        input_data = json.loads(job.input_data)
        session_id = input_data['session_id']
        student_answer = input_data['student_answer']

        # Get session
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if not session:
            raise Exception(f"Session {session_id} not found")

        problem = session.problem

        # Save student turn
        turn_number = db.query(Turn).filter(Turn.session_id == session_id).count() + 1
        student_turn = Turn(
            session_id=session_id,
            turn_number=turn_number,
            speaker=Speaker.STUDENT,
            message=student_answer
        )
        db.add(student_turn)
        db.commit()

        # Check correctness
        is_correct = student_answer.strip().lower() == problem.correct_answer.strip().lower()

        if is_correct:
            session.status = SessionStatus.COMPLETED
            db.commit()
            tutor_response = "Excellent! You got it right! Great work using logical thinking to solve this problem."
        else:
            # Generate next question
            agent = TutoringAgent()

            previous_turns = db.query(Turn).filter(
                Turn.session_id == session_id
            ).order_by(Turn.turn_number).all()

            history = "\n".join([
                f"{turn.speaker.value.upper()}: {turn.message}"
                for turn in previous_turns
            ])

            prompt = f"""You are continuing a Socratic tutoring session.

Problem: {problem.problem_text}
Correct Answer (DO NOT REVEAL): {problem.correct_answer}

Conversation so far:
{history}

The student's latest answer is INCORRECT. Generate your next Socratic question to guide them closer to the answer.
Remember: ASK guiding questions, don't reveal the answer!"""

            tutor_response = agent.run(prompt, max_iterations=2)

        # Save tutor turn
        tutor_turn = Turn(
            session_id=session_id,
            turn_number=turn_number + 1,
            speaker=Speaker.TUTOR,
            message=tutor_response
        )
        db.add(tutor_turn)
        db.commit()

        return {
            "session_id": session_id,
            "tutor_question": tutor_response,
            "is_correct": is_correct,
            "session_status": session.status.value
        }

    def process_job(self, job: Job):
        """
        Process a single job based on its type.
        """
        db = SessionLocal()

        try:
            print(f"[{self.worker_id}] Processing job {job.id} ({job.job_type})")

            # Update job status
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            job.worker_id = self.worker_id
            job.last_heartbeat = datetime.utcnow()
            db.commit()

            # Process based on job type
            if job.job_type == "start_session":
                result = self.process_start_session_job(job, db)
            elif job.job_type == "submit_turn":
                result = self.process_submit_turn_job(job, db)
            else:
                raise Exception(f"Unknown job type: {job.job_type}")

            # Mark as completed
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.result_data = json.dumps(result)
            db.commit()

            print(f"[{self.worker_id}] Job {job.id} completed successfully")

        except Exception as e:
            print(f"[{self.worker_id}] Job {job.id} failed: {e}")

            # Handle retry
            job.retry_count += 1

            if job.retry_count < job.max_retries:
                # Retry
                job.status = JobStatus.QUEUED
                job.error_message = f"Retry {job.retry_count}/{job.max_retries}: {str(e)}"
                print(f"[{self.worker_id}] Job {job.id} will retry ({job.retry_count}/{job.max_retries})")
            else:
                # Max retries reached
                job.status = JobStatus.FAILED
                job.completed_at = datetime.utcnow()
                job.error_message = f"Failed after {job.max_retries} retries: {str(e)}"
                print(f"[{self.worker_id}] Job {job.id} failed permanently")

            db.commit()

        finally:
            db.close()

    def find_and_process_jobs(self):
        """
        Find queued jobs and process them.
        """
        db = SessionLocal()

        try:
            # Find queued jobs or stuck jobs (heartbeat timeout)
            timeout_threshold = datetime.utcnow() - timedelta(minutes=5)

            job = db.query(Job).filter(
                and_(
                    Job.status.in_([JobStatus.QUEUED, JobStatus.RUNNING]),
                    (Job.last_heartbeat.is_(None)) | (Job.last_heartbeat < timeout_threshold)
                )
            ).order_by(Job.created_at).first()

            if job:
                # Process this job
                db.close()  # Close connection before processing
                self.process_job(job)
                return True
            else:
                return False

        finally:
            if db:
                db.close()

    def run(self, poll_interval: int = 2):
        """
        Main worker loop.
        """
        print(f"[{self.worker_id}] Worker started. Polling every {poll_interval}s")

        try:
            while self.running:
                # Try to process a job
                found_job = self.find_and_process_jobs()

                if not found_job:
                    # No jobs, wait before polling again
                    time.sleep(poll_interval)

        except KeyboardInterrupt:
            print(f"\n[{self.worker_id}] Worker stopping...")
        finally:
            print(f"[{self.worker_id}] Worker stopped")

    def stop(self):
        """
        Stop the worker gracefully.
        """
        self.running = False


# CLI to run worker
if __name__ == "__main__":
    worker = Worker()
    worker.run()
