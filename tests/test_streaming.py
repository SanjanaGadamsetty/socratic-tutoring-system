"""
Test SSE streaming endpoint.
Watch the agent think in real-time!
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TESTING SSE STREAMING")
print("=" * 60)

# Step 1: Start a session
print("\n[1] Starting session...")
response = requests.post(
    f"{BASE_URL}/sessions/start",
    json={"problem_id": 1, "student_id": "streaming_test"}
)
session_id = response.json()['session_id']
print(f"Session ID: {session_id}")

# Step 2: Submit answer with streaming
print("\n[2] Submitting answer with streaming...")
print("Watch the agent think in real-time:\n")

response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/turn/stream",
    json={"student_answer": "Maybe 100?"},
    stream=True  # Enable streaming
)

# Process SSE events
for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')

        # SSE format: "data: {json}"
        if line.startswith('data: '):
            data_str = line[6:]  # Remove "data: " prefix
            try:
                data = json.loads(data_str)
                event_type = data.get('type', 'unknown')

                if event_type == 'status':
                    print(f"[STATUS] {data['message']}")
                elif event_type == 'thinking':
                    print(f"[THINKING] {data['message']}")
                elif event_type == 'tool_call':
                    print(f"[TOOL CALL] {data['tool']}")
                    print(f"  Arguments: {data['arguments']}")
                elif event_type == 'tool_result':
                    print(f"[TOOL RESULT] {data['result']}")
                elif event_type == 'response':
                    print(f"\n[FINAL RESPONSE]")
                    print(f"{data['message']}")
                elif event_type == 'complete':
                    print(f"\n[COMPLETE]")
                    print(f"Session ID: {data.get('session_id')}")
                    print(f"Is Correct: {data.get('is_correct')}")
                    print(f"Status: {data.get('session_status')}")
                elif event_type == 'error':
                    print(f"[ERROR] {data['message']}")

            except json.JSONDecodeError:
                pass

print("\n" + "=" * 60)
print("STREAMING TEST COMPLETE!")
print("=" * 60)
