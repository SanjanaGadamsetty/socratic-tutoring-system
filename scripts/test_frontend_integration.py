"""
Test script to verify frontend-backend integration
Run this to test if the API endpoints work correctly
"""

import requests
import json
from database.connection import SessionLocal
from database.models import Problem, PDFDocument

API_BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 60)
    print("FRONTEND-BACKEND INTEGRATION TEST")
    print("=" * 60)
    print()

    # Test 1: Check if API is running
    print("Test 1: Checking if API is running...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✓ API is running")
        else:
            print(f"✗ API returned status code: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        print("\nPlease start the backend first:")
        print("  python -m uvicorn app.api.main:app --reload")
        return

    print()

    # Test 2: Get problems
    print("Test 2: Getting problems list...")
    try:
        response = requests.get(f"{API_BASE_URL}/problems")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Got {data.get('total', 0)} problems")
            print(f"  Response structure: {list(data.keys())}")
            if data.get('problems'):
                problem = data['problems'][0]
                print(f"  First problem fields: {list(problem.keys())}")
                print(f"  Has 'difficulty': {('difficulty' in problem)}")
        else:
            print(f"✗ Failed with status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print()

    # Test 3: Create a test problem if none exist
    db = SessionLocal()
    problems = db.query(Problem).all()

    if not problems:
        print("Test 3: Creating test problem...")
        test_problem = Problem(
            title="Test Math Problem",
            problem_text="What is 12 plus 8?",
            correct_answer="20",
            topic="Math",
            difficulty_level="easy"
        )
        db.add(test_problem)
        db.commit()
        db.refresh(test_problem)
        print(f"✓ Created test problem with ID: {test_problem.id}")
        problem_id = test_problem.id
    else:
        problem_id = problems[0].id
        print(f"Test 3: Using existing problem ID: {problem_id}")

    print()

    # Test 4: Start a session
    print("Test 4: Starting a session...")
    try:
        payload = {
            "problem_id": problem_id,
            "student_id": "test_student"
        }
        response = requests.post(f"{API_BASE_URL}/sessions/start", json=payload)
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Session started")
            print(f"  Response fields: {list(data.keys())}")
            print(f"  Has 'session_id': {('session_id' in data)}")
            print(f"  Has 'first_question': {('first_question' in data)}")
            session_id = data.get('session_id')

            # Test 5: Submit a turn
            if session_id:
                print()
                print("Test 5: Submitting a turn...")
                turn_payload = {
                    "student_answer": "I don't know"
                }
                response = requests.post(
                    f"{API_BASE_URL}/sessions/{session_id}/turn",
                    json=turn_payload
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Turn submitted")
                    print(f"  Response fields: {list(data.keys())}")
                    print(f"  Has 'tutor_question': {('tutor_question' in data)}")
                else:
                    print(f"✗ Failed with status: {response.status_code}")
                    print(f"  Error: {response.text}")
        else:
            print(f"✗ Failed with status: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print()
    print("=" * 60)
    print("FRONTEND CHECKLIST")
    print("=" * 60)
    print()
    print("Frontend should:")
    print("  1. Send 'student_answer' (not 'student_response')")
    print("  2. Expect 'session_id' from /sessions/start")
    print("  3. Expect 'tutor_question' from /sessions/{id}/turn")
    print("  4. Expect 'difficulty' field in problems")
    print()
    print("To start frontend:")
    print("  cd frontend")
    print("  npm run dev")
    print()
    print("Then visit: http://localhost:5173")
    print()

if __name__ == "__main__":
    test_api()
