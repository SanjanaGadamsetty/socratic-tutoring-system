"""
Day 3 Test: Durable Execution

This test demonstrates:
1. Background job creation
2. Idempotency (duplicate prevention)
3. Job status polling
4. Worker processing
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("DAY 3: DURABLE EXECUTION TEST")
print("=" * 60)

# Test 1: Create a job
print("\n[TEST 1] Create background job")
response = requests.post(
    f"{BASE_URL}/jobs/sessions/start",
    json={"problem_id": 1, "student_id": "async_test"},
    headers={"X-Idempotency-Key": "test-key-123"}
)
print(f"Status: {response.status_code}")
job_data = response.json()
job_id = job_data['job_id']
print(f"Job ID: {job_id}")
print(f"Status: {job_data['status']}")

# Test 2: Idempotency - send same request again
print("\n[TEST 2] Test idempotency (send same request)")
response2 = requests.post(
    f"{BASE_URL}/jobs/sessions/start",
    json={"problem_id": 1, "student_id": "async_test"},
    headers={"X-Idempotency-Key": "test-key-123"}
)
job_data2 = response2.json()
print(f"Job ID: {job_data2['job_id']}")
print(f"Same job returned? {job_data2['job_id'] == job_id}")

# Test 3: Poll job status
print("\n[TEST 3] Poll job status (waiting for worker...)")
print("NOTE: Make sure worker is running in another terminal!")
print("Run: python app/worker.py\n")

max_polls = 30
for i in range(max_polls):
    response = requests.get(f"{BASE_URL}/jobs/{job_id}")
    status_data = response.json()

    print(f"Poll {i+1}: Status = {status_data['status']}", end="")

    if status_data['status'] == 'completed':
        print(" - DONE!")
        print(f"\nResult:")
        print(json.dumps(status_data['result'], indent=2))
        break
    elif status_data['status'] == 'failed':
        print(" - FAILED!")
        print(f"Error: {status_data['error']}")
        break
    elif status_data['status'] == 'running':
        print(" (agent is thinking...)")
    else:
        print()

    time.sleep(2)
else:
    print("\n\nTimeout waiting for job completion")
    print("Is the worker running? (python app/worker.py)")

# Test 4: List all jobs
print("\n[TEST 4] List all jobs")
response = requests.get(f"{BASE_URL}/jobs?limit=5")
jobs = response.json()
print(f"Found {len(jobs)} recent jobs:")
for job in jobs:
    print(f"  - Job {job['job_id']}: {job['job_type']} - {job['status']}")

print("\n" + "=" * 60)
print("DAY 3 TEST COMPLETE")
print("=" * 60)
print("\nKey features demonstrated:")
print("1. Async job creation (202 Accepted)")
print("2. Idempotency (duplicate prevention)")
print("3. Job status polling")
print("4. Background worker processing")
