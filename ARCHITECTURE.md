# Socratic Tutoring System - Architecture Overview

---

## PAGE 1: Problem & System Architecture

### What problem does this solve?

Students often struggle with logic puzzles and programming problems not because they lack ability, but because traditional tutoring either gives away the answer too quickly or leaves them completely stuck. This system implements **Socratic questioning** - a teaching method where the tutor guides learning through carefully crafted questions rather than direct answers.

The goal: Build an AI tutor that asks the right questions at the right time, helping students discover solutions themselves while tracking their progress and maintaining conversation context.

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│                    (React + Material-UI)                            │
│                                                                     │
│   ┌──────────────┐        ┌──────────────┐                        │
│   │   Practice   │        │  PDF Upload  │                        │
│   │   Problems   │        │  & Study     │                        │
│   └──────┬───────┘        └──────┬───────┘                        │
└──────────┼───────────────────────┼─────────────────────────────────┘
           │                       │
           │  HTTP/JSON            │  FormData
           │                       │
┌──────────▼───────────────────────▼─────────────────────────────────┐
│                        FASTAPI BACKEND                              │
│                                                                     │
│  ┌──────────────────┐         ┌────────────────────┐              │
│  │  /sessions/start │         │  /pdfs/upload      │              │
│  │  /sessions/turn  │         │  /pdfs/sessions/   │              │
│  │  /problems       │         │       start        │              │
│  └────────┬─────────┘         └──────────┬─────────┘              │
│           │                              │                         │
│           └──────────┬───────────────────┘                         │
│                      │                                             │
│           ┌──────────▼───────────┐                                │
│           │   TutoringAgent      │                                │
│           │   (LangChain)        │                                │
│           └──────────┬───────────┘                                │
└──────────────────────┼─────────────────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
    ┌─────────┐  ┌─────────┐  ┌──────────┐
    │  Groq   │  │ Supabase│  │ PyPDF    │
    │   API   │  │ Postgres│  │ Parser   │
    │  (LLM)  │  │   (DB)  │  │          │
    └─────────┘  └─────────┘  └──────────┘
```

**Data Flow:**
1. User picks a problem or uploads a PDF
2. Frontend sends request to FastAPI
3. Backend creates session in database
4. Agent queries Groq LLM for Socratic question
5. Response stored in DB, sent back to UI
6. User answers → cycle repeats until correct or session ends

---

## PAGE 2: Data Model & Request Flow

### Database Schema (PostgreSQL/Supabase)

```
problems                               sessions
├─ id (PK)                            ├─ id (PK)
├─ topic                              ├─ problem_id (FK) → nullable
├─ difficulty                         ├─ pdf_document_id (FK) → nullable
├─ problem_text                       ├─ student_id
├─ correct_answer                     ├─ status (in_progress/completed)
└─ created_at                         ├─ started_at
                                      └─ ended_at
        ↓ 1:N                                  ↓ 1:N

                                      turns
pdf_documents                         ├─ id (PK)
├─ id (PK)                            ├─ session_id (FK)
├─ filename                           ├─ turn_number
├─ extracted_text                     ├─ speaker (tutor/student)
├─ uploaded_at                        └─ message
└─ file_path
```

**Key design decisions:**
- `problem_id` is nullable because PDF sessions don't have a predefined problem
- `turns` table captures full conversation history for both types of sessions
- `extracted_text` stores parsed PDF content for context retrieval

### API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/problems` | List all available practice problems |
| POST | `/sessions/start` | Start problem-based session |
| POST | `/sessions/{id}/turn` | Submit student answer, get next question |
| GET | `/sessions/{id}/transcript` | Retrieve full conversation |
| POST | `/pdfs/upload` | Upload & parse PDF document |
| POST | `/pdfs/sessions/start` | Start PDF-based tutoring session |

### Request Flow Example: Starting a Problem Session

**Step-by-step:**

```
1. Frontend: User clicks "Start" on Problem #3
   → POST /sessions/start { problem_id: 3, student_id: "alice" }

2. Backend validates:
   → Query: SELECT * FROM problems WHERE id = 3
   → Result: "Three people want to cross a bridge..."

3. Create session record:
   → INSERT INTO sessions (problem_id, student_id, status)
   → Returns session_id = 47

4. Initialize TutoringAgent:
   → Prompt: "Problem: <text>, Answer: <hidden>, generate first question"
   → Groq API call (model: llama-3.1-70b)

5. Agent generates: "Before we solve this, what constraints do we need to consider?"

6. Save to database:
   → INSERT INTO turns (session_id=47, turn_number=1, speaker='tutor', message=...)

7. Response to frontend:
   → { session_id: 47, first_question: "...", status: "in_progress" }

8. User types answer → POST /sessions/47/turn { student_answer: "..." }
   → Repeat steps 4-7 with conversation history included
```

**Performance optimization:** 
- Agent calls use template-based prompts (not multi-agent verification)
- Average response time: 2-3 seconds
- Database connection pooling handles concurrent sessions

---

## PAGE 3: Agent Architecture & LangGraph Flow

### The Core: TutoringAgent (LangChain-based)

The agent doesn't use a traditional multi-step graph. Instead, it's a **prompt-engineered LLM loop** that maintains Socratic principles through careful context management.

**Agent Components:**

```
┌─────────────────────────────────────────────────────────────┐
│                     TutoringAgent                           │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Conversation History (from database)              │   │
│  │  • All previous turns                              │   │
│  │  • Student's wrong attempts                        │   │
│  │  • Questions already asked                         │   │
│  └────────────┬───────────────────────────────────────┘   │
│               │                                            │
│               ▼                                            │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Prompt Construction                               │   │
│  │  1. Problem text + hidden answer                  │   │
│  │  2. Full conversation history                     │   │
│  │  3. Instruction: "ASK guiding questions,          │   │
│  │     DO NOT reveal answer"                         │   │
│  └────────────┬───────────────────────────────────────┘   │
│               │                                            │
│               ▼                                            │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Groq LLM Call                                     │   │
│  │  • Model: llama-3.1-70b-versatile                 │   │
│  │  • Temperature: 0.7 (creative but focused)        │   │
│  │  • Max iterations: 2 (fast response)              │   │
│  └────────────┬───────────────────────────────────────┘   │
│               │                                            │
│               ▼                                            │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Response Validation                               │   │
│  │  • Check: Did it ask a question?                  │   │
│  │  • Check: Did it avoid giving the answer?         │   │
│  │  • Fallback: Use template if validation fails    │   │
│  └────────────┬───────────────────────────────────────┘   │
│               │                                            │
│               ▼                                            │
│     Return Socratic Question                               │
└─────────────────────────────────────────────────────────────┘
```

### Why Not LangGraph?

**Original design** (Day 5) had a multi-agent system with LangGraph:
- TutorAgent → generates questions
- VerifierAgent → checks if answer was revealed
- HandoffController → orchestrates back-and-forth

**Problem:** This took 30+ seconds per turn and timed out frequently.

**Solution:** Simplified to single-agent with strict prompting. The Socratic constraint is enforced through:
1. Clear system instructions in every prompt
2. Conversation history showing pattern of questioning
3. Hidden answer clearly marked as "DO NOT REVEAL"

This reduced response time to 2-3 seconds with no loss in quality.

### PDF Tutoring Flow

When a user uploads a PDF, the flow differs slightly:

```
1. PDF Upload
   ↓
2. PyPDF extracts text
   ↓
3. Store in pdf_documents table
   ↓
4. Create session (pdf_document_id set, problem_id = NULL)
   ↓
5. Agent prompt includes PDF content as context:
   "You are tutoring using this study material: <extracted_text>"
   ↓
6. Student asks questions about the material
   ↓
7. Agent responds using Socratic method + PDF context
```

### Session Completion Logic

```python
# After each student turn:
if student_answer.lower() == correct_answer.lower():
    session.status = "completed"
    return "Excellent! You got it right!"
else:
    # Generate next Socratic question with history
    next_question = agent.run(prompt_with_history)
    return next_question
```

**Key insight:** The agent doesn't "know" when to stop. The backend compares the answer and explicitly ends the session. The agent's only job is asking good questions.

### Human-in-the-Loop

Every turn is human-driven:
- Agent never auto-generates multiple questions
- Student must respond before next question appears
- No autonomous loops or background processing
- Session persists across page refreshes (stored in DB)

This makes the system synchronous and predictable - important for a tutoring context where timing matters.

---

**Final Architecture Notes:**

The system prioritizes **speed and reliability** over complex agent orchestration. By keeping the AI layer simple (one agent, clear prompts, fast LLM) and pushing logic to the backend (answer checking, session management), we get:
- Consistent 2-3s response times
- No multi-agent coordination failures  
- Easy debugging (every turn logged in database)
- Scalable (stateless agent, state in DB)

The Socratic method works because the LLM is good at asking questions when explicitly instructed to do so. The architecture just needs to maintain context and enforce the "no direct answers" rule through prompting.
