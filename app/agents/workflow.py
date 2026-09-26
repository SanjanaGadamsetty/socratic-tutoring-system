"""
LangGraph Workflow - State machine for tutor-verifier handoff.

This uses LangGraph to create a declarative state machine that
manages the multi-agent workflow visually and with better state tracking.
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from app.agents.tutor_agent import TutorAgent
from app.agents.verifier_agent import VerifierAgent


# Define state that flows through the graph
class TutoringState(TypedDict):
    """
    State that flows through the LangGraph workflow.
    """
    # Input
    problem_text: str
    correct_answer: str
    student_response: str
    conversation_history: str

    # Working state
    tutor_response: str
    verification_result: dict
    attempt_count: int
    max_retries: int

    # Output
    final_response: str
    success: bool
    verifications: list


def create_tutoring_workflow(max_retries: int = 3):
    """
    Create LangGraph workflow for tutor-verifier handoff.

    Flow:
        START -> tutor_node -> verifier_node -> decision
            |                                      |
            |                                      v
            |                            approved? YES -> END
            |                                      |
            |                                     NO
            |                                      |
            |                                  retry? YES -> tutor_node
            |                                      |
            |                                     NO
            +------------------------------------> fallback -> END
    """

    # Initialize agents
    tutor = TutorAgent()
    verifier = VerifierAgent()

    # Define nodes
    def tutor_node(state: TutoringState) -> TutoringState:
        """
        Tutor generates Socratic response.
        """
        print(f"\n[TUTOR NODE] Attempt {state['attempt_count'] + 1}/{state['max_retries']}")

        context = {
            "problem_text": state["problem_text"],
            "correct_answer": state["correct_answer"],
            "student_last_response": state["student_response"],
            "conversation_history": state["conversation_history"]
        }

        response = tutor.generate_response(context)
        print(f"[TUTOR] Generated: {response[:80]}...")

        state["tutor_response"] = response
        state["attempt_count"] += 1

        return state

    def verifier_node(state: TutoringState) -> TutoringState:
        """
        Verifier checks tutor's response.
        """
        print("[VERIFIER NODE] Checking response...")

        verification = verifier.verify(
            tutor_response=state["tutor_response"],
            problem_text=state["problem_text"],
            correct_answer=state["correct_answer"]
        )

        print(f"[VERIFIER] Decision: {verification['decision']}")

        state["verification_result"] = verification

        # Track all verifications
        state["verifications"].append({
            "attempt": state["attempt_count"],
            "tutor_response": state["tutor_response"],
            "verification": verification
        })

        return state

    def fallback_node(state: TutoringState) -> TutoringState:
        """
        Generate safe fallback when all retries fail.
        """
        print("[FALLBACK NODE] All retries failed, using fallback")

        state["final_response"] = "Let's break this down step by step. What information do you have, and what are you trying to find?"
        state["success"] = False

        return state

    def decision_node(state: TutoringState) -> TutoringState:
        """
        Final decision node - sets final response if approved.
        """
        print("[DECISION NODE] Finalizing...")

        if state["verification_result"]["decision"] == "APPROVE":
            state["final_response"] = state["tutor_response"]
            state["success"] = True

        return state

    # Define routing logic
    def should_retry(state: TutoringState) -> Literal["retry", "fallback", "end"]:
        """
        Decide whether to retry, use fallback, or end.
        """
        verification = state["verification_result"]

        if verification["decision"] == "APPROVE":
            return "end"

        if state["attempt_count"] < state["max_retries"]:
            # Add rejection feedback to history for next attempt
            state["conversation_history"] += f"\n[REJECTED: {verification['reason']}]"
            return "retry"

        return "fallback"

    # Build the graph
    workflow = StateGraph(TutoringState)

    # Add nodes
    workflow.add_node("tutor", tutor_node)
    workflow.add_node("verifier", verifier_node)
    workflow.add_node("fallback", fallback_node)
    workflow.add_node("decision", decision_node)

    # Add edges
    workflow.set_entry_point("tutor")  # Start with tutor
    workflow.add_edge("tutor", "verifier")  # Tutor always goes to verifier

    # Conditional routing from verifier
    workflow.add_conditional_edges(
        "verifier",
        should_retry,
        {
            "retry": "tutor",      # Rejected but can retry
            "fallback": "fallback", # Max retries reached
            "end": "decision"       # Approved
        }
    )

    # Final edges
    workflow.add_edge("decision", END)
    workflow.add_edge("fallback", END)

    # Compile the graph
    app = workflow.compile()

    return app


# ===== EXPLANATION =====

"""
WHAT IS LANGGRAPH?

LangGraph = State machine framework for AI workflows

Think of it like a flowchart that executes:
    [Node 1] -> [Node 2] -> Decision -> [Node 3] or [Node 4]

VS manual if/else loops:
    Manual: You write all the control flow
    LangGraph: You define nodes and edges, it handles flow

KEY CONCEPTS:

1. STATE (TypedDict):
    Data that flows through the graph
    Each node can read and modify state
    State persists across the entire workflow

2. NODES (Functions):
    def tutor_node(state):
        # Do something
        state["key"] = value
        return state

    Each node is a processing step

3. EDGES (Connections):
    Simple edge: A always goes to B
        workflow.add_edge("A", "B")

    Conditional edge: A goes to B or C based on logic
        workflow.add_conditional_edges("A", decision_func, {...})

4. GRAPH:
    Defines the entire workflow
    Can be visualized (draws the flowchart!)
    Can be saved/loaded (persistent workflows)

OUR WORKFLOW:

    START
      |
      v
    +-------+
    | Tutor |
    +-------+
      |
      v
    +---------+
    |Verifier |
    +---------+
      |
      v
    Decision: Approved?
      |
      +-- YES -> [Decision Node] -> END
      |
      +-- NO -> Retry?
                  |
                  +-- YES -> [Tutor] (loop back)
                  |
                  +-- NO -> [Fallback] -> END

BENEFITS:

1. Visual:
    Can export graph as image
    See the workflow visually

2. Debuggable:
    See which node failed
    Track state at each step

3. Resumable:
    Save state mid-workflow
    Resume from checkpoint

4. Testable:
    Test individual nodes
    Test edge conditions

5. Professional:
    Industry standard pattern
    Used in production systems

COMPARISON:

Day 4 (Manual):
    for i in range(3):
        response = tutor.generate()
        verdict = verifier.check()
        if verdict == "APPROVE":
            return response
    return fallback()

    (Imperative - you control everything)

Day 5 (LangGraph):
    graph.add_node("tutor", tutor_node)
    graph.add_node("verifier", verifier_node)
    graph.add_conditional_edges(...)

    app = graph.compile()
    result = app.invoke(initial_state)

    (Declarative - you define structure, graph handles execution)

WHEN TO USE LANGGRAPH:

Use when:
- Complex multi-step workflows
- Need to visualize flow
- Want to save/resume workflows
- Multiple decision points
- Production systems

Don't need when:
- Simple linear flow
- One-shot operations
- Prototyping

Our case: Multi-agent with retry logic = PERFECT for LangGraph
"""
