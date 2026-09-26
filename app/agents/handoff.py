"""
Handoff Controller - Orchestrates tutor and verifier agents.

This coordinates the multi-agent workflow:
1. Tutor generates response
2. Verifier checks response
3. If rejected, tutor tries again (max 3 attempts)
4. If approved, send to student
"""

from typing import Dict, Any, List
from app.agents.tutor_agent import TutorAgent
from app.agents.verifier_agent import VerifierAgent


class HandoffController:
    """
    Manages the tutor-verifier handoff pattern.

    Flow:
        Student input
            |
            v
        Tutor drafts response
            |
            v
        Verifier checks draft
            |
            v
        Approved? -> Send to student
        Rejected? -> Tutor retries (max 3 times)
    """

    def __init__(self, max_retries: int = 3):
        """
        Initialize handoff controller.

        Args:
            max_retries: Maximum number of tutor retry attempts
        """
        self.tutor = TutorAgent()
        self.verifier = VerifierAgent()
        self.max_retries = max_retries

        print(f"[HandoffController] Initialized with max {max_retries} retries")

    def process_student_input(
        self,
        problem_text: str,
        correct_answer: str,
        student_response: str,
        conversation_history: str = ""
    ) -> Dict[str, Any]:
        """
        Process student input through tutor-verifier loop.

        Args:
            problem_text: The problem being solved
            correct_answer: The correct answer (not shown to student)
            student_response: What the student just said
            conversation_history: Previous conversation turns

        Returns:
            Dictionary with:
                - tutor_response: Final approved response
                - attempts: How many tries it took
                - verifications: List of all verification results
                - success: True if approved, False if all retries failed
        """
        verifications = []
        tutor_response = None

        print("\n" + "="*60)
        print("[HandoffController] Starting tutor-verifier loop")
        print("="*60)

        # Build context for tutor
        context = {
            "problem_text": problem_text,
            "correct_answer": correct_answer,
            "student_last_response": student_response,
            "conversation_history": conversation_history
        }

        # Retry loop
        for attempt in range(1, self.max_retries + 1):
            print(f"\n--- Attempt {attempt}/{self.max_retries} ---")

            # STEP 1: Tutor generates response
            print("[1/2] Tutor generating response...")
            tutor_response = self.tutor.generate_response(context)
            print(f"[Tutor] {tutor_response[:100]}...")

            # STEP 2: Verifier checks response
            print("\n[2/2] Verifier checking response...")
            verification = self.verifier.verify(
                tutor_response=tutor_response,
                problem_text=problem_text,
                correct_answer=correct_answer
            )

            verifications.append({
                "attempt": attempt,
                "tutor_response": tutor_response,
                "verification": verification
            })

            # STEP 3: Decision
            if verification["decision"] == "APPROVE":
                print(f"[Verifier] APPROVED")
                print(f"[HandoffController] Success on attempt {attempt}")
                return {
                    "tutor_response": tutor_response,
                    "attempts": attempt,
                    "verifications": verifications,
                    "success": True,
                    "final_verdict": "APPROVED"
                }
            else:
                print(f"[Verifier] REJECTED: {verification['reason']}")

                if attempt < self.max_retries:
                    print(f"[HandoffController] Tutor will retry...")

                    # Add rejection feedback to context for next attempt
                    context["conversation_history"] += f"\n\n[INTERNAL - Previous attempt rejected: {verification['reason']}]"
                else:
                    print(f"[HandoffController] Max retries reached")

        # All retries failed - return fallback
        print("\n[HandoffController] All retries failed, using fallback")
        fallback_response = self._generate_fallback(problem_text)

        return {
            "tutor_response": fallback_response,
            "attempts": self.max_retries,
            "verifications": verifications,
            "success": False,
            "final_verdict": "FALLBACK_USED"
        }

    def _generate_fallback(self, problem_text: str) -> str:
        """
        Generate a safe fallback response when all retries fail.

        This is a generic hint that doesn't reveal the answer.
        """
        return f"Let's approach this step by step. Can you identify what information you have and what you're trying to find?"


# ===== EXPLANATION =====

"""
HANDOFF PATTERN EXPLAINED:

This is the CORE of the multi-agent system!

FLOW DIAGRAM:

    Student Input
        |
        v
    +-------------------+
    | Attempt 1         |
    +-------------------+
        |
        | Tutor generates
        v
    "The answer is 120"
        |
        | Verifier checks
        v
    REJECT: "Answer revealed"
        |
        v
    +-------------------+
    | Attempt 2         |
    +-------------------+
        |
        | Tutor generates (with rejection feedback)
        v
    "15 × 8 = 120"
        |
        | Verifier checks
        v
    REJECT: "Still shows answer"
        |
        v
    +-------------------+
    | Attempt 3         |
    +-------------------+
        |
        | Tutor generates (with both rejections)
        v
    "Can you break 15 into 10 + 5?"
        |
        | Verifier checks
        v
    APPROVE: "No answer revealed"
        |
        v
    Send to student

KEY FEATURES:

1. RETRY LOOP:
    for attempt in range(1, max_retries + 1):
        response = tutor.generate()
        verdict = verifier.verify(response)
        if verdict == APPROVE:
            return response
        else:
            # Try again

2. FEEDBACK TO TUTOR:
    After rejection, tutor gets:
        "[Previous attempt rejected: Answer revealed]"

    This helps tutor learn and adjust next attempt

3. BOUNDED RETRIES:
    Max 3 attempts
    Prevents infinite loop
    After 3 failures -> fallback response

4. TRACKING:
    verifications list stores:
        - Each attempt
        - What tutor said
        - What verifier decided
        - Why rejected

    This creates an audit trail!

WHAT HAPPENS IN EACH ATTEMPT:

Attempt 1 (Fresh):
    Tutor: Generates based on problem + student input
    Context: Just the basics

Attempt 2 (After rejection):
    Tutor: Knows previous attempt was rejected
    Context: Includes rejection reason
    Tutor adapts: "I revealed the answer, let me be more careful"

Attempt 3 (After 2 rejections):
    Tutor: Knows both attempts failed
    Context: Both rejection reasons
    Tutor adapts: "I need to be much more indirect"

FALLBACK RESPONSE:

If all 3 attempts rejected:
    return generic_safe_hint()

Why?
    Better to give generic hint than:
        - Reveal answer (defeats purpose)
        - Give no response (bad UX)
        - Crash (terrible)

Generic hint examples:
    "Let's break this down step by step"
    "What information do you have?"
    "Can you identify what you're trying to find?"

These are ALWAYS safe (never reveal answer)

RETURN VALUE:

{
    "tutor_response": "Can you break 15 into 10 + 5?",
    "attempts": 3,
    "verifications": [
        {
            "attempt": 1,
            "tutor_response": "The answer is 120",
            "verification": {"decision": "REJECT", "reason": "..."}
        },
        {
            "attempt": 2,
            "tutor_response": "15 × 8 = 120",
            "verification": {"decision": "REJECT", "reason": "..."}
        },
        {
            "attempt": 3,
            "tutor_response": "Can you break 15 into 10 + 5?",
            "verification": {"decision": "APPROVE", "reason": "..."}
        }
    ],
    "success": True,
    "final_verdict": "APPROVED"
}

This detailed return lets us:
- Save to database (verifier_flags table)
- Show in UI (transparency)
- Debug issues
- Prove system works

COMPARISON TO SINGLE AGENT:

Single Agent (Day 1-3):
    agent.generate(input)
    -> Returns response
    -> No quality check
    -> Might leak answer

Multi-Agent (Day 4):
    handoff.process(input)
    -> Tutor drafts
    -> Verifier checks
    -> Retry if needed
    -> Quality guaranteed

This is REAL AI engineering!
"""
