"""
DEMO 3: TOOL FAILURE RECOVERY

What to explain in video:
- Tools can fail (bad input, API errors, etc.)
- System doesn't crash - handles gracefully
- Returns error as observation to agent
- Agent can recover and try different approach

Time: 2-3 minutes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.basic_tools import calculator, check_answer, get_hint

print("=" * 70)
print("DEMO 3: TOOL FAILURE RECOVERY")
print("=" * 70)

print("\n[WHY THIS MATTERS]")
print("In production, tools can fail:")
print("  - Invalid input")
print("  - API timeouts")
print("  - Network errors")
print("  - Permission issues")
print("")
print("Bad approach: System crashes")
print("Good approach: Handle gracefully, continue working")

print("\n[OUR TOOLS]")
print("1. calculator(expression) - Evaluates math")
print("2. check_answer(student, correct) - Verifies answer")
print("3. get_hint(problem, level) - Provides hints")

input("\nPress ENTER to test tools with failures...")

# Test 1: Calculator with invalid input
print("\n" + "=" * 70)
print("TEST 1: Calculator with invalid input")
print("=" * 70)

print("\nInput: 'fifteen times eight' (words, not numbers)")
result = calculator("fifteen times eight")

print(f"Success: {result['success']}")
if not result['success']:
    print(f"Error: {result['error']}")
    print("-> System did NOT crash!")
    print("-> Error returned as observation")
    print("-> Agent can try different approach")

# Test 2: Calculator with division by zero
print("\n" + "=" * 70)
print("TEST 2: Calculator with division by zero")
print("=" * 70)

print("\nInput: '10 / 0' (mathematical error)")
result = calculator("10 / 0")

print(f"Success: {result['success']}")
if not result['success']:
    print(f"Error: {result['error']}")
    print("-> System handled division by zero")
    print("-> Graceful error message")

# Test 3: Valid calculator usage
print("\n" + "=" * 70)
print("TEST 3: Calculator with valid input")
print("=" * 70)

print("\nInput: '15 * 8' (valid)")
result = calculator("15 * 8")

print(f"Success: {result['success']}")
if result['success']:
    print(f"Result: {result['result']}")
    print("-> Works perfectly with valid input")

# Test 4: Check answer tool
print("\n" + "=" * 70)
print("TEST 4: Check answer tool")
print("=" * 70)

print("\nTest 4a: Correct answer")
result = check_answer("120", "120")
print(f"Student: '120', Correct: '120'")
print(f"Result: {result}")

print("\nTest 4b: Wrong answer")
result = check_answer("100", "120")
print(f"Student: '100', Correct: '120'")
print(f"Result: {result}")

# Test 5: Hint tool
print("\n" + "=" * 70)
print("TEST 5: Hint system")
print("=" * 70)

problem = "What is 15 multiplied by 8?"

print(f"\nProblem: {problem}")
print("\nLevel 1 hint:")
result = get_hint(problem, 1)
print(f"  {result['hint']}")

print("\nLevel 2 hint:")
result = get_hint(problem, 2)
print(f"  {result['hint']}")

print("\nLevel 3 hint:")
result = get_hint(problem, 3)
print(f"  {result['hint']}")

print("\n" + "=" * 70)
print("KEY POINTS TO EXPLAIN:")
print("=" * 70)
print("1. Every tool returns {success: bool, ...}")
print("2. Failures don't crash - return error message")
print("3. Agent receives error as observation")
print("4. Agent can reason about error and try again")
print("5. This makes system ROBUST in production")

print("\n[SUCCESS] Tool failure recovery demo complete!")
