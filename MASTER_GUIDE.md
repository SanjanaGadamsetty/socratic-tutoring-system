# MASTER GUIDE - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack Deep Dive](#technology-stack-deep-dive)
3. [Complete File Structure](#complete-file-structure)
4. [Database Architecture](#database-architecture)
5. [Backend Architecture](#backend-architecture)
6. [Frontend Architecture](#frontend-architecture)
7. [Code Flow & Dependencies](#code-flow--dependencies)
8. [Building From Scratch](#building-from-scratch)
9. [How Everything Connects](#how-everything-connects)

---

## Project Overview

### What This App Does
A Socratic tutoring system where:
1. Students solve math problems OR upload PDFs (study materials)
2. AI tutor asks guiding questions (never gives direct answers)
3. Multi-agent system ensures quality (Tutor + Verifier)
4. Everything stored in PostgreSQL database

### Why Each Technology Was Chosen

**Frontend - React + Material-UI:**
- React: Component-based, easy to manage state
- Material-UI: Pre-built components (buttons, cards, text fields)
- Yellow theme: Custom requirement for this project
- Vite: Fast build tool, faster than Create React App

**Backend - FastAPI:**
- FastAPI: Python web framework, automatic API docs
- Async support: Can handle multiple requests simultaneously
- Type hints: Catches errors before runtime

**AI - LangChain + Groq:**
- LangChain: Framework for building AI agents
- LangGraph: State machine for multi-agent workflows
- Groq: Fast LLM inference (faster than OpenAI)

**Database - PostgreSQL (Supabase):**
- PostgreSQL: Reliable, supports complex queries
- Supabase: Hosted PostgreSQL (free tier)
- SQLAlchemy: ORM (write Python instead of SQL)

---

## Technology Stack Deep Dive

### Complete Dependency Chain

```
User's Browser
    ↓ HTTP Requests
React Frontend (Vite + Material-UI)
    ↓ Axios HTTP calls (http://localhost:8000)
FastAPI Backend (Python)
    ↓ SQLAlchemy queries
PostgreSQL Database (Supabase)
    
FastAPI Backend also calls:
    ↓ LangChain
Groq API (LLM)
    ↓ Returns text
LangChain processes
    ↓ Returns to FastAPI
FastAPI sends to Frontend
```

### Why This Stack?

**Problem:** Need AI tutoring that doesn't give away answers
**Solution:** Multi-agent system (one generates, one verifies)

**Problem:** Need persistent storage of conversations
**Solution:** PostgreSQL database with proper schema

**Problem:** Need modern UI with custom colors
**Solution:** React + Material-UI (yellow theme)

**Problem:** Need fast AI responses
**Solution:** Groq API (optimized for speed)

---

## Complete File Structure

### Root Directory Files

#### `.env` (Environment Variables)
```
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:pass@host:port/db
```

**Purpose:** Store secrets (API keys, database credentials)
**Why:** Never commit secrets to Git
**When Used:** Loaded at app startup by python-dotenv
**Dependencies:** None (root level)

#### `.env.example` (Template)
**Purpose:** Shows what environment variables are needed
**Why:** Developers know what to add to their `.env`
**Dependencies:** None

#### `.gitignore` (Git Ignore Rules)
```python
# Key entries:
venv/              # Python virtual environment (huge, auto-generated)
node_modules/      # NPM packages (huge, auto-generated)
.env               # Secrets (never commit!)
__pycache__/       # Python cache files
uploads/pdfs/      # User uploaded files
*.db               # Local database files
```

**Purpose:** Tell Git which files to NOT track
**Why:** Avoid committing secrets, large files, auto-generated files
**Dependencies:** None

#### `requirements.txt` (Python Dependencies)
```
groq                    # AI LLM client
langchain>=0.3.0        # AI agent framework
langchain-groq          # Groq integration for LangChain
langgraph               # Multi-agent state machine
fastapi>=0.104          # Web framework
uvicorn>=0.24           # ASGI server (runs FastAPI)
sqlalchemy>=2.0         # ORM (database)
psycopg2-binary>=2.9    # PostgreSQL driver
python-multipart        # File upload support
pypdf>=6.0              # PDF text extraction
pydantic>=2.0           # Data validation
python-dotenv           # Load .env files
requests>=2.31          # HTTP client
gunicorn>=21.0          # Production server
sse-starlette>=1.8      # Server-sent events
```

**Purpose:** List all Python packages needed
**Why:** `pip install -r requirements.txt` installs everything
**How:** Run `pip install -r requirements.txt`
**Dependencies:** Python 3.9+

#### `render.yaml` (Deployment Configuration)
```yaml
services:
  - type: web
    name: socratic-tutor-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app.api.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

**Purpose:** Tells Render how to deploy backend
**Why:** Automated deployment from Git push
**When Used:** Only in production (Render platform)
**Dependencies:** requirements.txt, app/api/main.py

---

## Database Architecture

### Database Schema (SQLAlchemy Models)

File: `database/models.py`

#### Table 1: `problems`
```python
class Problem(Base):
    __tablename__ = "problems"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    problem_text = Column(Text, nullable=False)
    correct_answer = Column(String(255), nullable=False)
    topic = Column(String(255))
    difficulty = Column(Enum(DifficultyLevel))
```

**Purpose:** Store math problems
**Why:** Need problems for students to solve
**Relationships:** 
- One Problem → Many Sessions (one problem can be attempted multiple times)

**Example Data:**
```sql
INSERT INTO problems (title, problem_text, correct_answer, topic, difficulty)
VALUES ('Basic Multiplication', 'What is 15 multiplied by 8?', '120', 'Mathematics - Multiplication', 'easy');
```

#### Table 2: `sessions`
```python
class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=True)
    pdf_document_id = Column(Integer, ForeignKey("pdf_documents.id"), nullable=True)
    student_id = Column(String(255), nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.IN_PROGRESS)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
```

**Purpose:** Track tutoring sessions
**Why:** Need to know who's learning what and when
**Relationships:**
- Many Sessions → One Problem (many attempts of same problem)
- Many Sessions → One PDF (many sessions on same PDF)
- One Session → Many Turns (conversation within session)

**Key Constraint:** 
- Either `problem_id` OR `pdf_document_id` must be set (not both)
- `problem_id` can be NULL (for PDF sessions)

#### Table 3: `turns`
```python
class Turn(Base):
    __tablename__ = "turns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    turn_number = Column(Integer, nullable=False)
    speaker = Column(Enum(Speaker), nullable=False)  # STUDENT or TUTOR
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Purpose:** Store conversation history
**Why:** Need to show past messages, provide context to AI
**Relationships:**
- Many Turns → One Session (many messages in a conversation)

**Example Flow:**
```
Turn 1: TUTOR says "What do you know about multiplication?"
Turn 2: STUDENT says "It's repeated addition"
Turn 3: TUTOR says "Correct! So how would you solve 15 × 8?"
Turn 4: STUDENT says "120"
Turn 5: TUTOR says "Excellent!"
```

#### Table 4: `pdf_documents`
```python
class PDFDocument(Base):
    __tablename__ = "pdf_documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    description = Column(Text)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(String(500), nullable=False)
    extracted_text = Column(Text, nullable=False)
    page_count = Column(Integer)
    file_size = Column(Integer)
    uploaded_by = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
```

**Purpose:** Store uploaded PDF metadata and extracted text
**Why:** Need to reference PDF content for tutoring
**Relationships:**
- One PDF → Many Sessions (same PDF used multiple times)

**Key Fields:**
- `filename`: UUID name on server (abc-123.pdf)
- `original_filename`: User's filename (biology_notes.pdf)
- `extracted_text`: Full text from PDF (used by AI)
- `file_path`: Where file is stored (uploads/pdfs/abc-123.pdf)

#### Table 5: `hints_given`
```python
class HintGiven(Base):
    __tablename__ = "hints_given"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    turn_id = Column(Integer, ForeignKey("turns.id"))
    hint_text = Column(Text, nullable=False)
    hint_type = Column(String(50))
```

**Purpose:** Track when hints are given
**Why:** Monitor how much help student needed
**Relationships:**
- Many Hints → One Session

#### Table 6: `verifier_flags`
```python
class VerifierFlag(Base):
    __tablename__ = "verifier_flags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    turn_id = Column(Integer, ForeignKey("turns.id"))
    rejected_response = Column(Text)
    rejection_reason = Column(Text)
    flagged_at = Column(DateTime, default=datetime.utcnow)
```

**Purpose:** Log when verifier rejects tutor's response
**Why:** Quality control - track when answers leak
**Relationships:**
- Many Flags → One Session

### Database Connection Flow

File: `database/connection.py`

```python
# 1. Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Fix URL for psycopg2 driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# 3. Create engine (connection to database)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Check if connection is alive before using
    pool_size=10,        # Keep 10 connections ready
    max_overflow=20      # Allow 20 extra connections if needed
)

# 4. Create session factory
SessionLocal = sessionmaker(
    autocommit=False,    # Manual commit (safer)
    autoflush=False,     # Manual flush (more control)
    bind=engine
)

# 5. Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db  # Give database session to endpoint
    finally:
        db.close()  # Always close when done
```

**Why This Design:**
- `pool_pre_ping`: Prevents "connection already closed" errors
- `pool_size`: Keeps connections ready (faster requests)
- `get_db()`: FastAPI dependency injection (automatic cleanup)

**When Used:**
- Every API endpoint that needs database access
- Example: `def some_endpoint(db: Session = Depends(get_db)):`

### Database Initialization

File: `database/init_db.py`

```python
def create_tables():
    """Create all tables defined in models.py"""
    Base.metadata.create_all(bind=engine)

def seed_sample_problems():
    """Add 7 sample math problems"""
    problems = [
        Problem(title="Basic Multiplication", ...),
        Problem(title="Fraction Addition", ...),
        # ... 5 more
    ]
    db.add_all(problems)
    db.commit()
```

**Purpose:** Initialize database from scratch
**When Used:** First time setup OR when database is empty
**How to Run:** `python database/init_db.py`

**Dependencies:**
- database/models.py (table definitions)
- database/connection.py (engine)
- .env (DATABASE_URL)

---

## Backend Architecture

### Main API Application

File: `app/api/main.py`

**Purpose:** Core FastAPI application - defines all HTTP endpoints

#### Imports & Setup
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

app = FastAPI(
    title="Socratic Tutoring System API",
    version="1.0.0"
)
```

**Why FastAPI:** 
- Automatic API documentation (Swagger UI at /docs)
- Type hints = automatic validation
- Async support for better performance

#### CORS Middleware
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Purpose:** Allow frontend (different port) to call backend
**Why:** Browser blocks cross-origin requests by default
**Production:** Change `["*"]` to specific frontend URL

**CORS Flow:**
1. Frontend (port 5173) calls backend (port 8000)
2. Browser sends OPTIONS request first (preflight)
3. Backend responds with CORS headers
4. Browser allows actual request

#### Endpoint 1: List Problems

```python
@app.get("/problems", response_model=ProblemsListResponse)
def list_problems(db: Session = Depends(get_db)):
    problems = db.query(Problem).all()
    return ProblemsListResponse(
        problems=[ProblemResponse.from_orm(p) for p in problems],
        total=len(problems)
    )
```

**Purpose:** Get all available problems
**HTTP Method:** GET
**URL:** http://localhost:8000/problems
**Response:**
```json
{
  "problems": [
    {
      "id": 1,
      "title": "Basic Multiplication",
      "problem_text": "What is 15 multiplied by 8?",
      "topic": "Mathematics - Multiplication",
      "difficulty": "easy"
    }
  ],
  "total": 7
}
```

**Dependencies:**
- database/models.py (Problem model)
- database/connection.py (get_db)
- app/api/schemas.py (ProblemsListResponse)

**When Called:** Frontend loads problem selector component

#### Endpoint 2: Start Session

```python
@app.post("/sessions/start", response_model=SessionStartResponse, status_code=201)
def start_session(request: SessionStartRequest, db: Session = Depends(get_db)):
    # 1. Validate input
    if not request.problem_id and not request.pdf_document_id:
        raise HTTPException(400, "Must provide problem_id or pdf_document_id")
    
    # 2. Get problem or PDF from database
    if request.problem_id:
        problem = db.query(Problem).filter(Problem.id == request.problem_id).first()
        if not problem:
            raise HTTPException(404, "Problem not found")
    
    if request.pdf_document_id:
        pdf_doc = db.query(PDFDocument).filter(PDFDocument.id == request.pdf_document_id).first()
        if not pdf_doc:
            raise HTTPException(404, "PDF not found")
    
    # 3. Create session in database
    session = DBSession(
        problem_id=request.problem_id,
        pdf_document_id=request.pdf_document_id,
        student_id=request.student_id,
        status=SessionStatus.IN_PROGRESS
    )
    db.add(session)
    db.commit()
    
    # 4. Generate first question using AI
    if problem:
        topic_words = problem.topic.split()[-1]
        first_question = f"Let's work through this together! Before we start, what do you already know about {topic_words}?"
    else:
        first_question = "I see you've uploaded study material. What topic from this document would you like to explore first?"
    
    # 5. Save first turn (tutor's question)
    turn = Turn(
        session_id=session.id,
        turn_number=1,
        speaker=Speaker.TUTOR,
        message=first_question
    )
    db.add(turn)
    db.commit()
    
    # 6. Return response
    return SessionStartResponse(
        session_id=session.id,
        problem=ProblemResponse.from_orm(problem),
        first_question=first_question,
        status=session.status
    )
```

**Purpose:** Start a new tutoring session
**HTTP Method:** POST
**URL:** http://localhost:8000/sessions/start
**Request Body:**
```json
{
  "problem_id": 1,
  "student_id": "alice"
}
```
**Response:**
```json
{
  "session_id": 79,
  "problem": {
    "id": 1,
    "title": "Basic Multiplication",
    "problem_text": "What is 15 multiplied by 8?",
    "difficulty": "easy"
  },
  "first_question": "Let's work through this together! Before we start, what do you already know about Multiplication?",
  "status": "in_progress"
}
```

**Flow:**
1. Frontend clicks "Start Session" button
2. POST request to /sessions/start
3. Backend creates session in database
4. Backend generates first question (simple template OR AI)
5. Backend saves question as Turn #1
6. Response sent to frontend
7. Frontend shows chat interface with first question

**Dependencies:**
- database/models.py (Session, Turn, Problem, PDFDocument)
- app/api/schemas.py (SessionStartRequest, SessionStartResponse)
- app/agents/tutor_agent.py (for AI-generated questions - currently using template)

**Why Two Approaches (Problem vs PDF):**
- Problem: Student solves specific math problem
- PDF: Student learns from uploaded study material
- Same session structure, different content source

#### Endpoint 3: Submit Turn

```python
@app.post("/sessions/{session_id}/turn", response_model=TurnSubmitResponse)
def submit_turn(
    session_id: int,
    request: TurnSubmitRequest,
    db: Session = Depends(get_db)
):
    # 1. Get session
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    
    # 2. Get problem or PDF
    problem = session.problem
    pdf_doc = session.pdf_document
    
    # 3. Save student's answer
    turn_number = db.query(Turn).filter(Turn.session_id == session_id).count() + 1
    student_turn = Turn(
        session_id=session_id,
        turn_number=turn_number,
        speaker=Speaker.STUDENT,
        message=request.student_answer
    )
    db.add(student_turn)
    db.commit()
    
    # 4. Get conversation history
    previous_turns = db.query(Turn).filter(
        Turn.session_id == session_id
    ).order_by(Turn.turn_number).all()
    
    history = "\n".join([
        f"{turn.speaker.value.upper()}: {turn.message}"
        for turn in previous_turns
    ])
    
    # 5. Check if answer is correct (only for problems)
    is_correct = None
    if problem:
        is_correct = request.student_answer.strip().lower() == problem.correct_answer.strip().lower()
        
        if is_correct:
            # Student got it right!
            session.status = SessionStatus.COMPLETED
            db.commit()
            tutor_response = "Excellent! You got it right! Great work!"
        else:
            # Generate next Socratic question using AI
            from app.agents.tutor_agent import TutorAgent
            tutor = TutorAgent()
            
            context = {
                "student_last_response": request.student_answer,
                "conversation_history": history,
                "problem_text": problem.problem_text,
                "correct_answer": problem.correct_answer
            }
            
            tutor_response = tutor.generate_response(context)
    else:
        # PDF session - no correct answer to check
        from app.agents.tutor_agent import TutorAgent
        tutor = TutorAgent()
        
        context = {
            "student_last_response": request.student_answer,
            "conversation_history": history,
            "pdf_content": pdf_doc.extracted_text
        }
        
        tutor_response = tutor.generate_response(context)
    
    # 6. Save tutor's response
    tutor_turn = Turn(
        session_id=session_id,
        turn_number=turn_number + 1,
        speaker=Speaker.TUTOR,
        message=tutor_response
    )
    db.add(tutor_turn)
    db.commit()
    
    # 7. Return response
    return TurnSubmitResponse(
        session_id=session_id,
        tutor_question=tutor_response,
        is_correct=is_correct,
        hints_used=0,
        session_status=session.status
    )
```

**Purpose:** Handle student's answer and get tutor's next question
**HTTP Method:** POST
**URL:** http://localhost:8000/sessions/79/turn
**Request:**
```json
{
  "student_answer": "I know multiplication is repeated addition"
}
```
**Response:**
```json
{
  "session_id": 79,
  "tutor_question": "Correct! So if we think of 15 × 8 as adding 15 eight times, can you write that out?",
  "is_correct": false,
  "hints_used": 0,
  "session_status": "in_progress"
}
```

**Flow:**
1. Student types answer in chat
2. Frontend sends POST to /sessions/{id}/turn
3. Backend saves student's message as Turn
4. Backend checks if answer is correct (problem-based only)
5. If correct: End session, congratulate
6. If incorrect: Call AI to generate next Socratic question
7. AI considers: problem text, correct answer, conversation history
8. AI generates guiding question (never reveals answer)
9. Backend saves tutor's question as Turn
10. Response sent to frontend
11. Frontend displays tutor's question in chat

**Dependencies:**
- database/models.py (Session, Turn, Problem, PDFDocument)
- app/agents/tutor_agent.py (AI question generation)
- app/api/schemas.py (TurnSubmitRequest, TurnSubmitResponse)

**Key Logic:**
- `turn_number`: Increments for each message (1, 2, 3, ...)
- `conversation_history`: Full conversation as context for AI
- `is_correct`: Only checked for problem-based sessions
- `tutor_response`: Generated by AI OR fallback template

### API Schemas (Data Models)

File: `app/api/schemas.py`

**Purpose:** Define request/response formats using Pydantic

#### Why Pydantic?
- Automatic validation (wrong type = error)
- Automatic documentation (shows in /docs)
- Type safety (catch bugs before runtime)

#### Schema Example: SessionStartRequest
```python
class SessionStartRequest(BaseModel):
    problem_id: Optional[int] = None
    pdf_document_id: Optional[int] = None
    student_id: str
```

**Purpose:** Validate session start request
**Why Optional:** Either problem_id OR pdf_document_id (not both)
**Validation:** FastAPI automatically rejects if:
- Missing student_id
- Both problem_id and pdf_document_id provided
- Wrong types (e.g., string for problem_id)

#### Schema Example: SessionStartResponse
```python
class SessionStartResponse(BaseModel):
    session_id: int
    problem: ProblemResponse
    first_question: str
    status: str
    
    class Config:
        from_attributes = True  # Allow creating from SQLAlchemy models
```

**Purpose:** Format session start response
**Why Config:** Enables `ProblemResponse.from_orm(problem)`

**All Schemas:**
- SessionStartRequest / Response
- TurnSubmitRequest / Response
- ProblemResponse
- ProblemsListResponse
- TranscriptResponse
- ErrorResponse

### PDF Upload Endpoint

File: `app/api/pdfs.py`

```python
@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(None),
    student_id: str = Form("anonymous"),
    db: Session = Depends(get_db)
):
    # 1. Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")
    
    # 2. Generate unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.pdf"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 3. Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 4. Extract text from PDF
    extraction_result = extract_text_from_pdf(file_path)
    
    if not extraction_result["success"]:
        os.remove(file_path)  # Clean up
        raise HTTPException(400, f"Failed to extract text: {extraction_result['error']}")
    
    # 5. Create database record
    pdf_doc = PDFDocument(
        title=title,
        description=description,
        filename=filename,
        original_filename=file.filename,
        file_path=file_path,
        extracted_text=extraction_result["text"],
        page_count=extraction_result["page_count"],
        file_size=os.path.getsize(file_path),
        uploaded_by=student_id
    )
    
    db.add(pdf_doc)
    db.commit()
    db.refresh(pdf_doc)
    
    # 6. Return response
    return {
        "success": True,
        "pdf_id": pdf_doc.id,
        "filename": file.filename,
        "page_count": pdf_doc.page_count,
        "file_size": pdf_doc.file_size
    }
```

**Purpose:** Handle PDF file uploads
**HTTP Method:** POST (multipart/form-data)
**URL:** http://localhost:8000/pdfs/upload

**Why multipart/form-data:**
- Regular JSON can't send files
- multipart supports: file + metadata (title, description)

**Request (via FormData):**
```javascript
const formData = new FormData();
formData.append('file', pdfFile);
formData.append('title', 'Biology Notes');
formData.append('description', 'Chapter 3');
formData.append('student_id', 'alice');
```

**Flow:**
1. Student selects PDF file
2. Frontend creates FormData with file + metadata
3. POST to /pdfs/upload
4. Backend saves file to uploads/pdfs/UUID.pdf
5. Backend extracts text using PyPDF
6. Backend saves metadata + text to database
7. Response with pdf_id
8. Frontend uses pdf_id to start session

**Dependencies:**
- app/utils/pdf_extractor.py (extract_text_from_pdf)
- database/models.py (PDFDocument)
- python-multipart package (file upload support)

**File Storage:**
- Files saved to: `uploads/pdfs/`
- Filename: UUID (prevents conflicts)
- Original name stored in database

**Why Extract Text:**
- AI needs text content (can't read PDF directly)
- Store in database for fast access
- No need to re-read file for each question

### AI Agent: Tutor

File: `app/agents/tutor_agent.py`

```python
class TutorAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.7,
            api_key=os.getenv("GROQ_API_KEY")
        )
    
    def generate_response(self, context: Dict[str, Any]) -> str:
        """
        Generate Socratic question based on context
        
        Context contains:
        - student_last_response: What student just said
        - conversation_history: Previous messages
        - problem_text: The problem (if problem-based)
        - correct_answer: The answer (DO NOT REVEAL!)
        - pdf_content: PDF text (if PDF-based)
        """
        
        # Build prompt for LLM
        if "problem_text" in context:
            # Problem-based tutoring
            prompt = f"""You are a Socratic tutor. Your goal is to guide the student to discover the answer themselves.

Problem: {context['problem_text']}
Correct Answer: {context['correct_answer']} (DO NOT REVEAL THIS!)

Conversation so far:
{context['conversation_history']}

Student just said: {context['student_last_response']}

Generate a guiding question that:
1. NEVER gives the answer directly
2. Asks about student's thinking process
3. Hints at next step without revealing it
4. Encourages logical reasoning

Your question:"""
        else:
            # PDF-based tutoring
            prompt = f"""You are a Socratic tutor helping a student learn from their study material.

Study Material:
{context['pdf_content'][:2000]}  # First 2000 chars

Conversation so far:
{context['conversation_history']}

Student just said: {context['student_last_response']}

Generate a thought-provoking question based on the material that:
1. Tests understanding
2. Encourages critical thinking
3. Connects concepts

Your question:"""
        
        # Call LLM
        response = self.llm.invoke(prompt)
        return response.content
```

**Purpose:** Generate Socratic questions using AI
**When Used:** Every time student answers (except when correct)

**Key Design Decisions:**

**1. Why Groq API:**
- Fast inference (< 2 seconds)
- Free tier available
- OpenAI-compatible API

**2. Why Temperature 0.7:**
- Temperature = randomness (0 = deterministic, 1 = creative)
- 0.7 = balanced (consistent but varied)
- Questions won't be identical for same input

**3. Why Separate Prompts:**
- Problem-based: Has correct answer (must not leak)
- PDF-based: No specific answer (test comprehension)

**4. Prompt Engineering:**
```
DO NOT REVEAL THIS! ← Explicit instruction
```
- LLMs follow instructions in prompt
- Without this, AI might give away answer
- Part of "Socratic" methodology

**Dependencies:**
- langchain-groq (ChatGroq)
- .env (GROQ_API_KEY)
- groq package

**Example Input/Output:**

**Input:**
```python
context = {
    "student_last_response": "I know it's repeated addition",
    "conversation_history": "TUTOR: What is multiplication?",
    "problem_text": "What is 15 × 8?",
    "correct_answer": "120"
}
```

**Output:**
```
"Great! Since multiplication is repeated addition, how many times would you add 15 to get the answer?"
```

**Flow:**
1. Student answers
2. Backend calls `tutor.generate_response(context)`
3. TutorAgent builds prompt
4. Prompt sent to Groq API
5. Groq returns question (takes 1-2 seconds)
6. Question returned to backend
7. Backend saves as Turn
8. Frontend displays question

### AI Agent: Verifier (Optional - Not Currently Used)

File: `app/agents/verifier_agent.py`

**Purpose:** Check if tutor's response leaked the answer
**Why:** Quality control - ensure Socratic method
**Currently:** Disabled (using tutor directly for speed)

**How It Would Work:**
1. Tutor generates response
2. Verifier checks: "Does this reveal the answer?"
3. If yes: Reject, ask tutor to regenerate
4. If no: Approve, send to student
5. Max 3 retries

**Code:**
```python
class VerifierAgent:
    def verify(self, tutor_response: str, correct_answer: str) -> Dict:
        prompt = f"""Is this tutor response revealing the answer?

Answer: {correct_answer}
Tutor said: {tutor_response}

Respond: APPROVE or REJECT"""
        
        result = self.llm.invoke(prompt)
        decision = "APPROVE" if "APPROVE" in result.content else "REJECT"
        
        return {
            "decision": decision,
            "reason": result.content
        }
```

**Why Disabled:**
- Adds 2-3 seconds per response
- Slower user experience
- Prompt engineering (DO NOT REVEAL) works well enough

**Could Re-enable:** If answer leaking becomes a problem

### PDF Text Extraction

File: `app/utils/pdf_extractor.py`

```python
def extract_text_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extract text content from PDF file
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        {
            "success": True/False,
            "text": "Extracted text content",
            "page_count": 2,
            "error": "Error message (if failed)"
        }
    """
    try:
        # Open PDF
        reader = PdfReader(pdf_path)
        
        # Extract text from all pages
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        
        return {
            "success": True,
            "text": text.strip(),
            "page_count": len(reader.pages),
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "page_count": 0,
            "error": str(e)
        }
```

**Purpose:** Convert PDF to text for AI
**Why:** AI can only read text, not PDF format

**Dependencies:**
- pypdf package (PDF reading)

**Limitations:**
- Scanned PDFs (images): Won't work (no OCR)
- Complex layouts: Might jumble text
- Encrypted PDFs: Will fail

**Example:**

**Input PDF (biology_notes.pdf):**
```
Chapter 3: Cell Structure

A cell has three main parts:
1. Cell membrane
2. Cytoplasm
3. Nucleus
```

**Extracted Text:**
```
Chapter 3: Cell Structure

A cell has three main parts:
1. Cell membrane
2. Cytoplasm
3. Nucleus
```

**Storage:**
- Text stored in `pdf_documents.extracted_text` column
- No need to re-extract for each question
- AI reads from database, not file

---

## Frontend Architecture

### Main Application

File: `frontend/src/main.jsx`

```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { CssBaseline, ThemeProvider } from '@mui/material'
import theme from './theme'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </StrictMode>,
)
```

**Purpose:** Entry point - bootstraps React app
**Why This Structure:**
- `StrictMode`: Extra checks in development
- `ThemeProvider`: Applies yellow theme globally
- `CssBaseline`: Resets browser defaults (consistent styling)

**Dependencies:**
- react (UI library)
- react-dom (renders to browser DOM)
- @mui/material (Material-UI components)
- ./theme.js (custom yellow theme)
- ./App.jsx (main component)

**Flow:**
1. Browser loads index.html
2. index.html has `<div id="root"></div>`
3. This file finds #root
4. Renders React app inside it

### Material-UI Theme

File: `frontend/src/theme.js`

```javascript
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#FDB813',        // Vibrant yellow
      light: '#FFD54F',       // Lighter yellow (hover states)
      dark: '#F9A825',        // Darker yellow (active states)
      contrastText: '#000000', // Black text on yellow (readable)
    },
    secondary: {
      main: '#FFC107',        // Alternate yellow shade
    },
    background: {
      default: '#FFFEF7',     // Off-white (softer than pure white)
      paper: '#FFFFFF',       // Pure white for cards
    },
    text: {
      primary: '#000000',     // Black text
      secondary: '#424242',   // Dark gray text
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

export default theme;
```

**Purpose:** Define app-wide colors and styles
**Why Material-UI Theme:**
- Consistent colors everywhere
- Automatic color variants (light, dark)
- Accessible (high contrast)

**Color Choices:**
- Primary Yellow (#FDB813): User requested yellow theme
- Background (#FFFEF7): Off-white for softer look
- Text Black (#000000): High contrast with yellow (readable)

**How It Works:**
```jsx
// In any component:
<Button color="primary">  {/* Uses #FDB813 yellow */}

<Box sx={{ backgroundColor: 'background.default' }}>  {/* Uses #FFFEF7 */}

<Typography color="text.primary">  {/* Uses #000000 black */}
```

**Dependencies:**
- @mui/material/styles

### Main App Component

File: `frontend/src/App.jsx`

```jsx
function App() {
  // State management
  const [studentId, setStudentId] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [activeSession, setActiveSession] = useState(null);
  const [sessionType, setSessionType] = useState(null);
  
  // Login handler
  const handleLogin = () => {
    if (studentId.trim()) {
      setIsLoggedIn(true);
    }
  };
  
  // Session start handler
  const handleSessionStart = (session, type) => {
    setActiveSession(session);
    setSessionType(type);
  };
  
  // PDF upload success handler
  const handlePDFUploadSuccess = async (uploadResult) => {
    const pdfId = uploadResult.pdf_id;
    const session = await startPDFSession(pdfId, studentId);
    handleSessionStart(session, 'pdf');
  };
  
  // Render login screen OR main app
  if (!isLoggedIn) {
    return (
      <Box>
        <TextField 
          label="Student ID"
          value={studentId}
          onChange={(e) => setStudentId(e.target.value)}
        />
        <Button onClick={handleLogin}>Start Learning</Button>
      </Box>
    );
  }
  
  // Main app (after login)
  if (activeSession) {
    return (
      <ChatInterface 
        session={activeSession}
        sessionType={sessionType}
        onEndSession={() => setActiveSession(null)}
      />
    );
  }
  
  return (
    <Container>
      <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
        <Tab label="Practice Problems" />
        <Tab label="Upload Study Material" />
      </Tabs>
      
      {tabValue === 0 && (
        <ProblemSelector 
          studentId={studentId}
          onSessionStart={handleSessionStart}
        />
      )}
      
      {tabValue === 1 && (
        <PDFUpload 
          studentId={studentId}
          onUploadSuccess={handlePDFUploadSuccess}
        />
      )}
    </Container>
  );
}
```

**Purpose:** Main app logic and state management
**State Variables:**
- `studentId`: Who is logged in
- `isLoggedIn`: Show login OR main app
- `tabValue`: Which tab is active (0 = Problems, 1 = PDF)
- `activeSession`: Current tutoring session (null = no session)
- `sessionType`: 'problem' or 'pdf'

**Flow:**

**1. Login Flow:**
```
User enters student ID
  ↓
Click "Start Learning"
  ↓
handleLogin() sets isLoggedIn = true
  ↓
App re-renders showing tabs
```

**2. Problem Session Flow:**
```
Click "Practice Problems" tab
  ↓
ProblemSelector shown
  ↓
Select a problem → Click "Start Session"
  ↓
ProblemSelector calls onSessionStart(session, 'problem')
  ↓
handleSessionStart() sets activeSession
  ↓
App re-renders showing ChatInterface
```

**3. PDF Session Flow:**
```
Click "Upload Study Material" tab
  ↓
PDFUpload shown
  ↓
Select PDF → Enter title → Click "Upload & Start"
  ↓
PDFUpload uploads file, gets pdf_id
  ↓
PDFUpload calls onUploadSuccess(result)
  ↓
handlePDFUploadSuccess() starts session
  ↓
App re-renders showing ChatInterface
```

**Why This Structure:**
- Single source of truth (state in App)
- Props drill down to children
- Callbacks bubble up from children
- Clean separation of concerns

**Dependencies:**
- react (useState hook)
- @mui/material (Container, Tabs, TextField, Button)
- ./components/ProblemSelector
- ./components/PDFUpload
- ./components/ChatInterface
- ./services/api (startPDFSession)

### Problem Selector Component

File: `frontend/src/components/ProblemSelector.jsx`

```jsx
function ProblemSelector({ studentId, onSessionStart }) {
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [startingSession, setStartingSession] = useState(null);
  
  // Load problems on mount
  useEffect(() => {
    loadProblems();
  }, []);
  
  const loadProblems = async () => {
    try {
      const data = await getProblems();  // API call
      setProblems(data.problems || []);
    } catch (err) {
      setError('Failed to load problems');
    } finally {
      setLoading(false);
    }
  };
  
  const handleStartSession = async (problemId) => {
    setStartingSession(problemId);
    try {
      const session = await startProblemSession(problemId, studentId);
      onSessionStart(session, 'problem');
    } catch (err) {
      setError('Failed to start session');
    } finally {
      setStartingSession(null);
    }
  };
  
  if (loading) {
    return <CircularProgress />;
  }
  
  return (
    <Grid container spacing={2}>
      {problems.map((problem) => (
        <Grid item xs={12} sm={6} md={4} key={problem.id}>
          <Card>
            <CardContent>
              <Typography variant="h6">{problem.title}</Typography>
              <Chip label={problem.difficulty_level} />
              <Typography variant="body2">
                {problem.problem_text}
              </Typography>
              <Button 
                onClick={() => handleStartSession(problem.id)}
                disabled={startingSession === problem.id}
              >
                {startingSession === problem.id ? (
                  <CircularProgress size={24} />
                ) : (
                  'Start Session'
                )}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}
```

**Purpose:** Display problem cards, start sessions
**Props:**
- `studentId`: Who is selecting (from App)
- `onSessionStart`: Callback when session starts (from App)

**State:**
- `problems`: Array of problem objects from backend
- `loading`: Show spinner while fetching
- `startingSession`: Which problem is starting (for loading spinner)

**Flow:**

**1. Component Mounts:**
```
useEffect runs
  ↓
loadProblems() called
  ↓
GET /problems
  ↓
Backend returns 7 problems
  ↓
setProblems(problems)
  ↓
Component re-renders with cards
```

**2. Start Session:**
```
User clicks "Start Session" on problem #1
  ↓
handleStartSession(1)
  ↓
setStartingSession(1) → Button shows spinner
  ↓
POST /sessions/start with problem_id: 1
  ↓
Backend creates session, returns data
  ↓
onSessionStart(session, 'problem') → Notify parent
  ↓
Parent (App) shows ChatInterface
```

**Why Material-UI Grid:**
- Responsive layout (3 columns → 2 columns → 1 column as screen shrinks)
- xs={12}: Full width on phone
- sm={6}: Half width on tablet
- md={4}: Third width on desktop

**Dependencies:**
- react (useState, useEffect)
- @mui/material (Grid, Card, Button, Chip, CircularProgress)
- ../services/api (getProblems, startProblemSession)

### PDF Upload Component

File: `frontend/src/components/PDFUpload.jsx`

```jsx
function PDFUpload({ studentId, onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  
  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate: must be PDF
    if (!file.name.endsWith('.pdf')) {
      setError('Only PDF files allowed');
      return;
    }
    
    // Validate: check page count (max 2 pages)
    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await PDFDocument.load(arrayBuffer);
      
      if (pdf.getPageCount() > 2) {
        setError('PDF must be 2 pages or less');
        return;
      }
      
      setSelectedFile(file);
      setError('');
    } catch (err) {
      setError('Failed to read PDF');
    }
  };
  
  const handleUpload = async () => {
    if (!selectedFile || !title) {
      setError('Please select file and enter title');
      return;
    }
    
    setUploading(true);
    try {
      // Upload PDF
      const result = await uploadPDF(selectedFile, title, description);
      
      // Notify parent
      onUploadSuccess(result);
    } catch (err) {
      setError('Upload failed');
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <Box>
      <Typography variant="h5">Upload Study Material (PDF)</Typography>
      
      <TextField 
        label="Title *"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        fullWidth
      />
      
      <TextField 
        label="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        multiline
        rows={3}
        fullWidth
      />
      
      <Button 
        variant="outlined"
        component="label"
      >
        SELECT PDF FILE (MAX 2 PAGES)
        <input 
          type="file"
          accept=".pdf"
          hidden
          onChange={handleFileChange}
        />
      </Button>
      
      {selectedFile && (
        <Typography>{selectedFile.name}</Typography>
      )}
      
      {error && (
        <Alert severity="error">{error}</Alert>
      )}
      
      <Button 
        variant="contained"
        onClick={handleUpload}
        disabled={!selectedFile || !title || uploading}
      >
        {uploading ? 'UPLOADING...' : 'UPLOAD & START SESSION'}
      </Button>
    </Box>
  );
}
```

**Purpose:** Handle PDF file selection and upload
**Props:**
- `studentId`: Who is uploading
- `onUploadSuccess`: Callback when upload succeeds

**State:**
- `selectedFile`: File object from input
- `title`: PDF title (required)
- `description`: Optional description
- `uploading`: Show loading state
- `error`: Error message

**Flow:**

**1. File Selection:**
```
User clicks "SELECT PDF FILE"
  ↓
Browser shows file picker
  ↓
User selects file
  ↓
handleFileChange(event)
  ↓
Validate: is PDF?
  ↓
Read PDF with pdf-lib
  ↓
Validate: ≤ 2 pages?
  ↓
setSelectedFile(file)
```

**2. Upload:**
```
User enters title
  ↓
User clicks "UPLOAD & START SESSION"
  ↓
handleUpload()
  ↓
Create FormData:
  - file: PDF file
  - title: "Biology Notes"
  - description: "Chapter 3"
  - student_id: "alice"
  ↓
POST /pdfs/upload (multipart/form-data)
  ↓
Backend saves file, extracts text
  ↓
Backend returns { pdf_id: 7, ... }
  ↓
onUploadSuccess({ pdf_id: 7 })
  ↓
Parent starts PDF session
```

**Client-Side Validation:**
- File type: .pdf extension check
- Page count: pdf-lib reads PDF, checks page count
- Why: Faster feedback (no need to upload invalid files)

**Why pdf-lib:**
```javascript
import { PDFDocument } from 'pdf-lib';

// Read PDF in browser (no backend needed)
const pdf = await PDFDocument.load(arrayBuffer);
const pageCount = pdf.getPageCount();
```

**Dependencies:**
- react (useState)
- @mui/material (Box, Button, TextField, Alert)
- pdf-lib (client-side PDF reading)
- ../services/api (uploadPDF)

### Chat Interface Component

File: `frontend/src/components/ChatInterface.jsx`

```jsx
function ChatInterface({ session, sessionType, onEndSession }) {
  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Load initial message on mount
  useEffect(() => {
    setMessages([
      {
        speaker: 'tutor',
        message: session.first_question,
        timestamp: new Date()
      }
    ]);
  }, [session]);
  
  // Auto-scroll to bottom when new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSend = async () => {
    if (!currentInput.trim()) return;
    
    // Add student message to UI
    const studentMessage = {
      speaker: 'student',
      message: currentInput,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, studentMessage]);
    setCurrentInput('');
    setSending(true);
    
    try {
      // Send to backend
      const response = await submitTurn(session.id, currentInput);
      
      // Add tutor response to UI
      const tutorMessage = {
        speaker: 'tutor',
        message: response.tutor_question,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, tutorMessage]);
      
      // Check if session ended
      if (response.is_correct) {
        setTimeout(() => {
          alert('Congratulations! You solved it!');
          onEndSession();
        }, 1000);
      }
    } catch (err) {
      setError('Failed to send message');
    } finally {
      setSending(false);
    }
  };
  
  return (
    <Box>
      {/* Header */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">
            {sessionType === 'problem' 
              ? session.problem.title 
              : 'PDF Tutoring'}
          </Typography>
          <Button onClick={onEndSession}>End Session</Button>
        </Toolbar>
      </AppBar>
      
      {/* Messages */}
      <Box sx={{ 
        height: '60vh',
        overflowY: 'auto',
        padding: 2,
        backgroundColor: '#FFFEF7'
      }}>
        {messages.map((msg, index) => (
          <Box 
            key={index}
            sx={{
              display: 'flex',
              justifyContent: msg.speaker === 'student' ? 'flex-end' : 'flex-start',
              mb: 2
            }}
          >
            <Paper 
              sx={{
                padding: 2,
                maxWidth: '70%',
                backgroundColor: msg.speaker === 'student' ? '#FFF9E6' : '#FFFFFF',
                border: msg.speaker === 'tutor' ? '2px solid #FDB813' : 'none'
              }}
            >
              <Typography variant="body2" fontWeight="bold">
                {msg.speaker === 'student' ? 'You' : 'Tutor'}
              </Typography>
              <Typography variant="body1">
                {msg.message}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {msg.timestamp.toLocaleTimeString()}
              </Typography>
            </Paper>
          </Box>
        ))}
        <div ref={messagesEndRef} />
      </Box>
      
      {/* Input */}
      <Box sx={{ 
        display: 'flex', 
        gap: 1,
        padding: 2,
        borderTop: '1px solid #E0E0E0'
      }}>
        <TextField 
          fullWidth
          placeholder="Type your answer..."
          value={currentInput}
          onChange={(e) => setCurrentInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !sending) {
              handleSend();
            }
          }}
          disabled={sending}
        />
        <Button 
          variant="contained"
          onClick={handleSend}
          disabled={!currentInput.trim() || sending}
        >
          {sending ? <CircularProgress size={24} /> : 'Send'}
        </Button>
      </Box>
    </Box>
  );
}
```

**Purpose:** Display conversation and handle message sending
**Props:**
- `session`: Session object with id, first_question, problem
- `sessionType`: 'problem' or 'pdf'
- `onEndSession`: Callback to exit chat

**State:**
- `messages`: Array of message objects
- `currentInput`: What user is typing
- `sending`: Show loading while waiting for response
- `messagesEndRef`: Reference for auto-scroll

**Message Object:**
```javascript
{
  speaker: 'tutor' | 'student',
  message: 'The actual message text',
  timestamp: Date object
}
```

**Flow:**

**1. Component Mounts:**
```
useEffect runs
  ↓
Add first tutor message to messages array
  ↓
Messages rendered as bubbles
```

**2. Send Message:**
```
User types answer
  ↓
User presses Enter OR clicks Send
  ↓
handleSend()
  ↓
Add student message to UI immediately (optimistic update)
  ↓
Clear input field
  ↓
POST /sessions/{id}/turn
  ↓
Wait for response (1-3 seconds)
  ↓
Receive tutor's next question
  ↓
Add tutor message to UI
  ↓
Auto-scroll to bottom
```

**3. Session End:**
```
Student types correct answer
  ↓
Backend responds with is_correct: true
  ↓
Show congratulations alert
  ↓
onEndSession() → Return to problem selector
```

**Styling:**

**Student Messages:**
- Aligned right
- Light yellow background (#FFF9E6)
- No border

**Tutor Messages:**
- Aligned left
- White background
- Yellow border (2px, #FDB813)

**Auto-Scroll:**
```javascript
// Scroll to bottom after each message
messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
```

**Dependencies:**
- react (useState, useEffect, useRef)
- @mui/material (Box, Paper, TextField, Button, AppBar, CircularProgress)
- ../services/api (submitTurn)

### API Client

File: `frontend/src/services/api.js`

```javascript
import axios from 'axios';

// Use environment variable in production, localhost in development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Get all problems
export const getProblems = async () => {
  const response = await api.get('/problems');
  return response.data;
};

// Start problem session
export const startProblemSession = async (problemId, studentId) => {
  const response = await api.post('/sessions/start', {
    problem_id: problemId,
    student_id: studentId,
  });
  return {
    ...response.data,
    id: response.data.session_id,  // Normalize field name
  };
};

// Start PDF session
export const startPDFSession = async (pdfId, studentId) => {
  const response = await api.post('/sessions/start', {
    pdf_document_id: pdfId,
    student_id: studentId,
  });
  return {
    ...response.data,
    id: response.data.session_id,
  };
};

// Submit turn
export const submitTurn = async (sessionId, studentResponse) => {
  const response = await api.post(`/sessions/${sessionId}/turn`, {
    student_answer: studentResponse,
  });
  return response.data;
};

// Upload PDF
export const uploadPDF = async (file, title, description) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title);
  if (description) {
    formData.append('description', description);
  }
  
  const response = await axios.post(`${API_BASE_URL}/pdfs/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export default api;
```

**Purpose:** Centralized API calls to backend
**Why Separate File:**
- DRY (Don't Repeat Yourself)
- Easy to change API URL
- Mock for testing

**Key Concepts:**

**1. axios vs fetch:**
```javascript
// axios (what we use):
const response = await api.get('/problems');
const data = response.data;  // Automatic JSON parsing

// fetch (alternative):
const response = await fetch('/problems');
const data = await response.json();  // Manual JSON parsing
```

**2. Environment Variables:**
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Development: http://localhost:8000 (fallback)
// Production: https://your-backend.onrender.com (from env var)
```

**How to Set in Production (Vercel):**
```
Environment Variable in Vercel:
VITE_API_URL = https://socratic-tutor-api.onrender.com
```

**3. FormData for File Upload:**
```javascript
// Regular JSON:
api.post('/endpoint', { key: 'value' })

// File upload:
const formData = new FormData();
formData.append('file', fileObject);
api.post('/endpoint', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
```

**4. Response Normalization:**
```javascript
// Backend returns: { session_id: 79, ... }
// Frontend expects: { id: 79, ... }

return {
  ...response.data,
  id: response.data.session_id,  // Add normalized field
};
```

**Dependencies:**
- axios (HTTP client)
- import.meta.env (Vite environment variables)

---

## Code Flow & Dependencies

### Complete Request Flow: Problem Session

```
1. USER ACTION
   User clicks "Start Session" on Problem #1

2. FRONTEND (ProblemSelector.jsx)
   handleStartSession(1) called
   ↓

3. API CLIENT (services/api.js)
   startProblemSession(1, "alice")
   ↓
   POST http://localhost:8000/sessions/start
   Body: { problem_id: 1, student_id: "alice" }
   ↓

4. BACKEND (app/api/main.py)
   @app.post("/sessions/start")
   start_session(request, db)
   ↓

5. DATABASE QUERY
   db.query(Problem).filter(Problem.id == 1).first()
   ↓
   SELECT * FROM problems WHERE id = 1
   ↓
   Returns: Problem object

6. CREATE SESSION
   session = DBSession(
     problem_id=1,
     student_id="alice",
     status="IN_PROGRESS"
   )
   db.add(session)
   db.commit()
   ↓
   INSERT INTO sessions (problem_id, student_id, status, started_at)
   VALUES (1, 'alice', 'IN_PROGRESS', NOW())
   RETURNING id
   ↓
   Returns: session_id = 79

7. GENERATE FIRST QUESTION
   topic = problem.topic.split()[-1]
   first_question = f"What do you know about {topic}?"
   ↓
   Result: "What do you know about Multiplication?"

8. SAVE FIRST TURN
   turn = Turn(
     session_id=79,
     turn_number=1,
     speaker="TUTOR",
     message=first_question
   )
   db.add(turn)
   db.commit()
   ↓
   INSERT INTO turns (session_id, turn_number, speaker, message)
   VALUES (79, 1, 'TUTOR', 'What do you know about Multiplication?')

9. RETURN RESPONSE
   return {
     session_id: 79,
     problem: { id: 1, title: "Basic Multiplication", ... },
     first_question: "What do you know about Multiplication?",
     status: "in_progress"
   }
   ↓

10. FRONTEND RECEIVES RESPONSE
    onSessionStart(session, 'problem')
    ↓

11. APP STATE UPDATE (App.jsx)
    setActiveSession(session)
    ↓

12. RENDER CHAT
    App renders <ChatInterface session={session} />
    ↓

13. DISPLAY FIRST MESSAGE
    ChatInterface shows tutor's first question
```

### Complete Request Flow: Submit Answer

```
1. USER ACTION
   User types "It's repeated addition" and clicks Send

2. FRONTEND (ChatInterface.jsx)
   handleSend() called
   ↓
   Add student message to UI (optimistic update)
   ↓

3. API CLIENT (services/api.js)
   submitTurn(79, "It's repeated addition")
   ↓
   POST http://localhost:8000/sessions/79/turn
   Body: { student_answer: "It's repeated addition" }
   ↓

4. BACKEND (app/api/main.py)
   @app.post("/sessions/{session_id}/turn")
   submit_turn(79, request, db)
   ↓

5. GET SESSION
   session = db.query(DBSession).filter(DBSession.id == 79).first()
   ↓
   SELECT * FROM sessions WHERE id = 79
   ↓
   Returns: Session with problem_id=1

6. GET PROBLEM
   problem = session.problem
   ↓
   SELECT * FROM problems WHERE id = 1
   ↓
   Returns: Problem "Basic Multiplication"

7. SAVE STUDENT TURN
   turn_number = count existing turns + 1
   ↓
   SELECT COUNT(*) FROM turns WHERE session_id = 79
   ↓
   Returns: 1 (first question already saved)
   ↓
   turn_number = 2
   ↓
   student_turn = Turn(
     session_id=79,
     turn_number=2,
     speaker="STUDENT",
     message="It's repeated addition"
   )
   db.add(student_turn)
   db.commit()
   ↓
   INSERT INTO turns (session_id, turn_number, speaker, message)
   VALUES (79, 2, 'STUDENT', "It's repeated addition")

8. GET CONVERSATION HISTORY
   previous_turns = db.query(Turn).filter(Turn.session_id == 79).all()
   ↓
   SELECT * FROM turns WHERE session_id = 79 ORDER BY turn_number
   ↓
   Returns: [Turn 1 (tutor), Turn 2 (student)]
   ↓
   history = """
   TUTOR: What do you know about Multiplication?
   STUDENT: It's repeated addition
   """

9. CHECK IF CORRECT
   is_correct = "It's repeated addition".lower() == "120".lower()
   ↓
   Result: False (not the final answer)

10. GENERATE AI RESPONSE
    from app.agents.tutor_agent import TutorAgent
    tutor = TutorAgent()
    ↓
    context = {
      student_last_response: "It's repeated addition",
      conversation_history: history,
      problem_text: "What is 15 multiplied by 8?",
      correct_answer: "120"
    }
    ↓
    tutor_response = tutor.generate_response(context)
    ↓

11. CALL GROQ API
    Prompt sent to Groq:
    """
    You are a Socratic tutor.
    Problem: What is 15 multiplied by 8?
    Correct Answer: 120 (DO NOT REVEAL!)
    
    Student said: It's repeated addition
    
    Generate guiding question...
    """
    ↓
    Groq API processes (1-2 seconds)
    ↓
    Returns: "Great! So if 15 × 8 means adding 15 eight times, how would you write that out?"

12. SAVE TUTOR TURN
    tutor_turn = Turn(
      session_id=79,
      turn_number=3,
      speaker="TUTOR",
      message="Great! So if 15 × 8 means..."
    )
    db.add(tutor_turn)
    db.commit()
    ↓
    INSERT INTO turns (session_id, turn_number, speaker, message)
    VALUES (79, 3, 'TUTOR', 'Great! So if 15 × 8 means...')

13. RETURN RESPONSE
    return {
      session_id: 79,
      tutor_question: "Great! So if 15 × 8 means...",
      is_correct: false,
      hints_used: 0,
      session_status: "in_progress"
    }
    ↓

14. FRONTEND RECEIVES RESPONSE
    Add tutor message to UI
    ↓

15. DISPLAY MESSAGE
    ChatInterface renders new message bubble
    ↓
    Auto-scroll to bottom
```

### Dependency Graph

```
Frontend Dependencies:
  App.jsx
  ├── theme.js
  ├── ProblemSelector.jsx
  │   └── services/api.js
  │       └── axios
  ├── PDFUpload.jsx
  │   ├── services/api.js
  │   └── pdf-lib
  └── ChatInterface.jsx
      └── services/api.js

Backend Dependencies:
  app/api/main.py
  ├── database/connection.py
  │   ├── database/models.py
  │   │   └── sqlalchemy
  │   ├── python-dotenv
  │   └── psycopg2-binary
  ├── app/api/schemas.py
  │   └── pydantic
  ├── app/agents/tutor_agent.py
  │   ├── langchain-groq
  │   ├── langchain
  │   └── groq
  └── app/api/pdfs.py
      └── app/utils/pdf_extractor.py
          └── pypdf

Database Dependencies:
  PostgreSQL (Supabase)
  └── psycopg2-binary (driver)
      └── sqlalchemy (ORM)
          └── database/models.py (schema)

External Services:
  Groq API
  └── GROQ_API_KEY (.env)
      └── app/agents/tutor_agent.py
```

---

## Building From Scratch

### Step 1: Set Up Development Environment

**Install Prerequisites:**
```bash
# Python 3.9+
python --version

# Node.js 18+
node --version
npm --version

# Git
git --version
```

### Step 2: Create Project Directory

```bash
mkdir socratic-tutoring-system
cd socratic-tutoring-system
```

### Step 3: Backend Setup

**3.1 Create Virtual Environment:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

**3.2 Create requirements.txt:**
```
groq
langchain>=0.3.0
langchain-groq>=1.1.0
langchain-community>=0.3.0
langgraph
fastapi>=0.104
uvicorn>=0.24
sqlalchemy>=2.0
psycopg2-binary>=2.9
python-multipart>=0.0.9
pypdf>=6.0
pydantic>=2.0
python-dotenv
requests>=2.31
gunicorn>=21.0
sse-starlette>=1.8
```

**3.3 Install Dependencies:**
```bash
pip install -r requirements.txt
```

**3.4 Create Directory Structure:**
```bash
mkdir -p app/api app/agents app/utils app/tools
mkdir -p database
mkdir -p uploads/pdfs
```

**3.5 Create .env File:**
```
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://user:pass@host:port/database
```

**Get Groq API Key:**
1. Go to console.groq.com
2. Sign up / Login
3. Create API key
4. Copy to .env

**3.6 Create Database Models (database/models.py):**
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class DifficultyLevel(enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class SessionStatus(enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Speaker(enum.Enum):
    STUDENT = "student"
    TUTOR = "tutor"

class Problem(Base):
    __tablename__ = "problems"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    problem_text = Column(Text, nullable=False)
    correct_answer = Column(String(255), nullable=False)
    topic = Column(String(255))
    difficulty = Column(Enum(DifficultyLevel))
    sessions = relationship("Session", back_populates="problem")

class PDFDocument(Base):
    __tablename__ = "pdf_documents"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(String(500), nullable=False)
    extracted_text = Column(Text, nullable=False)
    page_count = Column(Integer)
    file_size = Column(Integer)
    uploaded_by = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    sessions = relationship("Session", back_populates="pdf_document")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=True)
    pdf_document_id = Column(Integer, ForeignKey("pdf_documents.id"), nullable=True)
    student_id = Column(String(255), nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.IN_PROGRESS)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    problem = relationship("Problem", back_populates="sessions")
    pdf_document = relationship("PDFDocument", back_populates="sessions")
    turns = relationship("Turn", back_populates="session")
    hints_given = relationship("HintGiven", back_populates="session")
    verifier_flags = relationship("VerifierFlag", back_populates="session")

class Turn(Base):
    __tablename__ = "turns"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    turn_number = Column(Integer, nullable=False)
    speaker = Column(Enum(Speaker), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("Session", back_populates="turns")

class HintGiven(Base):
    __tablename__ = "hints_given"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    turn_id = Column(Integer, ForeignKey("turns.id"))
    hint_text = Column(Text, nullable=False)
    hint_type = Column(String(50))
    session = relationship("Session", back_populates="hints_given")

class VerifierFlag(Base):
    __tablename__ = "verifier_flags"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    turn_id = Column(Integer, ForeignKey("turns.id"))
    rejected_response = Column(Text)
    rejection_reason = Column(Text)
    flagged_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("Session", back_populates="verifier_flags")
```

**3.7 Create Database Connection (database/connection.py):**
```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Fix URL for psycopg2
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**3.8 Create Database Initialization (database/init_db.py):**
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Base, Problem, DifficultyLevel
from database.connection import engine, SessionLocal

def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created!")

def seed_problems():
    print("Seeding problems...")
    db = SessionLocal()
    
    problems = [
        Problem(
            title="Basic Multiplication",
            problem_text="What is 15 multiplied by 8?",
            correct_answer="120",
            topic="Mathematics - Multiplication",
            difficulty=DifficultyLevel.easy
        ),
        # ... add 6 more problems
    ]
    
    db.add_all(problems)
    db.commit()
    db.close()
    print(f"Seeded {len(problems)} problems!")

if __name__ == "__main__":
    create_tables()
    seed_problems()
```

**3.9 Run Database Initialization:**
```bash
python database/init_db.py
```

**3.10 Create Tutor Agent (app/agents/tutor_agent.py):**
```python
import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

class TutorAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.7,
            api_key=os.getenv("GROQ_API_KEY")
        )
    
    def generate_response(self, context: Dict[str, Any]) -> str:
        if "problem_text" in context:
            prompt = f"""You are a Socratic tutor.

Problem: {context['problem_text']}
Correct Answer: {context['correct_answer']} (DO NOT REVEAL!)

Conversation:
{context['conversation_history']}

Student: {context['student_last_response']}

Generate a guiding question (never reveal answer):"""
        else:
            prompt = f"""You are a Socratic tutor.

Material:
{context['pdf_content'][:2000]}

Conversation:
{context['conversation_history']}

Student: {context['student_last_response']}

Generate a thought-provoking question:"""
        
        response = self.llm.invoke(prompt)
        return response.content
```

**3.11 Create API Schemas (app/api/schemas.py):**
```python
from pydantic import BaseModel
from typing import Optional

class SessionStartRequest(BaseModel):
    problem_id: Optional[int] = None
    pdf_document_id: Optional[int] = None
    student_id: str

class SessionStartResponse(BaseModel):
    session_id: int
    problem: dict
    first_question: str
    status: str

class TurnSubmitRequest(BaseModel):
    student_answer: str

class TurnSubmitResponse(BaseModel):
    session_id: int
    tutor_question: str
    is_correct: Optional[bool]
    hints_used: int
    session_status: str

class ProblemsListResponse(BaseModel):
    problems: list
    total: int

class ProblemResponse(BaseModel):
    id: int
    title: str
    problem_text: str
    topic: str
    difficulty: str
    
    class Config:
        from_attributes = True
```

**3.12 Create Main API (app/api/main.py):**
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.schemas import *
from database.models import *
from database.connection import get_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "online", "service": "Socratic Tutoring System"}

@app.get("/problems", response_model=ProblemsListResponse)
def list_problems(db: Session = Depends(get_db)):
    problems = db.query(Problem).all()
    return ProblemsListResponse(
        problems=[ProblemResponse.from_orm(p) for p in problems],
        total=len(problems)
    )

@app.post("/sessions/start", response_model=SessionStartResponse, status_code=201)
def start_session(request: SessionStartRequest, db: Session = Depends(get_db)):
    # Implementation from earlier...
    pass

@app.post("/sessions/{session_id}/turn", response_model=TurnSubmitResponse)
def submit_turn(session_id: int, request: TurnSubmitRequest, db: Session = Depends(get_db)):
    # Implementation from earlier...
    pass
```

### Step 4: Frontend Setup

**4.1 Create React App:**
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

**4.2 Install Dependencies:**
```bash
npm install @mui/material @emotion/react @emotion/styled axios pdf-lib
```

**4.3 Create Theme (src/theme.js):**
```javascript
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#FDB813',
      contrastText: '#000000',
    },
    background: {
      default: '#FFFEF7',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#000000',
    },
  },
});

export default theme;
```

**4.4 Update Main (src/main.jsx):**
```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { CssBaseline, ThemeProvider } from '@mui/material'
import theme from './theme'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </StrictMode>,
)
```

**4.5 Create API Client (src/services/api.js):**
```javascript
// Implementation from earlier...
```

**4.6 Create Components:**
- src/App.jsx
- src/components/ProblemSelector.jsx
- src/components/PDFUpload.jsx
- src/components/ChatInterface.jsx

### Step 5: Run the Application

**Start Backend:**
```bash
# Terminal 1
cd socratic-tutoring-system
venv\Scripts\activate
python -m uvicorn app.api.main:app --reload
```

**Start Frontend:**
```bash
# Terminal 2
cd frontend
npm run dev
```

**Open Browser:**
```
http://localhost:5173
```

---

## How Everything Connects

### The Complete Picture

```
                    ┌─────────────────┐
                    │  USER'S BROWSER │
                    └────────┬────────┘
                             │
                             │ HTTP
                             ↓
              ┌──────────────────────────┐
              │   REACT FRONTEND         │
              │   (Port 5173)            │
              │                          │
              │  - App.jsx               │
              │  - ProblemSelector       │
              │  - PDFUpload             │
              │  - ChatInterface         │
              │  - services/api.js       │
              └──────────┬───────────────┘
                         │
                         │ Axios HTTP Requests
                         │ (JSON / FormData)
                         ↓
              ┌──────────────────────────┐
              │   FASTAPI BACKEND        │
              │   (Port 8000)            │
              │                          │
              │  - main.py (endpoints)   │
              │  - schemas.py (validate) │
              └─┬──────────┬─────────┬──┘
                │          │         │
     ┌──────────┘          │         └──────────┐
     │                     │                    │
     ↓                     ↓                    ↓
┌─────────┐       ┌────────────────┐    ┌──────────┐
│  GROQ   │       │   POSTGRESQL   │    │   PDF    │
│   API   │       │   (Supabase)   │    │  FILES   │
│         │       │                │    │          │
│ TutorAg │       │  - problems    │    │ uploads/ │
│ ent     │       │  - sessions    │    │  pdfs/   │
└─────────┘       │  - turns       │    └──────────┘
                  │  - pdf_docs    │
                  └────────────────┘
```

### Data Flow Example

**User Solves Problem "15 × 8":**

1. **Login:**
   - User enters "alice" → App.jsx sets studentId
   
2. **Select Problem:**
   - Click "Basic Multiplication" card
   - ProblemSelector calls API: `GET /problems`
   - Backend queries database: `SELECT * FROM problems`
   - Returns 7 problems
   - Frontend displays cards
   
3. **Start Session:**
   - Click "Start Session" on problem #1
   - ProblemSelector calls: `POST /sessions/start { problem_id: 1 }`
   - Backend creates session in database
   - Backend generates first question (template OR AI)
   - Backend saves question as Turn #1
   - Returns: `{ session_id: 79, first_question: "..." }`
   - App.jsx switches to ChatInterface
   
4. **First Response:**
   - User types: "It's repeated addition"
   - Click Send
   - ChatInterface calls: `POST /sessions/79/turn { student_answer: "..." }`
   - Backend saves as Turn #2
   - Backend calls TutorAgent
   - TutorAgent builds prompt
   - TutorAgent calls Groq API
   - Groq returns: "Great! So if 15 × 8 is adding 15 eight times..."
   - Backend saves as Turn #3
   - Returns: `{ tutor_question: "..." }`
   - ChatInterface displays tutor's message
   
5. **Continue Until Correct:**
   - Repeat until student types "120"
   - Backend detects: answer == "120"
   - Updates session: `status = COMPLETED`
   - Returns: `{ is_correct: true }`
   - ChatInterface shows congratulations
   - Exit back to problem selector

### File Dependency Matrix

| File | Imports | Used By | Database | External API |
|------|---------|---------|----------|--------------|
| frontend/src/main.jsx | theme.js, App.jsx, @mui/material | (entry) | No | No |
| frontend/src/theme.js | @mui/material/styles | main.jsx | No | No |
| frontend/src/App.jsx | ProblemSelector, PDFUpload, ChatInterface, @mui/material | main.jsx | No | No |
| frontend/src/components/ProblemSelector.jsx | services/api.js, @mui/material | App.jsx | No | Yes (backend) |
| frontend/src/components/PDFUpload.jsx | services/api.js, pdf-lib, @mui/material | App.jsx | No | Yes (backend) |
| frontend/src/components/ChatInterface.jsx | services/api.js, @mui/material | App.jsx | No | Yes (backend) |
| frontend/src/services/api.js | axios | All components | No | Yes (backend) |
| app/api/main.py | schemas.py, models.py, connection.py, tutor_agent.py | (uvicorn) | Yes | No |
| app/api/schemas.py | pydantic | main.py | No | No |
| app/agents/tutor_agent.py | langchain-groq, dotenv | main.py | No | Yes (Groq) |
| database/models.py | sqlalchemy | connection.py, main.py | No | No |
| database/connection.py | models.py, sqlalchemy, dotenv | main.py | Yes | No |
| database/init_db.py | models.py, connection.py | (manual run) | Yes | No |

---

## Summary

This project is a **Socratic Tutoring System** where:

1. **Frontend (React)** provides the user interface
2. **Backend (FastAPI)** handles logic and coordination
3. **Database (PostgreSQL)** stores all data
4. **AI (Groq API via LangChain)** generates Socratic questions

**Key Files:**
- **Backend Entry:** `app/api/main.py`
- **Database Schema:** `database/models.py`
- **AI Agent:** `app/agents/tutor_agent.py`
- **Frontend Entry:** `frontend/src/main.jsx`
- **API Client:** `frontend/src/services/api.js`

**To Build From Scratch:**
1. Create directory structure
2. Install Python dependencies
3. Create database models
4. Initialize database with sample data
5. Create FastAPI endpoints
6. Create AI tutor agent
7. Create React frontend
8. Connect frontend to backend via API
9. Run both servers
10. Open browser and use app

**Dependencies Flow:**
```
React → Axios → FastAPI → SQLAlchemy → PostgreSQL
                 ↓
            LangChain → Groq API
```

Every piece is documented above with:
- What it does (purpose)
- Why it exists (reason)
- When it's used (flow)
- How it works (code)
- What it depends on (dependencies)

**This guide is complete enough that someone can rebuild the entire app by following it step by step!**
