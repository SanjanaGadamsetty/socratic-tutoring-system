"""
Quick test to check why sessions aren't starting
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE = "http://localhost:8000"

print("="*60)
print("SESSION START TEST")
print("="*60)
print()

# Check API key
groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    print(f"GROQ_API_KEY: Set ({groq_key[:10]}...)")
else:
    print("GROQ_API_KEY: NOT SET - This is the problem!")
    print("Set it in .env file")
    exit(1)

print()

# Check if backend is running
try:
    response = requests.get(f"{API_BASE}/")
    print(f"Backend: Running (status {response.status_code})")
except Exception as e:
    print(f"Backend: NOT RUNNING - {e}")
    print("Start backend with: python -m uvicorn app.api.main:app --reload")
    exit(1)

print()

# Check problems
try:
    response = requests.get(f"{API_BASE}/problems")
    if response.status_code == 200:
        problems = response.json()
        total = problems.get('total', 0)
        print(f"Problems: {total} available")
        if total > 0:
            problem_id = problems['problems'][0]['id']
            print(f"Using problem ID: {problem_id}")
            print()

            # Try to start session
            print("Starting session...")
            session_data = {
                "problem_id": problem_id,
                "student_id": "test_student"
            }

            response = requests.post(
                f"{API_BASE}/sessions/start",
                json=session_data,
                timeout=60  # Give it time for multi-agent system
            )

            print(f"Response status: {response.status_code}")
            print()

            if response.status_code == 201:
                session = response.json()
                print("SUCCESS!")
                print(f"Session ID: {session['session_id']}")
                print(f"First question: {session.get('first_question', 'None')}")
            else:
                print("FAILED!")
                print(f"Error: {response.text}")
        else:
            print("No problems in database - run: python database/init_db.py")
    else:
        print(f"Failed to get problems: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
    print()
    print("Common issues:")
    print("1. GROQ_API_KEY not set in .env")
    print("2. Backend not running")
    print("3. Database not initialized")
    print("4. Multi-agent system timeout (try again)")
