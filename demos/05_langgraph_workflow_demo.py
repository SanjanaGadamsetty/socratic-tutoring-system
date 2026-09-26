"""
DEMO 5: LANGGRAPH STATE MACHINE (Day 5 Requirement)

What to explain in video:
- LangGraph = State machine framework
- Turns imperative code into declarative workflow
- Nodes = processing steps
- Edges = flow between steps
- Visual workflow representation
- Industry standard pattern

Time: 4-5 minutes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.workflow import create_tutoring_workflow

print("=" * 70)
print("DEMO 5: LANGGRAPH STATE MACHINE")
print("=" * 70)

print("\n[WHAT IS LANGGRAPH?]")
print("")
print("Traditional approach (Day 1-4):")
print("  for i in range(3):")
print("      response = tutor.generate()")
print("      verdict = verifier.check()")
print("      if verdict == APPROVE:")
print("          return response")
print("")
print("LangGraph approach (Day 5):")
print("  graph.add_node('tutor', tutor_fn)")
print("  graph.add_node('verifier', verifier_fn)")
print("  graph.add_conditional_edges(...)")
print("  result = graph.invoke(state)")

print("\n[BENEFITS OF LANGGRAPH]")
print("1. Declarative - Define WHAT, not HOW")
print("2. Visual - Can export as diagram")
print("3. Debuggable - See which node failed")
print("4. Resumable - Save/load workflow state")
print("5. Professional - Used in production systems")

print("\n[OUR WORKFLOW]")
print("")
print("Nodes (processing steps):")
print("  1. tutor_node - Generate Socratic question")
print("  2. verifier_node - Check for answer leaks")
print("  3. decision_node - Finalize if approved")
print("  4. fallback_node - Safe response if all fail")
print("")
print("Edges (flow):")
print("  START -> tutor_node")
print("  tutor_node -> verifier_node")
print("  verifier_node -> (conditional)")
print("    if APPROVED -> decision_node -> END")
print("    if REJECTED and retries left -> tutor_node")
print("    if REJECTED and no retries -> fallback_node -> END")

input("\nPress ENTER to create and run the workflow...")

print("\n" + "=" * 70)
print("CREATING LANGGRAPH WORKFLOW...")
print("=" * 70)

workflow = create_tutoring_workflow(max_retries=3)
print("✓ Workflow compiled successfully")
print("✓ State machine configured")
print("✓ Nodes registered")
print("✓ Edges defined")

print("\n" + "=" * 70)
print("PREPARING STATE...")
print("=" * 70)

initial_state = {
    "problem_text": "What is 18 + 7?",
    "correct_answer": "25",
    "student_response": "I don't know",
    "conversation_history": "",
    "tutor_response": "",
    "verification_result": {},
    "attempt_count": 0,
    "max_retries": 3,
    "final_response": "",
    "success": False,
    "verifications": []
}

print("\nInitial state prepared:")
print(f"  Problem: {initial_state['problem_text']}")
print(f"  Answer: {initial_state['correct_answer']} (hidden from student)")
print(f"  Student: '{initial_state['student_response']}'")

input("\nPress ENTER to invoke the workflow...")

print("\n" + "=" * 70)
print("WORKFLOW EXECUTION (Watch the state flow through nodes)...")
print("=" * 70)

result = workflow.invoke(initial_state)

print("\n" + "=" * 70)
print("WORKFLOW COMPLETE - FINAL STATE")
print("=" * 70)

print(f"\nFinal response: '{result['final_response']}'")
print(f"Success: {result['success']}")
print(f"Attempts: {result['attempt_count']}")

print(f"\nState changes:")
for i, v in enumerate(result['verifications'], 1):
    print(f"\n  Cycle {i}:")
    print(f"    State entered tutor_node")
    print(f"    State entered verifier_node")
    print(f"    Decision: {v['verification']['decision']}")
    if v['verification']['decision'] == 'APPROVE':
        print(f"    State entered decision_node")
        print(f"    State reached END")
    else:
        print(f"    State loops back to tutor_node")

print("\n" + "=" * 70)
print("KEY POINTS TO EXPLAIN:")
print("=" * 70)
print("1. State flows through nodes automatically")
print("2. Conditional routing based on verifier decision")
print("3. Loops back for retries")
print("4. Much cleaner than manual if/else loops")
print("5. Can visualize as flowchart (draw.io or mermaid)")

print("\n[COMPARISON]")
print("")
print("Manual (Day 4):")
print("  - 50+ lines of control flow")
print("  - Hard to visualize")
print("  - Hard to debug")
print("")
print("LangGraph (Day 5):")
print("  - Declarative node/edge definitions")
print("  - Visual representation")
print("  - Easy to debug (see which node)")
print("  - Professional pattern")

print("\n[SUCCESS] LangGraph workflow demo complete!")
