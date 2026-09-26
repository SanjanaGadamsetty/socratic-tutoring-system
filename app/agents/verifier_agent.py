"""
Verifier Agent - Quality control for tutor responses.

This agent's job:
- Check if tutor revealed the answer
- Detect answer leaks (direct or indirect)
- Approve or reject tutor's draft
- Provide rejection reason
"""

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

load_dotenv()


class VerificationResult(BaseModel):
    """
    Structured output from verifier agent.
    """
    decision: str = Field(description="Either 'APPROVE' or 'REJECT'")
    reason: str = Field(description="Explanation for the decision")
    leaked_info: str = Field(default="", description="What information was leaked (if any)")


class VerifierAgent:
    """
    Verifies tutor responses don't leak answers.

    Uses:
    - ChatGroq as LLM
    - Structured output (Pydantic)
    - Focused prompt for answer leak detection
    """

    def __init__(self):
        """
        Initialize verifier agent.
        """
        # Initialize LLM
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.3,  # Lower temp for more consistent checking
            api_key=os.getenv("GROQ_API_KEY")
        )

        # Output parser for structured results
        self.output_parser = PydanticOutputParser(pydantic_object=VerificationResult)

        # Create prompt
        self.prompt = self._create_prompt()

        print("[VerifierAgent] Initialized with answer leak detection")

    def _create_prompt(self) -> ChatPromptTemplate:
        """
        Create verification prompt.
        """
        template = """You are a verifier agent. Your job is to check if a tutor's response reveals the answer to a problem.

PROBLEM:
{problem_text}

CORRECT ANSWER:
{correct_answer}

TUTOR'S DRAFT RESPONSE:
{tutor_response}

YOUR TASK:
Carefully analyze the tutor's response. Check if it:
1. States the answer directly (e.g., "The answer is 120")
2. Reveals the answer indirectly (e.g., "15 times 8 equals 120")
3. Shows the final calculation result
4. Gives away the solution

DECISION RULES:
- REJECT if the correct answer appears anywhere in the response
- REJECT if the response shows the final result
- REJECT if someone reading this could know the answer without solving
- APPROVE if only asking guiding questions
- APPROVE if only providing hints or breaking down steps
- APPROVE if encouraging student reasoning without revealing answer

{format_instructions}

Analyze the response and provide your verdict:"""

        prompt = ChatPromptTemplate.from_template(template)

        return prompt

    def verify(
        self,
        tutor_response: str,
        problem_text: str,
        correct_answer: str
    ) -> Dict[str, Any]:
        """
        Verify if tutor response is appropriate.

        Args:
            tutor_response: What the tutor agent generated
            problem_text: The problem being solved
            correct_answer: The correct answer that should not be revealed

        Returns:
            Dictionary with:
                - decision: "APPROVE" or "REJECT"
                - reason: Explanation
                - leaked_info: What was leaked (if rejected)
        """
        try:
            # Build prompt
            formatted_prompt = self.prompt.format(
                problem_text=problem_text,
                correct_answer=correct_answer,
                tutor_response=tutor_response,
                format_instructions=self.output_parser.get_format_instructions()
            )

            # Call LLM
            response = self.llm.invoke(formatted_prompt)

            # Parse structured output
            result = self.output_parser.parse(response.content)

            print(f"[VerifierAgent] Decision: {result.decision}")
            print(f"[VerifierAgent] Reason: {result.reason}")

            return {
                "decision": result.decision,
                "reason": result.reason,
                "leaked_info": result.leaked_info
            }

        except Exception as e:
            print(f"[VerifierAgent] Error: {e}")

            # Fallback: Simple keyword check
            if correct_answer.lower() in tutor_response.lower():
                return {
                    "decision": "REJECT",
                    "reason": f"Response contains the answer '{correct_answer}'",
                    "leaked_info": correct_answer
                }
            else:
                return {
                    "decision": "APPROVE",
                    "reason": "Fallback check passed (no direct answer found)",
                    "leaked_info": ""
                }


# ===== EXPLANATION =====

"""
WHY VERIFIER IS DIFFERENT FROM TUTOR:

Tutor Agent:
    - Needs tools (calculator, hints)
    - Uses ReAct pattern (reasoning + acting)
    - Creative output (generates questions)
    - Higher temperature (0.7) for variety

Verifier Agent:
    - No tools needed (just analysis)
    - Direct prompt (no ReAct needed)
    - Structured output (APPROVE/REJECT)
    - Lower temperature (0.3) for consistency

STRUCTURED OUTPUT (Pydantic):

Without Pydantic:
    LLM returns: "I think this is okay because..."
    We have to parse text, extract decision
    Error-prone, inconsistent format

With Pydantic:
    class VerificationResult(BaseModel):
        decision: str
        reason: str

    LLM must return JSON matching this structure:
    {
        "decision": "REJECT",
        "reason": "Answer revealed"
    }

    Guaranteed format, easy to use!

HOW IT WORKS:

1. Build prompt with:
    - Problem
    - Correct answer
    - Tutor's draft

2. Tell LLM format requirements:
    "Return JSON with decision and reason fields"

3. LLM analyzes:
    "Does tutor response reveal '120'?"
    "Can student know answer from this?"

4. LLM returns structured JSON:
    {"decision": "REJECT", "reason": "..."}

5. Pydantic parses and validates:
    result.decision  -> "REJECT"
    result.reason    -> "Response contains 120"

FALLBACK LOGIC:

If LLM call fails or parsing breaks:
    -> Simple keyword check
    -> If correct_answer in response: REJECT
    -> Else: APPROVE

This ensures system never breaks completely!

EXAMPLE VERIFICATION:

Input:
    Problem: "What is 15 × 8?"
    Correct Answer: "120"
    Tutor Response: "The answer is 120"

Verifier thinks:
    "Response says 'answer is 120'"
    "120 is the correct answer"
    "This reveals the answer!"

Output:
    {
        "decision": "REJECT",
        "reason": "Response directly states the answer '120'",
        "leaked_info": "120"
    }

---

Input:
    Problem: "What is 15 × 8?"
    Correct Answer: "120"
    Tutor Response: "Can you break 15 into 10 and 5?"

Verifier thinks:
    "Response asks a question"
    "No mention of 120"
    "This guides without revealing"

Output:
    {
        "decision": "APPROVE",
        "reason": "Only provides guidance, no answer revealed",
        "leaked_info": ""
    }
"""
