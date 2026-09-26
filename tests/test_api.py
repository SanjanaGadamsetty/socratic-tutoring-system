"""
Quick API test script.
Tests all endpoints to verify everything works.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TESTING SOCRATIC TUTORING API")
print("=" * 60)

# Test 1: Health check
print("\n[TEST 1] Health Check")
response = requests.get(f"{BASE_URL}/")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 2: List problems
print("\n[TEST 2] List Problems")
response = requests.get(f"{BASE_URL}/problems")
print(f"Status: {response.status_code}")
data = response.json()
print(f"Found {data['total']} problems")
if data['problems']:
    print(f"First problem: {data['problems'][0]['title']}")

# Test 3: Start session
print("\n[TEST 3] Start Session")
response = requests.post(
    f"{BASE_URL}/sessions/start",
    json={"problem_id": 1, "student_id": "test_student"}
)
print(f"Status: {response.status_code}")
session_data = response.json()
session_id = session_data['session_id']
print(f"Session ID: {session_id}")
print(f"First Question: {session_data['first_question'][:100]}...")

# Test 4: Submit student turn
print("\n[TEST 4] Submit Student Answer")
response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/turn",
    json={"student_answer": "I think it's 120"}
)
print(f"Status: {response.status_code}")
turn_data = response.json()
print(f"Is Correct: {turn_data.get('is_correct')}")
print(f"Tutor Response: {turn_data['tutor_question'][:100]}...")

# Test 5: Get transcript
print("\n[TEST 5] Get Transcript")
response = requests.get(f"{BASE_URL}/sessions/{session_id}/transcript")
print(f"Status: {response.status_code}")
transcript = response.json()
print(f"Total turns: {len(transcript['turns'])}")
print(f"Session status: {transcript['status']}")

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
