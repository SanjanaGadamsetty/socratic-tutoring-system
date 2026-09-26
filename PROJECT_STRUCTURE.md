# Project Structure

## Directory Organization

```
socratic-tutoring-system/
│
├── .env                          # Environment variables (GROQ_API_KEY, DATABASE_URL)
├── .env.example                  # Example environment file
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── README.md                     # Project overview and setup instructions
├── PROJECT_STRUCTURE.md          # This file - project organization
│
├── About my project/             # Project documentation and planning
│   ├── PROJECT_JOURNAL.md        # Day-by-day development journal
│   ├── PROJECT_CHECKLIST.md      # Features and requirements checklist
│   └── Diagrams/                 # Architecture diagrams (draw.io)
│       ├── 1-Architecture-Diagram.drawio
│       ├── 2-Database-Schema.drawio
│       ├── 3-Agent-Sequence-Flow.drawio
│       └── 4-API-Endpoints.drawio
│
├── docs/                         # Documentation for submission
│   └── VIDEO_SCRIPT.md           # Complete 45-50 min video recording script
│
├── database/                     # Database layer
│   ├── __init__.py
│   ├── models.py                 # SQLAlchemy ORM models (7 tables)
│   ├── connection.py             # Database connection and session management
│   └── init_db.py                # Database initialization and seeding
│
├── app/                          # Application layer
│   ├── __init__.py
│   │
│   ├── agent.py                  # Day 1 - Single agent implementation
│   ├── worker.py                 # Day 3 - Background job worker
│   │
│   ├── agents/                   # Multi-agent system (Day 4-5)
│   │   ├── __init__.py
│   │   ├── tutor_agent.py        # Tutor agent - generates Socratic questions
│   │   ├── verifier_agent.py     # Verifier agent - checks for answer leaks
│   │   ├── handoff.py            # Handoff controller - orchestrates agents
│   │   └── workflow.py           # LangGraph state machine (Day 5)
│   │
│   ├── tools/                    # Agent tools
│   │   ├── __init__.py
│   │   └── basic_tools.py        # Calculator, check_answer, get_hint
│   │
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   └── pdf_extractor.py      # PDF text extraction (PyPDF)
│   │
│   └── api/                      # API layer (FastAPI)
│       ├── __init__.py
│       ├── main.py               # Main API application and core endpoints
│       ├── schemas.py            # Pydantic request/response models
│       ├── streaming.py          # Server-Sent Events (SSE) streaming
│       ├── jobs.py               # Background job endpoints
│       └── pdfs.py               # PDF upload/management endpoints
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_api.py               # API endpoint tests
│   ├── test_streaming.py         # SSE streaming tests
│   ├── test_day3.py              # Day 3 - Background jobs tests
│   ├── test_day4.py              # Day 4 - Multi-agent system tests
│   ├── test_day5_langgraph.py    # Day 5 - LangGraph workflow tests
│   ├── test_pdf_extraction.py    # PDF text extraction tests
│   ├── test_pdf_feature.py       # PDF upload API tests
│   ├── test_pdf_tutoring.py      # PDF-based tutoring tests
│   └── test_comprehensive_scenarios.py  # All edge cases
│
├── demos/                        # Interactive demo scripts for video
│   ├── README.md                 # Demo usage guide
│   ├── 01_happy_path_demo.py     # Normal successful operation
│   ├── 02_verifier_rejection_demo.py  # Retry mechanism
│   ├── 03_tool_failure_demo.py   # Error handling
│   ├── 04_multi_agent_architecture.py  # Multi-agent system (CORE)
│   ├── 05_langgraph_workflow_demo.py   # State machine (Day 5)
│   └── 06_pdf_tutoring_demo.py   # PDF feature (bonus)
│
├── uploads/                      # File uploads (created at runtime)
│   └── pdfs/                     # Uploaded PDF files
│
└── socratic_tutoring.db          # SQLite database (local development)
```

---

## Layer Architecture

### 1. Database Layer (`database/`)
**Purpose:** Data persistence and management

**Files:**
- `models.py` - 7 tables: Problem, Session, Turn, HintGiven, VerifierFlag, Job, PDFDocument
- `connection.py` - SQLAlchemy engine and session management
- `init_db.py` - Database creation and sample data seeding

**Connections:**
- Used by: API layer, Worker, Agents (for persistence)
- Database: PostgreSQL (Supabase) in production, SQLite for local dev

---

### 2. API Layer (`app/api/`)
**Purpose:** HTTP interface for client interactions

**Files:**
- `main.py` - Core endpoints (sessions, turns, problems)
- `streaming.py` - Real-time SSE streaming
- `jobs.py` - Background job management
- `pdfs.py` - PDF upload and management
- `schemas.py` - Request/response validation

**Connections:**
- Exposes: REST API on port 8000
- Uses: Database layer, Agent layer
- Provides: `/docs` interactive API documentation

---

### 3. Agent Layer (`app/agents/`) - THE CORE
**Purpose:** AI/ML logic - multi-agent Socratic tutoring

**Files:**
- `tutor_agent.py` - Generates Socratic questions (temp 0.7)
- `verifier_agent.py` - Checks for answer leaks (temp 0.3)
- `handoff.py` - Orchestrates tutor-verifier with retry (max 3)
- `workflow.py` - LangGraph state machine implementation

**Connections:**
- Used by: API endpoints
- Uses: Groq API (LLM), Tools, Database (for context)
- Pattern: Tutor → Verifier → Decision → Retry/Approve/Fallback

---

### 4. Tools Layer (`app/tools/`)
**Purpose:** Utilities for agents

**Files:**
- `basic_tools.py` - calculator, check_answer, get_hint

**Connections:**
- Used by: Agents
- Pattern: All tools return `{success: bool, ...}` for consistent error handling

---

### 5. Utils Layer (`app/utils/`)
**Purpose:** Shared utilities

**Files:**
- `pdf_extractor.py` - PDF text extraction with PyPDF

**Connections:**
- Used by: PDF API endpoints, PDF tutoring

---

## Key Design Patterns

### 1. Multi-Agent Pattern
```
Student Input → Tutor (draft) → Verifier (check) → Decision
                     ↓ REJECT           ↓ APPROVE
                Add feedback        Send to student
                     ↓
                Retry (max 3)
                     ↓
              Fallback if all fail
```

### 2. Retry with Feedback
- Attempt 1: Tutor generates
- Verifier: REJECT + reason
- Attempt 2: Tutor generates (with rejection reason as context)
- Verifier: Still REJECT + reason
- Attempt 3: Tutor is extra careful
- Verifier: APPROVE or use fallback

### 3. State Machine (LangGraph)
```
Nodes:
  - tutor_node: Generate response
  - verifier_node: Check quality
  - decision_node: Finalize if approved
  - fallback_node: Safe generic response

Edges:
  - tutor → verifier (always)
  - verifier → decision (if APPROVE)
  - verifier → tutor (if REJECT and retries left)
  - verifier → fallback (if REJECT and no retries)
```

### 4. Graceful Error Handling
All tools return:
```python
{
  "success": bool,
  "result": Any,        # if success
  "error": str          # if not success
}
```

Agents receive errors as observations, not crashes.

---

## Data Flow Examples

### Example 1: Start Session
```
Client → POST /sessions/start
  ↓
API validates request (schemas.py)
  ↓
Create Session in DB (models.py)
  ↓
Return session_id
```

### Example 2: Submit Turn (Multi-Agent)
```
Client → POST /sessions/{id}/turn
  ↓
API receives student response
  ↓
HandoffController.process_student_input()
  ↓
Loop (max 3 attempts):
  TutorAgent.generate_response()
    → Uses LLM, gets context from DB
  VerifierAgent.verify()
    → Uses LLM, checks for answer leaks
  If APPROVE: break
  If REJECT: add feedback, retry
  ↓
Save Turn to DB (speaker: TUTOR, message: response)
  ↓
Return response to client
```

### Example 3: PDF Tutoring
```
Client → POST /pdfs/upload (multipart form)
  ↓
Save PDF file to uploads/pdfs/
  ↓
pdf_extractor.extract_text_from_pdf()
  ↓
Create PDFDocument in DB (with extracted_text)
  ↓
Client → POST /sessions/start (with pdf_id)
  ↓
Session linked to PDF
  ↓
Client → POST /sessions/{id}/turn
  ↓
HandoffController gets PDF text from DB
  ↓
TutorAgent gets pdf_content as context (not problem/answer)
  ↓
Generates question based on PDF
```

---

## File Naming Conventions

- **snake_case** for Python files: `tutor_agent.py`
- **PascalCase** for classes: `TutorAgent`, `HandoffController`
- **snake_case** for functions: `generate_response()`, `extract_text_from_pdf()`
- **UPPER_CASE** for constants: `MAX_RETRIES`, `UPLOAD_DIR`
- **Test files**: `test_*.py` pattern
- **Demo files**: `XX_descriptive_name_demo.py` pattern

---

## Running the System

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your GROQ_API_KEY and DATABASE_URL

# Initialize database
python database/init_db.py
```

### 2. Run API Server
```bash
uvicorn app.api.main:app --reload
```
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### 3. Run Background Worker (Day 3)
```bash
python app/worker.py
```

### 4. Run Tests
```bash
# Individual tests
python tests/test_day4.py
python tests/test_day5_langgraph.py

# All tests
python -m pytest tests/
```

### 5. Run Demos (for video)
```bash
python demos/01_happy_path_demo.py
python demos/04_multi_agent_architecture.py
# ... etc
```

---

## Tech Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **LLM** | Groq API (OpenAI GPT) | Language model for agents |
| **Agent Framework** | LangChain | Tool calling, output parsing, agent orchestration |
| **Workflow** | LangGraph | State machine for multi-agent workflows |
| **API** | FastAPI | REST API and SSE streaming |
| **Database** | PostgreSQL (Supabase) | Production persistence |
| **Local DB** | SQLite | Local development |
| **ORM** | SQLAlchemy | Object-relational mapping |
| **Validation** | Pydantic | Request/response validation |
| **PDF** | PyPDF | PDF text extraction |
| **Environment** | python-dotenv | Environment variable management |

---

## Development Timeline

- **Day 1:** Agent fundamentals, tool implementation, error recovery
- **Day 2:** Database schema, API endpoints, SSE streaming
- **Day 3:** Background jobs, durable execution, idempotency
- **Day 4:** Multi-agent system (Tutor + Verifier + Handoff)
- **Day 5:** LangGraph workflow, comprehensive testing, PDF feature

**Total:** 6,530+ lines of production code

---

## Key Files for Video Demo

When recording your video, focus on these files:

1. **Architecture:** `About my project/Diagrams/1-Architecture-Diagram.drawio`
2. **Database:** `database/models.py` (lines 52-238)
3. **Tutor Agent:** `app/agents/tutor_agent.py` (lines 21-92)
4. **Verifier Agent:** `app/agents/verifier_agent.py` (lines 24-160)
5. **Handoff:** `app/agents/handoff.py` (lines 16-149)
6. **LangGraph:** `app/agents/workflow.py` (lines 15-177)
7. **API:** `app/api/main.py` (lines 35-54 for setup)
8. **Tools:** `app/tools/basic_tools.py` (all functions)

See `docs/VIDEO_SCRIPT.md` for complete recording guide.

---

## Notes

- `.env` contains secrets - never commit (in .gitignore)
- `socratic_tutoring.db` is local only - production uses Supabase
- `uploads/` is created at runtime - in .gitignore
- All test files are standalone - can run independently
- Demo scripts pause for user input - perfect for video recording
