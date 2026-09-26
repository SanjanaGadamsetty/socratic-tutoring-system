"""
Day 4 Test: Multi-Agent System

This demonstrates:
1. Tutor agent generating Socratic questions
2. Verifier agent checking for answer leaks
3. Handoff pattern with retry loop
4. Quality-controlled output
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.handoff import HandoffController

print("=" * 60)
print("DAY 4: MULTI-AGENT SYSTEM TEST")
print("=" * 60)

# Initialize handoff controller
controller = HandoffController(max_retries=3)

# Test scenario
problem = "What is 15 multiplied by 8?"
correct_answer = "120"
student_input = "I'm not sure how to start"

print("\n" + "=" * 60)
print("TEST SCENARIO")
print("=" * 60)
print(f"Problem: {problem}")
print(f"Correct Answer: {correct_answer} (hidden from student)")
print(f"Student said: {student_input}")

# Process through multi-agent system
print("\n" + "=" * 60)
print("PROCESSING THROUGH MULTI-AGENT SYSTEM")
print("=" * 60)

result = controller.process_student_input(
    problem_text=problem,
    correct_answer=correct_answer,
    student_response=student_input,
    conversation_history=""
)

# Display results
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)

print(f"\nFinal Response to Student:")
print(f"  {result['tutor_response']}")

print(f"\nNumber of Attempts: {result['attempts']}")
print(f"Success: {result['success']}")
print(f"Final Verdict: {result['final_verdict']}")

print(f"\nDetailed Verification History:")
for v in result['verifications']:
    print(f"\n  Attempt {v['attempt']}:")
    print(f"    Tutor said: {v['tutor_response'][:80]}...")
    print(f"    Verifier: {v['verification']['decision']}")
    print(f"    Reason: {v['verification']['reason']}")

print("\n" + "=" * 60)
print("KEY FEATURES DEMONSTRATED")
print("=" * 60)
print("1. Tutor Agent - Generates Socratic questions")
print("2. Verifier Agent - Checks for answer leaks")
print("3. Handoff Pattern - Tutor -> Verifier -> Retry loop")
print("4. Quality Control - Only approved responses sent")
print("5. LangChain Framework - Modern AI agent architecture")

print("\n" + "=" * 60)
print("DAY 4 TEST COMPLETE")
print("=" * 60)
