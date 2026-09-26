"""
The Agent Brain - Day 1 Core Implementation

This is the heart of our system!
The agent thinks, decides what to do, uses tools, and learns from results.
"""

import os
import sys
import json
import re
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from groq import Groq

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.basic_tools import TOOLS, get_tools_description


# Load environment variables from .env file
load_dotenv()


class TutoringAgent:
    """
    The main agent that helps tutor students.

    This is a "from scratch" implementation without frameworks.
    We're building the think-act-observe loop manually!
    """

    def __init__(self, model: str = "openai/gpt-oss-120b"):
        """
        Initialize the agent.

        Args:
            model: Which Groq model to use (default is openai/gpt-oss-120b)
        """
        # Get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file!")

        # Initialize Groq client
        self.client = Groq(api_key=api_key)
        self.model = model

        # Conversation history (memory!)
        self.messages: List[Dict[str, str]] = []

        # Tools available to the agent
        self.tools = TOOLS

        print(f"🤖 Agent initialized with model: {model}")
        print(f"🛠️  {len(self.tools)} tools available")

    def _build_system_prompt(self) -> str:
        """
        Build the system prompt that tells the AI how to behave.
        This is like giving instructions to an employee!
        """
        tools_desc = get_tools_description()

        system_prompt = f"""You are a Socratic tutor agent. Your job is to guide students to understanding through questions, NOT by giving direct answers.

{tools_desc}

**How to use tools:**
When you want to use a tool, respond in this EXACT format:
TOOL_CALL: tool_name
ARGUMENTS: {{"param1": "value1", "param2": "value2"}}

Example:
TOOL_CALL: calculator
ARGUMENTS: {{"expression": "2+2"}}

After you use a tool, you'll receive the result. Then continue helping the student.

**Your personality:**
- Ask guiding questions (Socratic method)
- Never give direct answers
- Be encouraging and patient
- Use tools when you need exact information
"""
        return system_prompt

    def _parse_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse the AI's response to see if it wants to call a tool.

        Example input:
        "TOOL_CALL: calculator
         ARGUMENTS: {"expression": "2+2"}"

        Returns:
        {"tool": "calculator", "arguments": {"expression": "2+2"}}
        """
        # Look for TOOL_CALL pattern
        tool_match = re.search(r'TOOL_CALL:\s*(\w+)', response)
        args_match = re.search(r'ARGUMENTS:\s*(\{.*?\})', response, re.DOTALL)

        if tool_match and args_match:
            try:
                tool_name = tool_match.group(1)
                arguments = json.loads(args_match.group(1))

                return {
                    "tool": tool_name,
                    "arguments": arguments
                }
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse tool arguments: {e}")
                return None

        return None

    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool and return the result.

        This includes ERROR RECOVERY - if tool fails, we don't crash!
        """
        print(f"\n🔧 Executing tool: {tool_name}")
        print(f"   Arguments: {arguments}")

        # Check if tool exists
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found!",
                "available_tools": list(self.tools.keys())
            }

        try:
            # Get the actual function
            tool_function = self.tools[tool_name]["function"]

            # Call it with the arguments
            result = tool_function(**arguments)

            print(f"✅ Tool result: {result}")
            return result

        except Exception as e:
            # ERROR RECOVERY! Don't crash - return error info
            print(f"❌ Tool execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute {tool_name}"
            }

    def run(self, task: str, max_iterations: int = 5) -> str:
        """
        The main agent loop! This is where the magic happens.

        THE LOOP:
        1. Think (call LLM)
        2. Act (use tools if needed)
        3. Observe (get results)
        4. Repeat until done

        Args:
            task: The task/question to work on
            max_iterations: Maximum thinking cycles (prevents infinite loops)

        Returns:
            Final response to the user
        """
        print(f"\n{'='*60}")
        print(f"🎯 NEW TASK: {task}")
        print(f"{'='*60}\n")

        # Initialize conversation with system prompt
        self.messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": task}
        ]

        iteration = 0
        final_response = ""

        # THE AGENT LOOP!
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration}/{max_iterations} ---")

            try:
                # STEP 1: THINK - Call the LLM
                print("🧠 Agent is thinking...")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    temperature=0.7,
                    max_tokens=500
                )

                # Get the AI's response
                assistant_message = response.choices[0].message.content
                print(f"💭 Agent thought: {assistant_message[:200]}...")

                # Add to conversation history
                self.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })

                # STEP 2: ACT - Check if agent wants to use a tool
                tool_call = self._parse_tool_call(assistant_message)

                if tool_call:
                    # Agent wants to use a tool!
                    tool_result = self._execute_tool(
                        tool_call["tool"],
                        tool_call["arguments"]
                    )

                    # STEP 3: OBSERVE - Give result back to agent
                    observation = f"TOOL_RESULT: {json.dumps(tool_result, indent=2)}"
                    print(f"📊 Observation: {observation}")

                    # Add observation to conversation
                    self.messages.append({
                        "role": "user",
                        "content": observation
                    })

                    # Loop continues - agent will think about the result

                else:
                    # No tool call - agent is done thinking!
                    print("✅ Agent finished (no more tool calls)")
                    final_response = assistant_message
                    break

            except Exception as e:
                # ERROR RECOVERY at the loop level!
                print(f"❌ Error in agent loop: {e}")
                error_message = f"I encountered an error: {str(e)}. Let me try a different approach."

                self.messages.append({
                    "role": "user",
                    "content": error_message
                })

                # Loop continues - agent will recover!

        if iteration >= max_iterations:
            final_response = "I've reached my thinking limit. Let me summarize what we've discovered so far..."

        print(f"\n{'='*60}")
        print(f"🎉 FINAL RESPONSE:")
        print(final_response)
        print(f"{'='*60}\n")

        return final_response

    def reset(self):
        """Clear conversation history for a fresh start."""
        self.messages = []
        print("🔄 Agent memory cleared")


# ===== DEMO FUNCTION - Let's test it! =====

def demo():
    """
    A simple demo to see the agent in action!
    """
    print("\n" + "="*60)
    print("🎓 SOCRATIC TUTORING AGENT DEMO")
    print("="*60 + "\n")

    # Create agent
    agent = TutoringAgent()

    # Test 1: Simple math problem
    print("\n📝 TEST 1: Math Problem")
    response = agent.run(
        "A student asks: 'What is 15 * 8?' Help them figure it out using Socratic questioning."
    )

    # Test 2: Checking an answer
    print("\n\n📝 TEST 2: Check Answer")
    agent.reset()
    response = agent.run(
        "The student thinks the answer to '10 + 5' is 16. Check their answer and guide them."
    )

    print("\n✅ Demo complete!")


if __name__ == "__main__":
    # Run demo if this file is executed directly
    demo()
