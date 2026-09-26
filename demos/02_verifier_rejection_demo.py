"""
DEMO 2: VERIFIER REJECTION & RETRY

What to explain in video:
- This shows what happens when tutor makes a mistake
- Verifier catches answer leaks
- System retries with feedback
- Eventually gets it right

Note: Due to LLM quality, tutor usually gets it right first time.
This demo explains how the retry mechanism WOULD work.

Time: 3-4 minutes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.handoff import HandoffController

print("=" * 70)
print("DEMO 2: VERIFIER REJECTION & RETRY MECHANISM")
print("=" * 70)

print("\n[CONCEPT EXPLANATION]")
print("Without verifier:")
print("  Tutor -> Student")
print("  Problem: Tutor might accidentally reveal answer!")
print("")
print("With verifier (our system):")
print("  Tutor -> Verifier -> (checks) -> Student")
print("  If bad: Verifier rejects, tutor tries again")
print("  If good: Verifier approves, send to student")

print("\n[HOW RETRY WORKS]")
print("Attempt 1: Tutor generates response")
print("         -> Verifier: 'You revealed the answer!' -> REJECT")
print("Attempt 2: Tutor tries again (knows why rejected)")
print("         -> Verifier: 'Still showing answer!' -> REJECT")
print("Attempt 3: Tutor is extra careful")
print("         -> Verifier: 'Good, no leaks!' -> APPROVE")

print("\n[ACTUAL RUN]")
input("Press ENTER to see how the system handles this...")

print("\n" + "=" * 70)
print("RUNNING WITH RETRY MECHANISM...")
print("=" * 70)

controller = HandoffController(max_retries=3)

result = controller.process_student_input(
    student_response="What's the answer?",
    conversation_history="",
    problem_text="What is 15 multiplied by 8?",
    correct_answer="120"
)

print("\n" + "=" * 70)
print("RETRY HISTORY")
print("=" * 70)

print(f"\nTotal attempts made: {result['attempts']}")
print(f"Final verdict: {result['final_verdict']}")

for i, v in enumerate(result['verifications'], 1):
    print(f"\n--- Attempt {i} ---")
    print(f"Tutor's draft: {v['tutor_response'][:80]}...")
    print(f"Verifier decision: {v['verification']['decision']}")
    print(f"Verifier's reason: {v['verification']['reason'][:100]}...")

    if v['verification']['decision'] == 'REJECT':
        print("-> System will retry with this feedback")
    else:
        print("-> APPROVED! Sending to student")

print("\n" + "=" * 70)
print("KEY POINTS TO EXPLAIN:")
print("=" * 70)
print("1. Verifier acts as QUALITY CONTROL")
print("2. System doesn't give up after one rejection")
print("3. Each retry includes feedback from previous rejection")
print("4. Max 3 attempts before using safe fallback")
print("5. This prevents answer leaking in production!")

print("\n[SUCCESS] Retry mechanism demo complete!")
