"""
Tutor Agent - Generates Socratic questions.

This agent's job:
- Ask guiding questions (Socratic method)
- NEVER give direct answers
- Help student think through problems
- Use tools when needed (calculator, hints)
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


class TutorAgent:
    """
    Socratic tutor agent using LangChain.

    Simplified approach using direct LLM calls with structured prompts.
    """

    def __init__(self):
        """
        Initialize tutor agent.
        """
        # Initialize LLM
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.7,
            api_key=os.getenv("GROQ_API_KEY")
        )

        print("[TutorAgent] Initialized with Socratic prompting")

    def generate_response(self, context: Dict[str, Any]) -> str:
        """
        Generate Socratic response based on context.

        Args:
            context: Dictionary containing:
                - problem_text: The problem being solved (optional if pdf_content provided)
                - correct_answer: The correct answer (agent must not reveal) (optional for PDF)
                - conversation_history: Previous turns
                - student_last_response: What student just said
                - pdf_content: PDF text content (optional, for PDF-based tutoring)

        Returns:
            Socratic question/guidance (string)
        """
        # Build prompt
        system_prompt = """You are a Socratic tutor. Your goal is to guide students to discover answers themselves through questioning.

CRITICAL RULES:
1. NEVER state the answer directly
2. NEVER reveal the correct answer in your questions
3. ASK guiding questions that lead student to think
4. Break down complex problems into smaller steps
5. Encourage student reasoning
6. Keep responses concise (2-3 sentences max)"""

        # Check if this is PDF-based or problem-based tutoring
        if 'pdf_content' in context and context['pdf_content']:
            # PDF-based tutoring
            user_prompt = f"""PDF Content (Study Material):
{context['pdf_content'][:2000]}...  (truncated for context)

Previous conversation:
{context.get('conversation_history', 'No previous conversation')}

Student just said: {context['student_last_response']}

Generate your next Socratic question based on the PDF content. Help the student understand the concepts from the material through guided questioning. Remember: ASK questions, don't give direct answers from the text."""
        else:
            # Problem-based tutoring
            user_prompt = f"""Problem: {context['problem_text']}
Correct Answer (DO NOT REVEAL THIS): {context['correct_answer']}

Previous conversation:
{context.get('conversation_history', 'No previous conversation')}

Student just said: {context['student_last_response']}

Generate your next Socratic question to guide the student. Remember: ASK questions, don't give answers."""

        try:
            # Create messages
            messages = [
                ("system", system_prompt),
                ("human", user_prompt)
            ]

            # Call LLM
            response = self.llm.invoke(messages)

            return response.content

        except Exception as e:
            print(f"[TutorAgent] Error: {e}")
            # Fallback response
            return "Let's break this down. What's the first step you think we should take?"


# ===== EXPLANATION =====

"""
WHAT IS LANGCHAIN DOING HERE?

1. ChatGroq (LLM):
    - Connects to Groq API
    - Same model we used before
    - But wrapped in LangChain format

2. Tools:
    Our old tools (calculator, get_hint)
    Wrapped in LangChain Tool format:
        Tool(name="calculator", func=calculator, description="...")

    This lets LangChain:
        - Know what tools exist
        - Pass descriptions to LLM
        - Execute tools when LLM requests them

3. ReAct Agent:
    ReAct = Reasoning + Acting

    Pattern:
        Thought: "I need to calculate 15*8"
        Action: calculator
        Action Input: "15*8"
        Observation: 120
        Thought: "Now I can guide student without revealing 120"
        Final Answer: "Can you break 15 into 10+5?"

4. AgentExecutor:
    Runs the think-act loop automatically
    We used to do this manually (Day 1)
    Now LangChain handles it

FLOW:

User calls: tutor.generate_response(context)
    |
    v
Build input text with problem + history
    |
    v
agent_executor.invoke({"input": text})
    |
    v
LangChain runs ReAct loop:
    - LLM thinks
    - Decides if tool needed
    - Executes tool if requested
    - LLM sees result
    - Generates final response
    |
    v
Return response to caller

COMPARISON:

Day 1 (Manual):
    messages = []
    for i in range(5):
        response = groq.chat(messages)
        if "TOOL_CALL" in response:
            result = execute_tool()
            messages.append(result)
        ...
    (50+ lines of code)

Day 4 (LangChain):
    agent_executor.invoke({"input": text})
    (1 line, LangChain does the rest)
"""
