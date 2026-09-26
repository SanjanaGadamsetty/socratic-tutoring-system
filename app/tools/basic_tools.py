"""
Basic tools for the tutoring agent to use.

These are simple functions that give the AI superpowers!
"""

import json
from typing import Dict, Any


def calculator(expression: str) -> Dict[str, Any]:
    """
    A simple calculator tool.

    Why? The AI might hallucinate wrong math answers.
    With this tool, it gets EXACT results!

    Args:
        expression: Math expression like "2+2" or "10*5"

    Returns:
        Dictionary with result or error
    """
    try:
        # eval() calculates the expression
        # Warning: In real production, use safer alternatives!
        result = eval(expression)
        return {
            "success": True,
            "result": result,
            "message": f"{expression} = {result}"
        }
    except Exception as e:
        # If something goes wrong, return error (not crash!)
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to calculate: {expression}"
        }


def check_answer(student_answer: str, correct_answer: str) -> Dict[str, Any]:
    """
    Check if student's answer matches the correct answer.

    Why? To know if the student solved the problem!

    Args:
        student_answer: What the student said
        correct_answer: The correct answer

    Returns:
        Dictionary with match result
    """
    try:
        # Simple comparison (we can make this smarter later!)
        is_correct = student_answer.strip().lower() == correct_answer.strip().lower()

        return {
            "success": True,
            "is_correct": is_correct,
            "message": "Correct!" if is_correct else "Not quite right, keep trying!"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to check answer"
        }


def get_hint(problem_text: str, hint_level: int) -> Dict[str, Any]:
    """
    Generate hints based on difficulty level.

    Why? To help students without giving away the answer!

    Args:
        problem_text: The problem being solved
        hint_level: 1 (easy hint) to 3 (stronger hint)

    Returns:
        Dictionary with hint
    """
    try:
        # Simple hint system (we'll make this AI-powered later!)
        hints = {
            1: "Think about what information you have and what you're looking for.",
            2: "Break the problem into smaller steps. What's the first step?",
            3: "Look at the key numbers or concepts in the problem. How do they relate?"
        }

        hint_level = max(1, min(3, hint_level))  # Keep between 1-3

        return {
            "success": True,
            "hint": hints.get(hint_level),
            "level": hint_level,
            "message": f"Hint level {hint_level} provided"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate hint"
        }


# Tool registry - tells the agent what tools exist
TOOLS = {
    "calculator": {
        "function": calculator,
        "description": "Calculate mathematical expressions exactly. Use when you need precise math results.",
        "parameters": {
            "expression": "string - the math expression to calculate (e.g., '2+2', '10*5')"
        }
    },
    "check_answer": {
        "function": check_answer,
        "description": "Check if student's answer matches the correct answer.",
        "parameters": {
            "student_answer": "string - the student's answer",
            "correct_answer": "string - the correct answer"
        }
    },
    "get_hint": {
        "function": get_hint,
        "description": "Get a hint for the student. Hint level 1-3, where 1 is gentle and 3 is stronger.",
        "parameters": {
            "problem_text": "string - the problem being solved",
            "hint_level": "integer - 1 (gentle) to 3 (stronger)"
        }
    }
}


def get_tools_description() -> str:
    """
    Generate a text description of all available tools.
    This is what we'll show the AI so it knows what it can use!
    """
    desc = "You have access to the following tools:\n\n"

    for tool_name, tool_info in TOOLS.items():
        desc += f"**{tool_name}**\n"
        desc += f"Description: {tool_info['description']}\n"
        desc += "Parameters:\n"
        for param, param_desc in tool_info['parameters'].items():
            desc += f"  - {param}: {param_desc}\n"
        desc += "\n"

    return desc
