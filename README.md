# 🎓 Multi-Agent Socratic Tutoring System

A production-ready multi-agent AI tutoring system that uses **Socratic questioning** to guide students toward understanding, rather than giving direct answers. Built with LangChain, LangGraph, and FastAPI.

**Core Innovation:** Quality-controlled AI tutoring through multi-agent collaboration (Tutor + Verifier + Handoff Controller).

---

## 🌟 Key Features

### Multi-Agent Architecture
- **Tutor Agent**: Generates Socratic guiding questions (never reveals answers)
- **Verifier Agent**: Quality control - checks every response for answer leaks  
- **Handoff Controller**: Orchestrates agents with retry-with-feedback loop (max 3 attempts)

### Advanced Capabilities
- **LangGraph State Machine**: Declarative workflow with visual representation
- **Retry with Feedback**: Rejected responses get feedback for improvement
- **PDF-Based Tutoring** (Bonus): Students upload study materials, get tutored on content
- **Real-time Streaming**: Server-Sent Events (SSE) for live agent updates
- **Background Jobs**: Durable execution with retry logic and heartbeat monitoring
- **Comprehensive Testing**: 9 test files + 6 interactive demo scripts

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Groq API (OpenAI GPT models) |
| **Agent Framework** | LangChain + LangGraph |
| **API** | FastAPI with SSE streaming |
| **Database** | PostgreSQL (Supabase) / SQLite (local) |
| **ORM** | SQLAlchemy |
| **Validation** | Pydantic |
| **PDF Processing** | PyPDF |
| **Environment** | python-dotenv |

---

## 📁 Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed organization.

```
socratic-tutoring-system/
├── app/
│   ├── agents/              # Multi-agent system (Tutor, Verifier, Handoff, LangGraph)
│   ├── tools/               # Agent tools (calculator, check_answer, get_hint)
│   ├── utils/               # Utilities (PDF extraction)
│   └── api/                 # FastAPI endpoints (main, streaming, jobs, pdfs)
├── database/                # Schema, models, connection
├── tests/                   # 9 test files covering all scenarios
├── demos/                   # 6 interactive demo scripts for video
├── docs/                    # Documentation (VIDEO_SCRIPT.md)
├── About my project/
│   ├── journal/             # Day-by-day build log
│   └── Drawings/            # Architecture diagrams (draw.io)
└── uploads/                 # PDF uploads (created at runtime)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Groq API Key ([Get one here](https://console.groq.com))
- PostgreSQL (Supabase) or use SQLite locally

### Installation

1. **Clone and navigate:**
```bash
git clone https://github.com/SanjanaGadamsetty/socratic-tutoring-system.git
cd socratic-tutoring-system
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup environment:**
```bash
cp .env.example .env
# Edit .env:
# GROQ_API_KEY=your_key_here
# DATABASE_URL=your_postgres_url (for Supabase)
# OR
# DATABASE_URL=sqlite:///database/socratic_tutoring.db (for local SQLite)
# OR leave empty to auto-use local SQLite
```

4. **Initialize database:**
```bash
python database/init_db.py
```

5. **Start API server:**
```bash
uvicorn app.api.main:app --reload
```

6. **Access:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Test Endpoint: http://localhost:8000/

---

## 📊 Database Schema

**7 Tables:**

1. **problems** - Tutoring problems with correct answers
2. **sessions** - Individual tutoring sessions (problem or PDF-based)
3. **turns** - Conversation exchanges (tutor/student)
4. **hints_given** - Hint escalation tracking
5. **verifier_flags** - Quality control audit trail
6. **jobs** - Background job processing (Day 3)
7. **pdf_documents** - Uploaded PDFs with extracted text

See diagrams: `About my project/Drawings/2-Database-Schema.drawio`

---

## 🔄 Multi-Agent Flow

```
Student Question
    |
    v
[Handoff Controller]
    |
    | Attempt 1
    v
[Tutor Agent] → Drafts Socratic question
    |
    v
[Verifier Agent] → Checks for answer leaks
    |
    +-- APPROVE → Send to student
    |
    +-- REJECT → Add feedback, retry (Attempt 2)
        |
        v
    [Tutor Agent] → Tries again with feedback
        |
        v
    [Verifier Agent] → Checks again
        |
        +-- APPROVE → Send to student
        |
        +-- REJECT → Retry (Attempt 3)
            |
            v
        [Tutor Agent] → Extra careful attempt
            |
            v
        [Verifier Agent] → Final check
            |
            +-- APPROVE → Send to student
            |
            +-- REJECT → Use safe fallback
```

See detailed flow: `About my project/Drawings/3-Agent-Sequence-Flow.drawio`

---

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /problems` - List available problems
- `POST /sessions/start` - Start tutoring session
- `POST /sessions/{id}/turn` - Submit student response
- `GET /sessions/{id}/transcript` - Get conversation history

### Streaming
- `GET /stream/session/{id}` - SSE stream of agent events

### Background Jobs (Day 3)
- `POST /jobs` - Create background job
- `GET /jobs/{id}` - Get job status
- `POST /jobs/{id}/cancel` - Cancel job
- `GET /jobs` - List jobs
- `GET /jobs/stats` - Job statistics

### PDF Feature (Bonus)
- `POST /pdfs/upload` - Upload PDF document
- `GET /pdfs` - List uploaded PDFs
- `GET /pdfs/{id}` - Get PDF details
- `DELETE /pdfs/{id}` - Delete PDF

Full API docs at: http://localhost:8000/docs

---

## 🧪 Testing

### Run All Tests
```bash
# Individual day tests
python tests/test_day3.py
python tests/test_day4.py
python tests/test_day5_langgraph.py

# PDF feature tests
python tests/test_pdf_extraction.py
python tests/test_pdf_tutoring.py

# Comprehensive scenarios
python tests/test_comprehensive_scenarios.py

# Using pytest
python -m pytest tests/
```

### Interactive Demos (Perfect for Video Recording)
```bash
# Demo 1: Normal operation
python demos/01_happy_path_demo.py

# Demo 2: Retry mechanism
python demos/02_verifier_rejection_demo.py

# Demo 3: Error handling
python demos/03_tool_failure_demo.py

# Demo 4: Multi-agent system (MOST IMPORTANT)
python demos/04_multi_agent_architecture.py

# Demo 5: LangGraph workflow
python demos/05_langgraph_workflow_demo.py

# Demo 6: PDF tutoring
python demos/06_pdf_tutoring_demo.py
```

See `demos/README.md` for demo guide.

---

## 📝 Development Journey

This project was built over 5 days following structured requirements:

- **Day 1:** Agent fundamentals, tools, error recovery
- **Day 2:** Database, API, streaming
- **Day 3:** Background jobs, durable execution
- **Day 4:** Multi-agent system (Tutor + Verifier)
- **Day 5:** LangGraph, testing, documentation

**Total:** 6,530+ lines of production Python code

See complete journal: `About my project/journal/PROJECT_JOURNAL.md`

---

## 🎬 Video Demo

Complete 45-50 minute video recording script available at: `docs/VIDEO_SCRIPT.md`

Covers:
- Introduction and problem statement
- Architecture deep dive
- Live demos (6 scenarios)
- Code walkthrough
- Testing and wrap-up

---

## 🔑 Key Design Patterns

### 1. Multi-Agent Pattern
Two specialized agents with one orchestrator:
- Tutor: Creative (temp 0.7) - generates questions
- Verifier: Consistent (temp 0.3) - checks quality
- Handoff: Orchestration with retry logic

### 2. State Machine (LangGraph)
Declarative workflow definition:
- Nodes: Processing steps (tutor, verifier, decision, fallback)
- Edges: Flow control (simple + conditional)
- State: Data flowing through nodes

### 3. Graceful Error Handling
All tools return `{success: bool, result/error}`:
- No crashes on tool failures
- Errors returned as observations
- Agent can reason about failures and retry

### 4. Structured Outputs
Pydantic models for consistency:
- Verifier returns `{decision: "APPROVE"|"REJECT", reason: str}`
- API validates all requests/responses
- Type safety throughout

---

## 💡 Use Cases

### Problem-Based Tutoring
- Instructor creates problems with known answers
- System ensures answers are never leaked
- Complete conversation history tracking

### PDF-Based Tutoring (Bonus)
- Student uploads textbook chapter
- System extracts text, tutors from content
- Flexible, personalized learning
- No manual problem creation needed

---

## 📈 Project Statistics

- **Lines of Code:** 6,530+
- **Python Files:** 45+
- **Test Files:** 9
- **Demo Scripts:** 6
- **API Endpoints:** 15+
- **Database Tables:** 7
- **Agent Classes:** 3
- **Tools:** 3
- **Time Invested:** 46 hours

---

## 🎯 Submission Deliverables

✅ **1. Working Project** - This repository
⏳ **2. 3-Page Architecture Doc** - In progress
⏳ **3. 30+ Minute Video** - Script ready at `docs/VIDEO_SCRIPT.md`

---

## 👤 Author

**Sanjana Gadamsetty**

Built as part of **SODAK EDUTECH - AI Foundation**  
HDP 1: Agentic AI - 5-Day Project

**GitHub:** https://github.com/SanjanaGadamsetty/socratic-tutoring-system

---

## 🙏 Acknowledgments

- **SODAK EDUTECH** for project structure and requirements
- **Anthropic Claude** for development mentorship and guidance
- **Groq** for fast LLM inference
- **LangChain & LangGraph** for agent frameworks

---

## 📜 License

MIT License - feel free to use for learning and education

---

## 🔮 Future Enhancements

Post-submission ideas:
- React frontend with real-time agent visualization
- More sophisticated tools (web search, code execution)
- Fine-tuned model for Socratic questioning
- Multi-turn conversation analysis
- Student progress tracking and analytics
- Support for more document formats (Word, PPT, etc.)

---

## 🐛 Known Issues

- LangGraph workflow is parallel to Day 4 handoff (both work, choose one)
- PDF verification is lighter than problem verification (by design)
- Database file (`database/socratic_tutoring.db`) is gitignored - create with `python database/init_db.py`

---

## 📞 Contact

For questions about this project:
- Open an issue on GitHub
- See journal for detailed build process
- Check VIDEO_SCRIPT.md for comprehensive walkthrough

---

**Built with ❤️ and lots of ☕**

*"Teaching is not about giving answers, it's about asking the right questions."*
