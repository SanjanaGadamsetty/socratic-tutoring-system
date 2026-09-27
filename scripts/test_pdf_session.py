"""
Quick test to verify PDF session creation and first question
"""
import requests

API_BASE = "http://localhost:8000"

# First, check if there are any PDFs
print("Checking for PDFs...")
response = requests.get(f"{API_BASE}/pdfs")
if response.status_code == 200:
    pdfs = response.json()
    print(f"Found {len(pdfs)} PDFs")
    if pdfs:
        pdf_id = pdfs[0]["id"]
        print(f"Using PDF ID: {pdf_id}")

        # Try to start a session
        print("\nStarting PDF session...")
        session_data = {
            "pdf_document_id": pdf_id,
            "student_id": "test_student"
        }

        response = requests.post(f"{API_BASE}/sessions/start", json=session_data)
        print(f"Status: {response.status_code}")

        if response.status_code == 201:
            session = response.json()
            print(f"Session ID: {session['session_id']}")
            print(f"First question: {session.get('first_question', 'NO FIRST QUESTION!')}")

            # Now get the transcript
            print("\nGetting transcript...")
            transcript_response = requests.get(f"{API_BASE}/sessions/{session['session_id']}/transcript")
            if transcript_response.status_code == 200:
                transcript = transcript_response.json()
                print(f"Turns: {len(transcript.get('turns', []))}")
                for turn in transcript.get('turns', []):
                    print(f"  - {turn['speaker']}: {turn['message'][:50]}...")
        else:
            print(f"Error: {response.text}")
else:
    print("No PDFs found or error accessing API")
    print("Please upload a PDF first at http://localhost:8000/docs")
