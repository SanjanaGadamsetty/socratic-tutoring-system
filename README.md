# 🎓 Socratic Tutoring System

A multi-agent AI tutoring system that uses **Socratic questioning** to guide students toward understanding, rather than giving direct answers.

---

## 🌟 Features

- **Dual-Agent Architecture:**
  - **Tutor Agent**: Generates guiding Socratic questions
  - **Verifier Agent**: Ensures the tutor never leaks the answer
  
- **Smart Retry Loop**: If verifier catches answer leakage, tutor regenerates (max 3 retries)

- **Session Management**: Track full conversation history, hints given, and verifier flags

- **PDF Support (Bonus)**: Upload PDFs and get tutored on their content using RAG

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **AI/LLM**: OpenAI GPT models
- **Agents**: LangChain + LangGraph
- **Vector DB**: ChromaDB (for PDF feature)

---

## 📁 Project Structure

```
socratic-tutoring-system/
├── app/
│   ├── agents/          # Tutor & Verifier agents
│   ├── tools/           # Agent tools
│   └── api/             # FastAPI endpoints
├── database/            # Schema & migrations
├── tests/               # Test files
├── About my project/    
│   └── Drawings/        # Architecture diagrams
└── PROJECT_JOURNAL.md   # Build log
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL
- OpenAI API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd socratic-tutoring-system
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Run database migrations:**
   ```bash
   # Coming soon in Day 2
   ```

6. **Start the server:**
   ```bash
   # Coming soon in Day 2
   ```

---

## 📊 Database Schema

- `problems` - Stores tutoring problems
- `sessions` - Tracks each tutoring session
- `turns` - Every question/answer exchange
- `hints_given` - Hint escalation tracking
- `verifier_flags` - When verifier rejects tutor's response

See `About my project/Drawings/2-Database-Schema.drawio` for visual representation.

---

## 🔄 Agent Flow

1. Student asks a question
2. Tutor drafts a Socratic question
3. Verifier checks if it leaks the answer
4. If rejected → tutor retries (max 3 times)
5. If approved → question sent to student
6. Loop continues until problem is solved

See `About my project/Drawings/3-Agent-Sequence-Flow.drawio` for detailed flow.

---

## 📡 API Endpoints

- `POST /sessions/start` - Start a new tutoring session
- `POST /sessions/{id}/turn` - Submit answer, get next question
- `GET /sessions/{id}/transcript` - Get full conversation history

*(PDF endpoints coming in bonus feature)*

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📝 Development Progress

See `PROJECT_JOURNAL.md` for detailed build log.

---

## 👤 Author

**Sanju**  
Building this as part of HDP 1 - Agentic AI course

---

## 📜 License

MIT License (or specify your license)

---

## 🙏 Acknowledgments

- SODAK EDUTECH - AI Foundation Course
- Anthropic Claude for mentorship assistance
