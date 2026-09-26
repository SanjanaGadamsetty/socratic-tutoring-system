"""
Day 5 Test: LangGraph Workflow

Tests the state machine implementation of tutor-verifier handoff.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.workflow import create_tutoring_workflow

print("=" * 60)
print("DAY 5: LANGGRAPH WORKFLOW TEST")
print("=" * 60)

# Create workflow
print("\n[1/3] Creating LangGraph workflow...")
workflow = create_tutoring_workflow(max_retries=3)
print("Workflow compiled successfully!")

# Prepare initial state
print("\n[2/3] Preparing initial state...")
initial_state = {
    "problem_text": "What is 15 multiplied by 8?",
    "correct_answer": "120",
    "student_response": "I don't know where to start",
    "conversation_history": "",
    "tutor_response": "",
    "verification_result": {},
    "attempt_count": 0,
    "max_retries": 3,
    "final_response": "",
    "success": False,
    "verifications": []
}

print("Initial state ready")

# Run workflow
print("\n[3/3] Running workflow through state machine...")
print("=" * 60)

result = workflow.invoke(initial_state)

# Display results
print("\n" + "=" * 60)
print("WORKFLOW RESULTS")
print("=" * 60)

print(f"\nFinal Response:")
print(f"  {result['final_response']}")

print(f"\nWorkflow Metrics:")
print(f"  Total Attempts: {result['attempt_count']}")
print(f"  Success: {result['success']}")
print(f"  Verifications Performed: {len(result['verifications'])}")

print(f"\nVerification History:")
for v in result['verifications']:
    print(f"\n  Attempt {v['attempt']}:")
    print(f"    Decision: {v['verification']['decision']}")
    print(f"    Reason: {v['verification']['reason']}")

print("\n" + "=" * 60)
print("LANGGRAPH ADVANTAGES DEMONSTRATED")
print("=" * 60)
print("1. State Machine - Declarative workflow definition")
print("2. Visual Flow - Can export graph diagram")
print("3. State Tracking - Complete state history")
print("4. Resumable - Can save/load workflow state")
print("5. Professional - Production-ready pattern")

print("\n" + "=" * 60)
print("DAY 5 LANGGRAPH TEST COMPLETE")
print("=" * 60)
