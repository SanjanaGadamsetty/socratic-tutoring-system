# Socratic Tutoring System - Build Journal

**Date Started:** September 26, 2026  
**Mentor:** Claude  
**Builder:** Sanju  

---

## Session 1 - Getting Started

### What We're Building
A smart tutoring system where:
- Tutor agent asks questions (doesn't give answers directly)
- Verifier agent checks tutor didn't leak the answer
- Students learn by thinking, not by being told
- BONUS: PDF upload feature for tutoring on any document

---

## Progress Log

### Step 1: Project Structure [COMPLETE]

Created folder organization:
- `app/` - all our Python code
- `app/agents/` - tutor & verifier agents
- `app/tools/` - functions agents can use
- `app/api/` - web server endpoints (FastAPI)
- `database/` - database setup
- `tests/` - test files

**Flow Diagram:**
```
Project Root
    |
    |-- app/
    |     |-- agents/       (Tutor & Verifier agents)
    |     |-- tools/        (Functions agents can call)
    |     |-- api/          (FastAPI endpoints)
    |
    |-- database/           (DB schema & migrations)
    |-- tests/              (Test files)
    |-- About my project/   (Docs & diagrams)
    |-- .env                (API keys - NOT committed)
    |-- .gitignore          (Files to ignore)
    |-- requirements.txt    (Dependencies)
```

**Why folders?** Real projects need structure. Keeps code organized and maintainable.

---

### Step 2: Design Diagrams [COMPLETE]

Created 4 visual diagrams in `About my project/Drawings/`:

1. **Architecture Diagram** - shows Student to API to Agents to Database flow
2. **Database Schema** - 5 tables: problems, sessions, turns, hints_given, verifier_flags
3. **Agent Sequence Flow** - the tutor to verifier to retry loop (max 3 retries)
4. **API Endpoints** - 5 routes we'll build (3 core + 2 PDF bonus)

**Flow Diagram - System Overview:**
```
[Student] 
    |
    | HTTP Request
    v
[FastAPI Server]
    |
    | Calls agent
    v
[Agent System]
    |-- Tutor Agent (generates questions)
    |-- Verifier Agent (checks for leaks)
    |
    | Saves data
    v
[PostgreSQL Database]
    |
    | AI calls
    v
[Groq API / LLM]
```

**Why diagrams first?** Like blueprints before building a house. Plan before code.

---

### Step 3: GitHub Prep [COMPLETE]

Created essential git files:
- `.gitignore` - tells git what NOT to upload (secrets, cache, temp files)
- `README.md` - project description & documentation
- `.env.example` - template for API keys

**Flow Diagram - Git Workflow:**
```
Local Files
    |
    | .gitignore filters
    v
Git Staging Area (.env excluded, code included)
    |
    | git commit
    v
Local Repository (commit history)
    |
    | git push
    v
GitHub Remote Repository (code visible online)
```

**Why .gitignore?** So we NEVER accidentally upload API keys to GitHub. Security first.

---

### Step 4: GitHub Connected [COMPLETE]

Successfully set up Git and pushed to GitHub:
- Initialized local git repository
- Created remote repo on GitHub
- Connected local to remote
- Pushed initial commit

**Flow Diagram - First Push:**
```
Step 1: git init
    (Creates .git folder locally)

Step 2: git add .
    (Stages all files)

Step 3: git commit -m "message"
    (Saves snapshot locally)

Step 4: git remote add origin [URL]
    (Links to GitHub repo)

Step 5: git push -u origin main
    (Uploads code to GitHub)
```

**Why GitHub?** Version control = time machine for code. Can always go back if we break something.

---

### Step 5: Environment Setup [COMPLETE]

- Updated to use **Groq API** (faster and free)
- Created `requirements.txt` with all dependencies
- Installed all packages successfully
- Created `.env` file with API key

**Flow Diagram - Package Installation:**
```
requirements.txt
    |
    | Lists packages needed:
    | - groq
    | - python-dotenv
    | - pydantic
    |
    v
pip install -r requirements.txt
    |
    | Downloads and installs
    v
Packages installed in virtual environment
    |
    v
Code can now import these packages
```

**Why Groq?** Super fast, free, same API style as OpenAI. Perfect for learning.

---

## DAY 1: Building The Agent Brain

Now we build the core agent system - the thinking engine.

---

### Step 6: Created Basic Tools [COMPLETE]

Built 3 essential tools in `app/tools/basic_tools.py`:
1. **calculator()** - exact math calculations (no hallucinations)
2. **check_answer()** - compares student answer vs correct answer
3. **get_hint()** - provides hints at 3 difficulty levels

**Flow Diagram - Tool Execution:**
```
Agent decides to use a tool
    |
    v
Parse tool name & arguments from LLM response
    |
    v
Check if tool exists in TOOLS registry
    |
    v
Execute tool function with arguments
    |
    |-- Success: return {"success": True, "result": ...}
    |
    |-- Error: return {"success": False, "error": ...}
    |
    v
Return result to agent (NO CRASH)
```

**Key learning:** Tools give AI superpowers. Without tools, AI just guesses. With tools, it gets exact results.

**Error recovery built in:** Every tool returns `{"success": True/False}` - if it fails, agent gets error info instead of crashing.

---

### Step 7: Built The Agent Brain [COMPLETE]

Created `app/agent.py` - the main thinking loop.

**The Agent Loop (Think-Act-Observe):**
1. **THINK** - Agent calls LLM to decide what to do
2. **ACT** - If agent wants to use a tool, execute it
3. **OBSERVE** - Give tool result back to agent
4. **REPEAT** - Loop continues until task is done (max 5 iterations)

**Flow Diagram - Main Agent Loop:**
```
START: User gives task
    |
    v
ITERATION 1:
    |
    | THINK: Call Groq API with task + system prompt
    v
    LLM returns response
    |
    v
    Does response contain TOOL_CALL?
    |
    |-- NO --> Task complete, return response to user
    |
    |-- YES --> Parse tool name & arguments
                    |
                    v
                Execute tool (with error recovery)
                    |
                    v
                Get tool result
                    |
                    v
                OBSERVE: Add result to conversation
                    |
                    v
                Go to next iteration
    |
    v
ITERATION 2, 3, 4, 5... (repeat until done or max iterations)
    |
    v
END: Return final response
```

**Key components:**
- `_build_system_prompt()` - instructions for the AI (job description)
- `_parse_tool_call()` - detects when AI wants to use a tool
- `_execute_tool()` - runs tools with error recovery
- `run()` - the main loop that orchestrates everything

**Self-healing - Error Recovery at 2 Levels:**
```
LEVEL 1: Tool Execution
    try:
        result = tool_function()
    except Exception as e:
        return {"success": False, "error": str(e)}
    
    (Tool never crashes, always returns result)

LEVEL 2: Agent Loop
    try:
        response = groq_api.call()
    except Exception as e:
        add error to conversation
        loop continues
    
    (Agent keeps trying, doesn't give up)
```

---

### Step 8: Debugged Groq Models [COMPLETE]

Hit issue: old Groq models were decommissioned.

Created diagnostic scripts in `tests/model tests/`:
- `test_groq.py` - checks API key and connection
- `list_models.py` - lists all available models
- `test_chat_models.py` - finds which models work for chat

**Flow Diagram - Model Discovery:**
```
Try model: llama-3.1-8b-instant
    |
    v
    404 Error: Model not found
    |
    v
Try model: llama3-8b-8192
    |
    v
    400 Error: Model decommissioned
    |
    v
List all available models
    |
    v
    Found: openai/gpt-oss-120b
    |
    v
Test model with simple query
    |
    v
    SUCCESS! Use this model
```

**Solution:** Updated to `openai/gpt-oss-120b` (120B parameters, very powerful)

**Tested successfully:** Agent now thinks, uses tools, and tutors students.

---

## DAY 1 COMPLETE

**What we built:**
- [x] 3 working tools (calculator, check_answer, get_hint)
- [x] Full agent loop (think-act-observe)
- [x] Error recovery at 2 levels
- [x] Successfully ran 2 test scenarios

**Day 1 checkpoint met:** Working agent that completes tasks using tools, with demonstrated error recovery.

**Complete System Flow:**
```
User Input
    |
    v
Agent.run(task)
    |
    v
Build system prompt with tool descriptions
    |
    v
Loop (max 5 iterations):
    |
    | Call Groq API (THINK)
    v
    Parse response
    |
    |-- Contains TOOL_CALL?
    |       |
    |       v
    |       Execute tool (ACT)
    |       |
    |       v
    |       Get result (OBSERVE)
    |       |
    |       v
    |       Add to conversation
    |       |
    |       v
    |       Continue loop
    |
    |-- Plain text response?
            |
            v
            Task complete
            |
            v
            Return response to user
```

---

### Step 9: Pushed to GitHub [COMPLETE]

All Day 1 work successfully pushed to GitHub.
- Repository: https://github.com/SanjanaGadamsetty/socratic-tutoring-system
- Commit message: "Day 1 Complete: Built agent brain with tools and error recovery"
- 852 lines of code written

**Flow Diagram - Git Commit Cycle:**
```
Code changes made locally
    |
    v
git add . (stage changes)
    |
    v
git status (review what will be committed)
    |
    v
git commit -m "message" (save snapshot)
    |
    v
git push origin main (upload to GitHub)
    |
    v
Code visible on GitHub (backup + sharing)
```

**Why commit often?** GitHub = safety net. If something breaks tomorrow, we can always go back to this working version.

**Note:** Removed co-author attribution from future commits per user preference.

---

## DAY 1 FINAL SUMMARY

**What we accomplished:**
- [x] Project structure & GitHub setup
- [x] 4 architecture diagrams created
- [x] 3 working tools with error recovery
- [x] Full agent brain (think-act-observe loop)
- [x] Successfully tested with real AI model
- [x] 852 lines of working code

**Learning outcomes:**
- Understood tool-based agents
- Built agent loop from scratch (no frameworks)
- Implemented error recovery at multiple levels
- Debugged API issues successfully

**High-Level System Architecture:**
```
                    SOCRATIC TUTORING SYSTEM - DAY 1
                    
    +----------------------------------------------------------+
    |                      USER INPUT                          |
    |                   "What is 15 * 8?"                      |
    +----------------------------------------------------------+
                                |
                                v
    +----------------------------------------------------------+
    |                    TUTORING AGENT                        |
    |                   (app/agent.py)                         |
    |                                                          |
    |  Think-Act-Observe Loop:                                |
    |  1. THINK  -> Call Groq LLM                             |
    |  2. ACT    -> Execute tools if needed                   |
    |  3. OBSERVE-> Get results, update context               |
    |  4. REPEAT -> Until task complete                       |
    +----------------------------------------------------------+
                    |                           |
                    v                           v
    +-------------------------+   +--------------------------+
    |    TOOLS (3 total)      |   |    GROQ API             |
    |  - calculator           |   |  (openai/gpt-oss-120b)  |
    |  - check_answer         |   |                         |
    |  - get_hint             |   |  Returns: decisions,    |
    |                         |   |  questions, tool calls  |
    |  Each with error        |   +--------------------------+
    |  recovery built in      |
    +-------------------------+
                    |
                    v
    +----------------------------------------------------------+
    |                   AGENT RESPONSE                         |
    |    "Let's break this down. Can you think of this as     |
    |     repeated addition? What is 15 added 8 times?"       |
    +----------------------------------------------------------+
```

---

### Step 10: Created Project Checklist [COMPLETE]

Created comprehensive `PROJECT_CHECKLIST.md` with:
- All 5 days broken down into actionable tasks
- Bonus PDF feature tasks
- Final deliverables checklist
- Progress tracker
- Notes on decisions made

**Flow Diagram - Project Roadmap:**
```
DAY 1: Agent Fundamentals [COMPLETE]
    - Tools + Agent loop + Error recovery
    |
    v
DAY 2: Database & API
    - PostgreSQL + FastAPI + SSE streaming
    |
    v
DAY 3: Durable Execution
    - Background jobs + Retry logic + Idempotency
    |
    v
DAY 4: LangChain Multi-Agent
    - Tutor agent + Verifier agent + Handoff
    |
    v
DAY 5: LangGraph & Testing
    - State graph + Testing + Documentation + Video
    |
    v
BONUS: PDF Feature (Optional)
    - PDF upload + RAG + Vector DB
    |
    v
FINAL DELIVERABLES
    - Working project + 3-page doc + 30-min video
```

**Why a checklist?** Keeps us organized, shows progress, ensures we don't miss requirements.

---

## Next: Day 2 - Database & API Layer

Ready to start whenever you are.
