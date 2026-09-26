"""
DEMO 4: MULTI-AGENT ARCHITECTURE EXPLAINED

What to explain in video:
- System has TWO agents working together
- Tutor Agent: Generates Socratic questions
- Verifier Agent: Quality control
- HandoffController: Orchestrates them
- This is the CORE of your project!

Time: 4-5 minutes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.tutor_agent import TutorAgent
from app.agents.verifier_agent import VerifierAgent
from app.agents.handoff import HandoffController

print("=" * 70)
print("DEMO 4: MULTI-AGENT ARCHITECTURE")
print("=" * 70)

print("\n[SINGLE AGENT VS MULTI-AGENT]")
print("")
print("Traditional AI tutor (single agent):")
print("  Student -> AI -> Response")
print("  Problem: Might reveal answers accidentally!")
print("")
print("Our multi-agent system:")
print("  Student -> Tutor (draft) -> Verifier (check) -> Response")
print("  Benefit: Quality control prevents answer leaking!")

print("\n[THE THREE COMPONENTS]")
print("")
print("1. TUTOR AGENT")
print("   - Role: Generate Socratic questions")
print("   - Model: OpenAI GPT via Groq")
print("   - Temperature: 0.7 (creative)")
print("   - Input: Problem + student response + history")
print("   - Output: Guiding question (not answer)")
print("")
print("2. VERIFIER AGENT")
print("   - Role: Check for answer leaks")
print("   - Model: Same LLM")
print("   - Temperature: 0.3 (consistent)")
print("   - Input: Tutor's draft + correct answer")
print("   - Output: APPROVE or REJECT + reason")
print("")
print("3. HANDOFF CONTROLLER")
print("   - Role: Orchestrate tutor <-> verifier")
print("   - Logic: Retry loop with feedback")
print("   - Max retries: 3")
print("   - Fallback: Safe generic question")

input("\nPress ENTER to see components in action...")

print("\n" + "=" * 70)
print("INITIALIZING AGENTS...")
print("=" * 70)

print("\n[1/3] Creating Tutor Agent...")
tutor = TutorAgent()

print("\n[2/3] Creating Verifier Agent...")
verifier = VerifierAgent()

print("\n[3/3] Creating Handoff Controller...")
controller = HandoffController(max_retries=3)

print("\n" + "=" * 70)
print("DEMONSTRATING HANDOFF PATTERN...")
print("=" * 70)

problem = "What is 25 times 4?"
correct_answer = "100"
student_input = "I'm not sure how to solve this"

print(f"\nProblem: {problem}")
print(f"Correct Answer: {correct_answer} (tutor must not reveal)")
print(f"Student Says: '{student_input}'")

input("\nPress ENTER to watch the handoff...")

print("\n[HANDOFF IN ACTION]")
print("-" * 70)

result = controller.process_student_input(
    student_response=student_input,
    conversation_history="",
    problem_text=problem,
    correct_answer=correct_answer
)

print("\n" + "=" * 70)
print("HANDOFF COMPLETE - ANALYZING FLOW")
print("=" * 70)

print(f"\nAttempts made: {result['attempts']}")
print(f"Final verdict: {result['final_verdict']}")

print("\nWhat happened at each step:")
for i, v in enumerate(result['verifications'], 1):
    print(f"\n  Step {i}:")
    print(f"    -> Tutor generated: '{v['tutor_response'][:60]}...'")
    print(f"    -> Verifier decided: {v['verification']['decision']}")
    print(f"    -> Reason: {v['verification']['reason'][:80]}...")

    if v['verification']['decision'] == 'APPROVE':
        print(f"    -> ✓ Approved! Sending to student")
    else:
        print(f"    -> ✗ Rejected! Tutor will retry")

print(f"\nFinal response to student:")
print(f"  '{result['tutor_response']}'")

print("\n" + "=" * 70)
print("KEY POINTS TO EXPLAIN:")
print("=" * 70)
print("1. TWO AI agents, not one")
print("2. Separation of concerns:")
print("   - Tutor focuses on teaching")
print("   - Verifier focuses on quality")
print("3. HandoffController orchestrates them")
print("4. Retry loop with feedback")
print("5. This is ADVANCED AI architecture!")

print("\n" + "=" * 70)
print("WHY MULTI-AGENT?")
print("=" * 70)
print("- Single agent can make mistakes")
print("- Verifier adds quality control layer")
print("- Catches problems before reaching student")
print("- Industry pattern (used in production AI systems)")
print("- Your project requirement: Multi-agent system ✓")

print("\n[SUCCESS] Multi-agent architecture demo complete!")
