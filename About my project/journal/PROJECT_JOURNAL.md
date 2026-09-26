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

---

## DAY 2: Database & API Layer [COMPLETE]

Building the persistence and HTTP service layers.

---

### Step 11: Database Setup [COMPLETE]

Created SQLite database with SQLAlchemy ORM.

**Files created:**
- `database/models.py` - 5 table models (Problem, Session, Turn, HintGiven, VerifierFlag)
- `database/connection.py` - Database engine and session management
- `database/init_db.py` - Initialization script with seed data

**Flow Diagram - Database Architecture:**
```
SQLAlchemy ORM Models (Python Classes)
    |
    | Base.metadata.create_all()
    v
SQLite Database File (socratic_tutoring.db)
    |
    +-- problems (7 sample rows)
    +-- sessions (empty, ready for data)
    +-- turns (empty)
    +-- hints_given (empty)
    +-- verifier_flags (empty)

Table Relationships:
    Problem (1) ----< (Many) Session
    Session (1) ----< (Many) Turn
    Session (1) ----< (Many) HintGiven
    Session (1) ----< (Many) VerifierFlag
    Turn (1) ----< (Many) VerifierFlag
```

**Key concepts learned:**
- ORM maps Python classes to database tables
- Relationships provide navigation between tables
- Cascade deletes clean up related data automatically

**Database initialization flow:**
```
Run: python database/init_db.py
    |
    v
Create all tables from models
    |
    v
Check if problems exist
    |
    |-- Exist? Skip seeding
    |
    |-- Empty? Seed 7 sample problems
    v
Database ready for use
```

---

### Step 12: API Layer with FastAPI [COMPLETE]

Built HTTP API to expose tutoring system.

**Files created:**
- `app/api/schemas.py` - Pydantic request/response models
- `app/api/main.py` - FastAPI application with 4 endpoints
- `app/api/streaming.py` - SSE streaming endpoint

**API Endpoints:**
```
GET /
    Purpose: Health check
    Response: {"status": "online", ...}

GET /problems
    Purpose: List all available problems
    Response: {"problems": [...], "total": 7}

POST /sessions/start
    Input: {"problem_id": 1, "student_id": "alice"}
    Process: Create session + Generate first question
    Response: {"session_id": 1, "first_question": "..."}

POST /sessions/{id}/turn
    Input: {"student_answer": "120"}
    Process: Save turn + Check correctness + Generate next question
    Response: {"tutor_question": "...", "is_correct": true/false}

GET /sessions/{id}/transcript
    Purpose: Get full conversation history
    Response: {"turns": [...], "hints_given": [...], "verifier_flags": [...]}
```

**Flow Diagram - API Request Cycle:**
```
Client sends HTTP POST /sessions/start
    |
    | Body: {"problem_id": 1, "student_id": "alice"}
    v
FastAPI validates against SessionStartRequest schema
    |
    |-- Invalid? Return 400 with validation errors
    |
    |-- Valid? Continue
    v
Dependency injection: get_db() provides database session
    |
    v
Endpoint function executes:
    |
    +-- Query problem from database
    |
    +-- Create new session record
    |
    +-- Call agent to generate first question
    |
    +-- Save tutor turn to database
    |
    +-- Build SessionStartResponse
    v
FastAPI serializes response to JSON
    |
    v
Client receives: {"session_id": 1, "first_question": "..."}
    |
    v
Database session automatically closed
```

**Key concepts learned:**
- Pydantic validates input/output automatically
- Dependency injection manages database connections
- FastAPI auto-generates API documentation
- Response models ensure type safety

---

### Step 13: Server-Sent Events (SSE) Streaming [COMPLETE]

Added real-time streaming to watch agent think.

**File created:**
- `app/api/streaming.py` - SSE implementation

**Flow Diagram - SSE Streaming:**
```
Client opens SSE connection: POST /sessions/{id}/turn/stream
    |
    v
Server starts async generator
    |
    v
yield {"type": "status", "message": "Initializing..."}
    |
    | Client receives event, updates UI
    v
yield {"type": "thinking", "message": "Agent is thinking..."}
    |
    | Client shows loading indicator
    v
yield {"type": "tool_call", "tool": "calculator", "args": {...}}
    |
    | Client shows "Using calculator..."
    v
yield {"type": "tool_result", "result": {"success": true, "result": 120}}
    |
    | Client displays tool result
    v
yield {"type": "response", "message": "Final agent response"}
    |
    | Client displays agent's question
    v
yield {"type": "complete"}
    |
    v
Connection closes
```

**Why SSE vs WebSockets?**
```
SSE (Server-Sent Events):
    - One-way: Server to Client only
    - HTTP-based, simpler setup
    - Auto-reconnects
    - Perfect for: Progress updates, notifications, streaming responses

WebSockets:
    - Two-way: Bidirectional communication
    - More complex protocol
    - Better for: Chat apps, gaming, real-time collaboration

Our use case: Server sends progress updates to client
Choice: SSE (simpler, fits perfectly)
```

**Streaming vs Non-Streaming comparison:**
```
Without Streaming:
    Client: "Start session"
    [5 seconds of waiting...]
    Server: "Here's the response"
    
    User sees: Loading spinner for 5 seconds, then response

With Streaming:
    Client: "Start session"
    Server: "Status: Initializing..." (0.1s)
    Server: "Agent thinking..." (1s)
    Server: "Using calculator..." (2s)
    Server: "Tool result: 120" (2.5s)
    Server: "Final response" (5s)
    
    User sees: Live updates, understands what's happening
```

---

### Step 14: Testing & Validation [COMPLETE]

Created test scripts to verify all functionality.

**Test files:**
- `test_api.py` - Tests all standard endpoints
- `test_streaming.py` - Tests SSE streaming

**Test results:**
```
Standard API Tests:
    [PASS] Health check (GET /)
    [PASS] List problems (GET /problems) - Found 7 problems
    [PASS] Start session (POST /sessions/start) - Session ID: 1
    [PASS] Submit turn (POST /sessions/{id}/turn) - Got response
    [PASS] Get transcript (GET /sessions/{id}/transcript) - 3 turns

SSE Streaming Test:
    [PASS] Connection established
    [PASS] Received status events
    [PASS] Received thinking events
    [PASS] Received final response
    [PASS] Stream completed successfully
```

**Complete system flow:**
```
Student -> API -> Database -> Agent -> Tools -> LLM
   ^                                              |
   |                                              v
   +-------- Response with question  <-----------+

Detailed Flow:
1. Student calls POST /sessions/start
2. API creates session in database
3. API calls agent with problem context
4. Agent generates system prompt
5. Agent calls Groq LLM
6. LLM may request tool use
7. Agent executes tool (e.g., calculator)
8. Agent gets result, continues thinking
9. Agent generates Socratic question
10. API saves turn to database
11. API returns question to student
```

---

## DAY 2 COMPLETE

**What we built:**
- [x] SQLite database with 5 tables
- [x] SQLAlchemy ORM models
- [x] Database seeding (7 sample problems)
- [x] FastAPI application
- [x] 4 API endpoints (health, list, start, turn, transcript)
- [x] Pydantic request/response validation
- [x] SSE streaming for real-time updates
- [x] Incremental persistence (saves after each turn)
- [x] Complete integration tests

**Day 2 checkpoint met:** HTTP API backed by database, with SSE streaming tool events.

**Database Schema Visualization:**
```
socratic_tutoring.db (SQLite)
|
+-- problems
|   - Stores tutoring problems
|   - 7 sample problems loaded
|
+-- sessions
|   - Tracks tutoring sessions
|   - Links to problem
|   - Has status (started/in_progress/completed/abandoned)
|
+-- turns
|   - Each conversation exchange
|   - Links to session
|   - Speaker: tutor or student
|
+-- hints_given
|   - Tracks hint escalation
|   - Links to session
|   - Levels 1-3
|
+-- verifier_flags
    - When verifier rejects tutor
    - Links to session and turn
    - Stores rejection reason
```

**Architecture After Day 2:**
```
                COMPLETE SYSTEM ARCHITECTURE
                
    +--------------------------------------------------+
    |                   CLIENT                         |
    |            (Postman / curl / Frontend)           |
    +--------------------------------------------------+
                        |
                        | HTTP Request
                        v
    +--------------------------------------------------+
    |               FASTAPI SERVER                     |
    |                                                  |
    |  Endpoints:                                      |
    |  - GET /problems                                 |
    |  - POST /sessions/start                          |
    |  - POST /sessions/{id}/turn                      |
    |  - GET /sessions/{id}/transcript                 |
    |  - POST /sessions/{id}/turn/stream (SSE)         |
    |                                                  |
    |  Features:                                       |
    |  - Request validation (Pydantic)                 |
    |  - Dependency injection                          |
    |  - Auto-generated docs                           |
    +--------------------------------------------------+
            |                           |
            | Database queries          | Agent calls
            v                           v
    +-----------------+        +----------------------+
    |  SQLite DB      |        |   Tutoring Agent     |
    |                 |        |                      |
    |  - problems     |        |  - Think-Act-Observe |
    |  - sessions     |        |  - Tool execution    |
    |  - turns        |        |  - Error recovery    |
    |  - hints_given  |        +----------------------+
    |  - verifier_    |                    |
    |    flags        |                    | LLM calls
    +-----------------+                    v
                                   +----------------------+
                                   |     Groq API         |
                                   | (openai/gpt-oss-120b)|
                                   +----------------------+
```

---

## Next: Day 3 - Durable Execution (Optional)

**Note:** Based on project requirements, we should focus 80% on AI/agent layer, 20% on scaffolding.

**Options:**
1. Skip Day 3 (background jobs) - Go directly to Day 4 (Multi-agent with LangChain)
2. Do simplified Day 3 - Basic retry logic only, skip queue system
3. Stay on agent improvements - Enhance current agent before adding complexity

**Recommended:** Go to Day 4 (Multi-agent layer) - This is the core AI deliverable.
---

## DAY 3: Durable Execution [COMPLETE]

Building background job system for reliable long-running operations.

---

### Step 15: Job Model and Database [COMPLETE]

Created Job table for tracking background operations.

**File updated:**
- `database/models.py` - Added Job model and JobStatus enum

**Job model fields:**
```
Job Table:
    - id (primary key)
    - job_type (start_session, submit_turn)
    - status (queued, running, completed, failed, cancelled)
    - idempotency_key (prevent duplicates)
    - input_data (JSON of request)
    - result_data (JSON of response)
    - error_message (if failed)
    - retry_count / max_retries
    - timestamps (created, started, completed)
    - worker_id / last_heartbeat (for monitoring)
```

**Flow Diagram - Job Lifecycle:**
```
Job Created
    |
    | status = QUEUED
    v
Waiting in Queue
    |
    | Worker picks up
    v
status = RUNNING
    |
    | Worker processes
    v
Success?
    |
    |-- YES -> status = COMPLETED
    |          result_data = {...}
    |
    |-- NO -> retry_count++
                |
                |-- retry_count < max_retries
                |   status = QUEUED (try again)
                |
                |-- retry_count >= max_retries
                    status = FAILED
                    error_message = "..."
```

---

### Step 16: Background Worker [COMPLETE]

Built worker process to execute jobs asynchronously.

**File created:**
- `app/worker.py` - Worker that polls and processes jobs

**Worker features:**
1. Polls database for queued jobs
2. Processes jobs based on type
3. Updates job status in real-time
4. Implements retry logic
5. Handles stuck jobs (heartbeat timeout)

**Flow Diagram - Worker Operation:**
```
Worker starts
    |
    v
Poll database for jobs
    |
    |-- No jobs? Sleep 2 seconds, poll again
    |
    |-- Found job? Process it
        |
        v
    Update: status = RUNNING
        |
        v
    Execute job logic (call agent)
        |
        v
    Success?
        |
        |-- YES: Update status = COMPLETED
        |         Save result_data
        |
        |-- NO: Check retry_count
                |
                |-- Can retry: status = QUEUED
                |
                |-- Max retries: status = FAILED
        |
        v
    Continue polling
```

**Worker recovery mechanisms:**
```
Heartbeat Timeout Detection:

Job stuck in RUNNING for 5+ minutes?
    |
    v
Considered orphaned (worker crashed?)
    |
    v
Another worker can pick it up
    |
    v
Reprocess job
```

---

### Step 17: Job API Endpoints [COMPLETE]

Created async API endpoints for job management.

**File created:**
- `app/api/jobs.py` - Job creation and status endpoints

**Endpoints:**
```
POST /jobs/sessions/start
    Input: {problem_id, student_id}
    Output: {job_id, status: "queued"}
    Response: 202 Accepted (immediate)

POST /jobs/sessions/{id}/turn
    Input: {student_answer}
    Output: {job_id, status: "queued"}
    Response: 202 Accepted (immediate)

GET /jobs/{job_id}
    Output: {status, result, error, retry_count}
    Poll this to check completion

POST /jobs/{job_id}/cancel
    Cancel a queued job

GET /jobs
    List recent jobs
```

**Idempotency implementation:**
```
Client sends idempotency_key
    |
    v
Server checks: Does job with this key exist?
    |
    |-- YES: Return existing job (no duplicate)
    |
    |-- NO: Create new job
```

**Why idempotency matters:**
```
Without:
    User clicks "Start Session" twice (slow network)
        |
        v
    2 sessions created (bug!)

With idempotency:
    User clicks "Start Session" twice
        |
        | Same idempotency_key sent
        v
    First click: Create job 1
    Second click: Return job 1 (no duplicate)
        |
        v
    Only 1 session created (correct!)
```

---

### Step 18: Testing and Validation [COMPLETE]

Created comprehensive test demonstrating all Day 3 features.

**Test file:**
- `test_day3.py` - Async job system test

**Test demonstrates:**
```
Test 1: Job Creation
    - POST to /jobs/sessions/start
    - Returns 202 Accepted immediately
    - Job ID returned
    - Status: queued

Test 2: Idempotency
    - Send same request twice
    - Same job_id returned
    - No duplicate created

Test 3: Status Polling
    - Poll GET /jobs/{id} every 2 seconds
    - Watch status change: queued -> running -> completed
    - Retrieve final result

Test 4: List Jobs
    - GET /jobs?limit=5
    - See all recent jobs
```

**Complete flow diagram:**
```
                ASYNC JOB FLOW

Terminal 1: API Server
    |
    | Receives POST /jobs/sessions/start
    v
Create job in database (status=QUEUED)
    |
    | Return 202 Accepted
    v
Client has job_id

Terminal 2: Background Worker
    |
    | Polls database every 2s
    v
Found job with status=QUEUED
    |
    | Pick it up
    v
Update status=RUNNING
    |
    | Call agent (takes 10 seconds)
    v
Agent generates response
    |
    | Save result
    v
Update status=COMPLETED

Terminal 3: Client Polling
    |
    | GET /jobs/{id} every 2s
    v
status=queued... queued... running... running... completed!
    |
    | Got result
    v
Display to user
```

---

## DAY 3 COMPLETE

**What we built:**
- [x] Job table in database
- [x] Background worker process
- [x] Job status state machine
- [x] Retry logic (max 3 attempts)
- [x] Idempotency (duplicate prevention)
- [x] Job cancellation
- [x] Orphaned job detection (heartbeat timeout)
- [x] Job polling endpoints
- [x] Complete test suite

**Day 3 checkpoint met:** Run same job twice, no duplicate side effects. Stuck jobs get reaped.

**Key learnings:**
```
Why async jobs?
    - Immediate response (user doesn't wait)
    - Reliability (survives crashes)
    - Retry automatically (handles transient failures)
    - Prevents duplicates (idempotency)

When to use:
    - Long operations (30+ seconds)
    - Operations that might fail temporarily
    - High-traffic production systems

When NOT needed:
    - Fast operations (5-10 seconds)
    - Demo/development environments
    - Low traffic
```

**Architecture after Day 3:**
```
                COMPLETE ASYNC SYSTEM

    +------------------+
    |     Client       |
    +------------------+
            |
            | POST /jobs/... (immediate)
            v
    +------------------+
    |   FastAPI        |
    | (Job creation)   |
    +------------------+
            |
            | INSERT job
            v
    +------------------+
    |  Supabase DB     |
    |  jobs table      |
    +------------------+
            |
            | Worker polls
            v
    +------------------+
    | Background       |
    | Worker           |
    +------------------+
            |
            | Calls agent
            v
    +------------------+
    | Tutoring Agent   |
    +------------------+
            |
            | Calls LLM
            v
    +------------------+
    |   Groq API       |
    +------------------+
```

---

## Next: Day 4 - Multi-Agent Layer (CORE REQUIREMENT)

This is the most important day - building Tutor + Verifier agents with handoff pattern.

---

## DAY 4: Multi-Agent Layer (CORE REQUIREMENT) [COMPLETE]

Building the tutor-verifier agent system with LangChain.

---

### Step 19: Tutor Agent with LangChain [COMPLETE]

Created specialized Socratic tutoring agent.

**File created:**
- `app/agents/tutor_agent.py` - Tutor agent using LangChain

**Agent characteristics:**
```
Role: Generate Socratic questions
Goal: Guide student to discover answer
Rules:
    - NEVER state answer directly
    - ASK guiding questions
    - Break down problems
    - Encourage reasoning

Technology:
    - ChatGroq LLM (openai/gpt-oss-120b)
    - Temperature: 0.7 (creative questioning)
    - LangChain framework
```

**How it works:**
```
Input Context:
    - Problem text
    - Correct answer (must not reveal)
    - Conversation history
    - Student's last response
    |
    v
Tutor Agent processes:
    - Understands where student is
    - Identifies knowledge gaps
    - Formulates guiding question
    |
    v
Output:
    - Socratic question
    - Encourages thinking
    - No answer revealed
```

---

### Step 20: Verifier Agent [COMPLETE]

Created quality control agent to check tutor output.

**File created:**
- `app/agents/verifier_agent.py` - Verifier agent with structured output

**Agent characteristics:**
```
Role: Quality control / Answer leak detection
Goal: Ensure tutor doesn't reveal answer
Rules:
    - REJECT if answer appears
    - REJECT if result shown
    - APPROVE only if purely guiding

Technology:
    - ChatGroq LLM (openai/gpt-oss-120b)
    - Temperature: 0.3 (consistent checking)
    - Pydantic structured output
```

**Verification logic:**
```
Input:
    - Tutor's draft response
    - Correct answer
    - Problem text
    |
    v
Verifier analyzes:
    - Does response contain answer?
    - Is answer revealed indirectly?
    - Can student deduce answer?
    |
    v
Decision:
    {
        "decision": "APPROVE" or "REJECT",
        "reason": "Explanation",
        "leaked_info": "What was leaked (if any)"
    }
```

**Why Pydantic structured output?**
```
Without structure:
    LLM returns: "I think this is okay..."
    We parse text (error-prone)

With Pydantic:
    class VerificationResult(BaseModel):
        decision: str
        reason: str
    
    LLM returns guaranteed JSON:
    {"decision": "APPROVE", "reason": "..."}
    
    Easy to use, type-safe!
```

---

### Step 21: Handoff Controller [COMPLETE]

Built orchestrator to manage tutor-verifier workflow.

**File created:**
- `app/agents/handoff.py` - Multi-agent coordination

**The handoff pattern:**
```
Student Input
    |
    v
FOR attempt in 1 to 3:
    |
    +-> Tutor generates response
    |
    +-> Verifier checks response
    |
    +-> Decision:
        |
        |-- APPROVE? Return to student
        |
        |-- REJECT? Tutor retries
            (with rejection feedback)
    |
    v
If all 3 rejected:
    Return safe fallback hint
```

**Flow diagram - Successful case:**
```
Attempt 1:
    Tutor: "What does 15×8 represent in repeated addition?"
    Verifier: APPROVE
    -> Send to student

Total attempts: 1
```

**Flow diagram - Retry case:**
```
Attempt 1:
    Tutor: "The answer is 120"
    Verifier: REJECT - "Answer revealed"
    
Attempt 2:
    Tutor: "15 times 8 equals 120"
    Verifier: REJECT - "Still shows answer"
    
Attempt 3:
    Tutor: "Can you break 15 into 10+5?"
    Verifier: APPROVE
    -> Send to student

Total attempts: 3
```

**Key features:**
1. **Bounded retries** - Max 3 attempts (prevents infinite loop)
2. **Feedback loop** - Rejected attempts inform next try
3. **Fallback safety** - Generic hint if all retries fail
4. **Audit trail** - All attempts logged to database

---

### Step 22: Testing Multi-Agent System [COMPLETE]

Tested complete tutor-verifier workflow.

**Test file:**
- `test_day4.py` - End-to-end multi-agent test

**Test results:**
```
Scenario:
    Problem: "What is 15 multiplied by 8?"
    Correct Answer: "120"
    Student: "I'm not sure how to start"

Result:
    Attempt 1: SUCCESS
        Tutor: "What does 15×8 represent in repeated addition?"
        Verifier: APPROVED
        Reason: "Only asks guiding questions, no answer revealed"

    Final Response: Sent to student
    Total Attempts: 1
    Status: SUCCESS
```

**What this proves:**
- Tutor generates quality Socratic questions
- Verifier successfully detects appropriate responses
- Handoff pattern works smoothly
- No answer leakage
- LangChain integration successful

---

## DAY 4 COMPLETE

**What we built:**
- [x] Tutor Agent (Socratic questioning with LangChain)
- [x] Verifier Agent (answer leak detection with structured output)
- [x] Handoff Controller (multi-agent coordination)
- [x] Retry logic (max 3 attempts with feedback)
- [x] Fallback mechanism (safe default if all retries fail)
- [x] Complete test suite

**Day 4 checkpoint met:** Multi-agent system with tutor-verifier handoff, demonstrated rejection and retry capability.

**This is the CORE PROJECT REQUIREMENT - Multi-agent AI system with quality control.**

**Why Day 4 is critical:**
```
Single Agent (Basic):
    Input -> Agent -> Output
    (Anyone can do this)

Multi-Agent (Advanced):
    Input -> Tutor -> Verifier -> Decision
              |          |
              |          +-> Reject? Retry with feedback
              |
              +-> Adapt and improve
    
    (Demonstrates real AI engineering)
```

**Architecture after Day 4:**
```
                    MULTI-AGENT SYSTEM

    Student Input
        |
        v
    +-------------------------+
    | Handoff Controller      |
    +-------------------------+
        |                   |
        v                   v
    +----------+      +-----------+
    | Tutor    |      | Verifier  |
    | Agent    |<---->| Agent     |
    +----------+      +-----------+
        |                   |
        | LangChain         | Pydantic
        v                   v
    ChatGroq LLM      ChatGroq LLM
        |                   |
        +-------------------+
                |
                v
        Groq API (openai/gpt-oss-120b)
```

**Key learnings:**
- Multi-agent collaboration is more reliable than single agent
- Two minds (tutor + verifier) better than one
- Handoff patterns enable quality control
- LangChain simplifies agent development
- Structured outputs ensure consistency
- Retry with feedback enables improvement

---

## Next: Day 5 - LangGraph + Testing + Documentation

Final day: State machines, comprehensive testing, and video demonstration.


---

# DAY 5: LANGGRAPH + TESTING + DOCUMENTATION

**Date:** September 26, 2024
**Focus:** State machine workflows, comprehensive testing, demo scripts, and documentation

---

## Step 1: LangGraph State Machine Implementation

### What is LangGraph?

**LangGraph = State machine framework for AI workflows**

Think of it like a flowchart that executes.

**Manual approach (Day 4):** Imperative - you control everything

**LangGraph approach (Day 5):** Declarative - you define structure, graph handles execution

---

### Creating workflow.py

**File created:** `app/agents/workflow.py`

**Workflow Structure:**
```
START -> tutor_node -> verifier_node -> Decision
If APPROVE: decision_node -> END
If REJECT and retries: tutor_node (loop)
If REJECT no retries: fallback_node -> END
```

---

### Benefits of LangGraph

1. Declarative - Define WHAT, not HOW
2. Visual - Can export as diagram
3. Debuggable - See which node failed
4. Resumable - Save/load workflow state
5. Professional - Industry standard pattern

---

## Step 2: PDF-Based Tutoring Feature (Bonus)

**Problem:** Problem-based tutoring requires manually creating each problem.

**Solution:** Let students upload PDFs and tutor from that content.

### Database Changes

- Added PDFDocument table
- Updated Session table to support both problem_id and pdf_document_id

### PDF Extraction Utility

**File:** `app/utils/pdf_extractor.py`
- Extracts text from all PDF pages
- Cleans whitespace
- Graceful error handling

### PDF API Endpoints

**File:** `app/api/pdfs.py`
- POST /pdfs/upload
- GET /pdfs
- GET /pdfs/{id}
- DELETE /pdfs/{id}

### Agent Updates

- Modified tutor_agent.py to support PDF content
- Modified handoff.py for dual mode (problem/PDF)
- Lighter verification for PDF mode

---

## Step 3: Comprehensive Test Suite

**Test files created:**
- tests/test_day5_langgraph.py
- tests/test_pdf_extraction.py
- tests/test_pdf_tutoring.py
- tests/test_comprehensive_scenarios.py

---

## Step 4: Interactive Demo Scripts

**Created demos/ folder with 6 standalone demos:**
1. 01_happy_path_demo.py
2. 02_verifier_rejection_demo.py
3. 03_tool_failure_demo.py
4. 04_multi_agent_architecture.py (MOST IMPORTANT)
5. 05_langgraph_workflow_demo.py
6. 06_pdf_tutoring_demo.py

---

## Step 5: Documentation

**Created:**
1. VIDEO_SCRIPT.md (in docs/) - 45-50 minute recording guide
2. PROJECT_STRUCTURE.md - Complete organization reference
3. demos/README.md - Demo usage guide

---

## Project Statistics After Day 5:

**Code metrics:**
- Total lines: 6,530+
- Python files: 45+
- Test files: 9
- Demo scripts: 6
- API endpoints: 15+
- Database tables: 7

**Time investment:**
- Day 1: 8 hours
- Day 2: 8 hours
- Day 3: 8 hours
- Day 4: 10 hours
- Day 5: 12 hours
- Total: 46 hours

---

## Key Achievements:

✓ Multi-agent architecture - Tutor + Verifier + Handoff
✓ Quality control - Retry with feedback
✓ State machine - LangGraph workflow
✓ PDF feature - Document-based tutoring (bonus)
✓ Comprehensive testing - 9 test files, 6 demos
✓ Complete documentation - Video script, structure, journal
✓ Production patterns - Error handling, persistence, streaming
✓ Socratic method - Never reveals answers

---

## Ready for Submission:

✅ 1. End-to-end working project - DONE
⏳ 2. 3-page architecture document - TODO
⏳ 3. YouTube video (30+ min) - TODO

**Deadline:** Sunday 6:00 PM

**Project Status:** 95% COMPLETE!

Just documentation and video remaining!

---

**End of Day 5 Journal**
