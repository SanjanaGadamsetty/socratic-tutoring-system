"""
Quick Backend Connection Test

Run this to check if backend is accessible.
"""

import requests
import sys

def test_connection():
    print("="*60)
    print("BACKEND CONNECTION TEST")
    print("="*60)
    print()

    # Test 1: Root endpoint
    print("[1/4] Testing root endpoint...")
    try:
        r = requests.get("http://localhost:8000", timeout=5)
        print(f"    SUCCESS: {r.status_code}")
        print(f"    Response: {r.json()}")
    except requests.exceptions.ConnectionError:
        print("    FAILED: Cannot connect to backend")
        print("    Backend is NOT running or blocked by firewall")
        print()
        print("FIX: Start backend with:")
        print("    python -m uvicorn app.api.main:app --reload")
        return False
    except Exception as e:
        print(f"    FAILED: {e}")
        return False

    print()

    # Test 2: Problems endpoint
    print("[2/4] Testing /problems endpoint...")
    try:
        r = requests.get("http://localhost:8000/problems", timeout=5)
        print(f"    SUCCESS: {r.status_code}")
        data = r.json()
        print(f"    Found {data.get('total', 0)} problems")
    except Exception as e:
        print(f"    FAILED: {e}")

    print()

    # Test 3: Session start endpoint
    print("[3/4] Testing /sessions/start endpoint...")
    try:
        payload = {
            "problem_id": 1,
            "student_id": "test_student"
        }
        r = requests.post(
            "http://localhost:8000/sessions/start",
            json=payload,
            timeout=30  # Multi-agent system can be slow
        )
        print(f"    Status: {r.status_code}")
        if r.status_code == 201:
            print("    SUCCESS: Session started")
            data = r.json()
            print(f"    Session ID: {data.get('session_id')}")
            print(f"    First question: {data.get('first_question')[:80]}...")
        elif r.status_code == 404:
            print("    Problem ID 1 not found (this is OK, backend is working)")
        elif r.status_code == 500:
            print("    FAILED: Internal Server Error")
            print("    Backend crashed or multi-agent system failed")
            print("    Check backend terminal for error details")
        else:
            print(f"    Response: {r.text}")
    except requests.exceptions.Timeout:
        print("    FAILED: Request timed out after 30 seconds")
        print("    Multi-agent system is likely hanging")
        print("    Check GROQ_API_KEY in .env file")
    except Exception as e:
        print(f"    FAILED: {e}")

    print()

    # Test 4: CORS check
    print("[4/4] Checking CORS headers...")
    try:
        r = requests.options("http://localhost:8000/problems")
        cors_header = r.headers.get('Access-Control-Allow-Origin', 'NOT SET')
        print(f"    CORS header: {cors_header}")
        if cors_header == '*':
            print("    SUCCESS: CORS is configured correctly")
        else:
            print("    WARNING: CORS might not be configured")
    except Exception as e:
        print(f"    FAILED: {e}")

    print()
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print()
    print("If all tests passed:")
    print("  Backend is running and accessible!")
    print("  Network error is likely in frontend code.")
    print()
    print("If connection test failed:")
    print("  Start backend: python -m uvicorn app.api.main:app --reload")
    print()
    print("If session start timed out:")
    print("  1. Check .env has GROQ_API_KEY set")
    print("  2. Check GROQ_API_KEY is valid")
    print("  3. Backend may be using fallback (check terminal)")
    print()

    return True

if __name__ == "__main__":
    test_connection()
