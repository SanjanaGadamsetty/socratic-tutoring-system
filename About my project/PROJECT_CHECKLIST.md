# 📋 Socratic Tutoring System - Complete Project Checklist

**Project Goal:** Build a multi-agent tutoring system with Socratic questioning, tutor-verifier handoff, and error recovery.

---

## 🎯 DAY 1 - Agent Fundamentals ✅ COMPLETE

### Core Agent System
- [x] Project scaffold (folders, environment, dependencies)
- [x] Create `.env` file with API keys
- [x] Install requirements (`groq`, `python-dotenv`, `pydantic`)
- [x] Design database schema (sketch)
- [x] Create architecture diagrams

### Tools Implementation
- [x] Build 3 basic tools:
  - [x] `calculator()` - exact math calculations
  - [x] `check_answer()` - compare student vs correct answer
  - [x] `get_hint()` - hint escalation (levels 1-3)
- [x] Tool registry system
- [x] Error recovery in tools (return error, don't crash)

### Agent Loop
- [x] Build agent without framework (manual loop)
- [x] Think-Act-Observe pattern
- [x] Tool selection logic
- [x] Tool execution with error handling
- [x] Self-healing: failed tool → observation → retry

### Testing & Validation
- [x] Command-line runnable agent
- [x] Complete one full task using 2+ tools
- [x] Demonstrate error recovery (one deliberate failure)

### Documentation
- [x] README.md with project overview
- [x] PROJECT_JOURNAL.md tracking progress
- [x] GitHub repository setup
- [x] Initial commit pushed

**Day 1 Checkpoint:** ✅ Working agent from CLI that uses tools and recovers from errors

---

## 🗄️ DAY 2 - Tools, Service & Schema

### Database Design & Implementation
- [ ] Finalize database schema (5 tables):
  - [ ] `problems` table (id, title, problem_text, correct_answer, topic, difficulty)
  - [ ] `sessions` table (id, problem_id, student_id, status, started_at, ended_at)
  - [ ] `turns` table (id, session_id, turn_number, speaker, message, timestamp)
  - [ ] `hints_given` table (id, session_id, hint_level, hint_text, given_at)
  - [ ] `verifier_flags` table (id, session_id, turn_id, rejected_message, reason, flagged_at)
- [ ] Create database connection module
- [ ] Write SQLAlchemy models for all tables
- [ ] Create migration/setup script
- [ ] Add foreign key constraints
- [ ] Seed database with sample problems (5-10 problems)

### HTTP API Service
- [ ] Set up FastAPI application structure
- [ ] Create API endpoints:
  - [ ] `POST /sessions/start` - start new tutoring session
  - [ ] `POST /sessions/{id}/turn` - submit student answer, get next question
  - [ ] `GET /sessions/{id}/transcript` - get full conversation history
- [ ] Add request/response models (Pydantic schemas)
- [ ] Input validation on all endpoints
- [ ] Error handling middleware

### Structured Outputs & Validation
- [ ] Create Pydantic models for agent responses
- [ ] Validate tool outputs before returning
- [ ] Invalid output → feedback to model (not crash)
- [ ] Structured logging for debugging

### Real-Time Streaming
- [ ] Implement Server-Sent Events (SSE)
- [ ] Stream tool-call events in real-time
- [ ] Stream agent thinking process
- [ ] Test streaming from client perspective

### Incremental Persistence
- [ ] Save conversation state after each turn (not just at end)
- [ ] Track session status in real-time
- [ ] Handle partial session recovery

**Day 2 Checkpoint:** ✅ HTTP API backed by database, with SSE streaming tool events

---

## 🔄 DAY 3 - Durable Execution

### Background Job System
- [ ] Move agent runs to background (non-blocking)
- [ ] Implement job queue (database-backed)
- [ ] Create job status state machine:
  - [ ] `queued` → `running` → `completed` / `failed`
- [ ] Add job status endpoint: `GET /jobs/{id}/status`

### Worker & Heartbeat System
- [ ] Create worker process to execute jobs
- [ ] Implement worker heartbeat mechanism
- [ ] Orphaned job detection (worker died mid-execution)
- [ ] Job reaping/cleanup for stuck jobs

### Idempotency
- [ ] Implement idempotency at tool-call level
- [ ] Idempotency keys for API requests
- [ ] Prevent double-charging, double-booking, double-sending
- [ ] Retrying a run doesn't duplicate side effects

### Retry Logic & Cost Awareness
- [ ] Smart retry semantics (don't retry completed expensive actions)
- [ ] Distinguish retriable vs non-retriable errors
- [ ] Track tool execution costs (if applicable)
- [ ] Maximum retry limits per job

### Cancellation & Dead Letters
- [ ] Job cancellation endpoint: `POST /jobs/{id}/cancel`
- [ ] Never interrupt tool mid-execution
- [ ] Dead-letter queue for permanently failed jobs
- [ ] Manual retry from dead-letter queue

**Day 3 Checkpoint:** ✅ Run same job twice, no duplicate side effects. Show stuck job gets reaped.

---

## 🤖 DAY 4 - LangChain / Multi-Agent Layer

### LangChain Integration
- [ ] Install LangChain packages (`langchain`, `langchain-groq`)
- [ ] Convert tools to LangChain tool format
- [ ] Create LangChain agent with tool-calling
- [ ] Implement output parsers
- [ ] Add conversation memory

### Tutor Agent (LangChain)
- [ ] Create dedicated Tutor agent
- [ ] System prompt: Socratic questioning, never give direct answers
- [ ] Tool access: calculator, check_answer, get_hint
- [ ] Generate guiding questions
- [ ] Track hint escalation

### Verifier Agent (LangChain)
- [ ] Create dedicated Verifier agent
- [ ] System prompt: check if tutor leaked answer
- [ ] Access to problem + correct answer
- [ ] Return: approve/reject + reason
- [ ] Flag specific phrases that leak answers

### Multi-Agent Handoff Pattern
- [ ] Implement agent-to-agent handoff
- [ ] Tutor drafts response → Verifier checks → decision
- [ ] Bounded retry loop (max 3 attempts)
- [ ] If 3 rejections → fallback to generic hint

### Business Rules Externalization
- [ ] Move policies to database/config (not hardcoded in prompts):
  - [ ] Maximum retries (3)
  - [ ] Hint levels (1-3)
  - [ ] Rejection reasons
  - [ ] Allowed phrases
- [ ] Make rules editable without code changes

### Parallel Agent Execution (if needed)
- [ ] Fan-out to multiple verifiers (if multi-dimensional checking)
- [ ] Per-task timeouts
- [ ] Merge results with partial failure reporting

**Day 4 Checkpoint:** ✅ LangChain agents run end-to-end. Multi-agent handoff works. Show one rejection → retry.

---

## 🕸️ DAY 5 - LangGraph, Testing, Documentation & Demo

### LangGraph Workflow
- [ ] Install LangGraph (`langgraph`)
- [ ] Design state graph with nodes:
  - [ ] `tutor_turn` node - generates question
  - [ ] `verify` node - checks for answer leakage
  - [ ] `student_response` node - receives student input
- [ ] Define edges:
  - [ ] `tutor_turn` → `verify`
  - [ ] `verify` → (approve) → `send` → `student_response`
  - [ ] `verify` → (reject) → `tutor_turn` (retry, max 3)
  - [ ] `student_response` → `tutor_turn` (loop)
- [ ] Implement conditional branching (approve/reject logic)
- [ ] Add cycle detection (prevent infinite loops)
- [ ] Human-in-the-loop interrupt points (if student quits)

### State Management
- [ ] Define state schema (session state, turn count, retry count)
- [ ] Persist state to database
- [ ] Resume from checkpoint (if session interrupted)

### Testing Suite
- [ ] Test 1: Normal successful run (student solves problem)
- [ ] Test 2: Failure and recovery (verifier rejects → retry succeeds)
- [ ] Test 3: Edge case - max retries hit, fallback triggered
- [ ] Test 4: API endpoint integration tests
- [ ] Test 5: Database CRUD operations

### Code Quality
- [ ] Clean up debug print statements
- [ ] Add type hints throughout
- [ ] Format code consistently
- [ ] Remove unused imports
- [ ] Update requirements.txt with all dependencies

### Documentation - 3-Page Flow Doc
- [ ] **Page 1: Problem & Architecture**
  - [ ] One paragraph problem statement
  - [ ] Architecture diagram (client → API → agents → DB → LLM)
  - [ ] Data flow arrows
- [ ] **Page 2: Data & Control Flow**
  - [ ] Database schema diagram
  - [ ] API endpoint table
  - [ ] Request/response flow walkthrough
- [ ] **Page 3: Agent/LangGraph Flow**
  - [ ] LangGraph node-edge diagram
  - [ ] Tutor → Verifier handoff visualization
  - [ ] Retry loop logic
  - [ ] Where human-in-the-loop happens

### Final README Update
- [ ] Setup instructions (how to run locally)
- [ ] Environment variables needed
- [ ] Database setup steps
- [ ] Run commands
- [ ] Testing commands
- [ ] Troubleshooting section

**Day 5 Checkpoint:** ✅ Full project runs locally end-to-end. All 3 deliverables ready. Video recorded.

---

## 🎁 BONUS FEATURE - PDF Upload & RAG

### PDF Processing
- [ ] Install PDF packages (`pypdf2`, `sentence-transformers`, `chromadb`)
- [ ] Create `POST /documents/upload` endpoint
- [ ] Extract text from PDF (handle multi-page)
- [ ] Chunk text into semantic sections
- [ ] Generate embeddings for chunks
- [ ] Store in vector database (ChromaDB)

### Document Table
- [ ] Add `documents` table (id, student_id, filename, upload_date)
- [ ] Add `document_chunks` table (id, document_id, chunk_text, embedding, chunk_index)

### PDF-Based Sessions
- [ ] Create `POST /sessions/start-from-pdf` endpoint
- [ ] Accept: document_id + student_question
- [ ] Retrieve relevant chunks via semantic search
- [ ] Pass chunks as context to tutor + verifier
- [ ] Conduct normal Socratic dialogue based on PDF content

### Testing PDF Feature
- [ ] Upload sample PDF (e.g., math textbook chapter)
- [ ] Ask question about PDF content
- [ ] Verify tutor uses PDF context
- [ ] Verify verifier checks against PDF content

**Bonus Checkpoint:** ✅ Student uploads PDF, asks question, gets tutored on PDF content

---

## 🎬 FINAL DELIVERABLES

### 1. Working Project
- [ ] Full system runnable locally
- [ ] All core features working
- [ ] Database populated with sample data
- [ ] API accessible via Postman/curl
- [ ] LangGraph workflow executing
- [ ] Tutor-Verifier handoff demonstrated
- [ ] Error recovery demonstrated
- [ ] PDF feature working (bonus)

### 2. Architecture Documentation (3 pages)
- [ ] Page 1: Architecture diagram + problem statement
- [ ] Page 2: Database schema + API endpoints + flow
- [ ] Page 3: LangGraph agent workflow
- [ ] Diagrams are clear and professional
- [ ] Document is concise (max 3 pages)

### 3. Demo Video (30+ minutes on YouTube)
- [ ] **Introduction (2-3 min)**
  - [ ] Problem explanation
  - [ ] Why it's real-world relevant
  - [ ] Approach summary
- [ ] **Architecture Walkthrough (5-7 min)**
  - [ ] Walk through diagrams
  - [ ] Explain agent loop, tools, LangChain, LangGraph
  - [ ] Design choices explained
- [ ] **Live Demo (10-15 min)**
  - [ ] Run system live (not recording of recording)
  - [ ] Happy path: student solves problem
  - [ ] Trigger failure: verifier rejects tutor (show retry)
  - [ ] Show error recovery
  - [ ] Show PDF feature (bonus)
- [ ] **Code Walkthrough (5-8 min)**
  - [ ] Show agent loop code
  - [ ] Show LangGraph graph definition
  - [ ] Show key tools
  - [ ] Show database schema
- [ ] **Wrap-up (2-3 min)**
  - [ ] What was hardest
  - [ ] What you'd do differently
  - [ ] Summary of layers (DB, backend, AI)
- [ ] Video is 30+ minutes
- [ ] Uploaded to YouTube (unlisted OK)
- [ ] Link is shareable

### GitHub Repository
- [ ] Clean, organized folder structure
- [ ] README with setup instructions
- [ ] All code committed
- [ ] No secrets in repo (.env in .gitignore)
- [ ] Requirements.txt complete
- [ ] Architecture diagrams included

---

## 📊 PROGRESS TRACKER

**Overall Progress:** Day 1 Complete ✅ (20% done)

- [x] Day 1 - Agent Fundamentals (100% ✅)
- [ ] Day 2 - Database & API (0%)
- [ ] Day 3 - Durable Execution (0%)
- [ ] Day 4 - LangChain Multi-Agent (0%)
- [ ] Day 5 - LangGraph & Testing (0%)
- [ ] Bonus - PDF Feature (0%)
- [ ] Final Deliverables (0%)

---

## 🎯 CURRENT FOCUS

**Next up:** Day 2 - Database & API Layer

**Key tasks:**
1. Set up PostgreSQL database
2. Create 5 tables with SQLAlchemy
3. Build FastAPI endpoints
4. Implement SSE streaming
5. Test full request/response cycle

---

## 📝 NOTES & DECISIONS

- Using **Groq API** with `openai/gpt-oss-120b` model
- Using **SQLAlchemy** for database ORM
- Using **FastAPI** for HTTP API
- Using **Server-Sent Events** for streaming
- **No attribution** in git commits (per user preference)
- PDF feature is **bonus** (do after core features)

---

**Keep this checklist updated as you progress!** ✅ = Done | ⏳ = In Progress | ❌ = Blocked
