"""
DEMO 1: HAPPY PATH - Normal Successful Run

What to explain in video:
- This shows the normal flow when everything works correctly
- Student asks a question
- Tutor generates a Socratic question (guiding, not revealing)
- Verifier checks and approves on first attempt
- Student gets quality-controlled response

Time: 2-3 minutes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.handoff import HandoffController

print("=" * 70)
print("DEMO 1: HAPPY PATH - Normal Successful Run")
print("=" * 70)

print("\n[SETUP]")
print("Problem: What is 12 + 8?")
print("Correct Answer: 20 (tutor must NOT reveal this)")
print("Student Input: 'I don't know how to add these numbers'")

print("\n[WHAT WILL HAPPEN]")
print("1. Student question goes to Tutor Agent")
print("2. Tutor generates a Socratic question (asks, doesn't tell)")
print("3. Verifier Agent checks: 'Did tutor leak the answer?'")
print("4. If good -> Approve and send to student")
print("5. If bad -> Reject and tutor tries again")

input("\nPress ENTER to run the demo...")

print("\n" + "=" * 70)
print("RUNNING MULTI-AGENT SYSTEM...")
print("=" * 70)

controller = HandoffController(max_retries=3)

result = controller.process_student_input(
    student_response="I don't know how to add these numbers",
    conversation_history="",
    problem_text="What is 12 + 8?",
    correct_answer="20"
)

print("\n" + "=" * 70)
print("FINAL RESULT")
print("=" * 70)

print(f"\nTutor's Response to Student:")
print(f"  '{result['tutor_response']}'")

print(f"\nMetrics:")
print(f"  Success: {result['success']}")
print(f"  Attempts Needed: {result['attempts']}")
print(f"  Final Verdict: {result['final_verdict']}")

print(f"\nVerification Details:")
for i, v in enumerate(result['verifications'], 1):
    print(f"\n  Attempt {i}:")
    print(f"    Tutor said: {v['tutor_response'][:60]}...")
    print(f"    Verifier decision: {v['verification']['decision']}")
    print(f"    Reason: {v['verification']['reason']}")

print("\n" + "=" * 70)
print("KEY POINTS TO EXPLAIN:")
print("=" * 70)
print("1. Tutor asked a QUESTION, not gave an answer")
print("2. Verifier checked and approved")
print("3. Student learns through guidance, not direct answers")
print("4. This is the Socratic method in action!")

print("\n[SUCCESS] Happy path demo complete!")
