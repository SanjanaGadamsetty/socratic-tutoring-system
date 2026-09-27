# Socratic Tutoring System

Multi-agent AI tutoring system using Socratic questioning. Built with React, FastAPI, and LangChain.

## Features

- **Practice Problems** - Solve math problems with Socratic guidance
- **PDF Upload** - Upload study materials (max 2 pages) and get tutored
- **Multi-Agent AI** - Tutor + Verifier agents ensure quality responses
- **Yellow Theme** - Beautiful Material-UI interface

## Tech Stack

**Frontend:** React + Vite + Material-UI (yellow/white theme)
**Backend:** FastAPI + Python
**AI:** LangChain + LangGraph + Groq API
**Database:** PostgreSQL (Supabase)

## Quick Start

### 1. Start the App

```bash
# Start both backend and frontend
scripts\restart_app.bat
```

Then open: http://localhost:5173

### 2. Use the App

1. **Login** with any student ID
2. **Select a Problem** or **Upload a PDF**
3. **Answer Questions** - The tutor guides you with Socratic questions
4. **Learn by Thinking** - No direct answers, only hints!

## Project Structure

```
app/               - Backend (FastAPI)
frontend/          - React UI (Material-UI)
database/          - Database models & migrations
docs/              - Documentation
scripts/           - Startup & test scripts
```

## Setup (First Time)

### Install Dependencies

**Backend:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Configure Environment

Create `.env` file:
```
GROQ_API_KEY=your_key_here
DATABASE_URL=your_supabase_url
```

### Initialize Database

```bash
python database\init_db.py
```

## Available Scripts

```bash
scripts\restart_app.bat           # Start everything
scripts\start_backend_now.bat     # Backend only
scripts\start_frontend_now.bat    # Frontend only
```

## Deployment

Ready to deploy? See: `docs/DEPLOYMENT.md`

**Deployment Stack:**
- Backend → Render (free)
- Frontend → Vercel (free)
- Database → Supabase (free)

## Development

### Backend
- **Main API:** `app/api/main.py`
- **Agents:** `app/agents/`
- **Database:** `database/models.py`

### Frontend
- **Components:** `frontend/src/components/`
- **Theme:** `frontend/src/theme.js`
- **API Client:** `frontend/src/services/api.js`

## Testing

```bash
# Test backend
python scripts/test_backend_connection.py

# Test database
python scripts/test_database.py
```

## Features in Detail

### Practice Problems
- 7 sample math problems (easy/medium/hard)
- Topics: Multiplication, Fractions, Algebra, Geometry
- Socratic questioning guides you to the answer

### PDF Tutoring
- Upload study materials (max 2 pages)
- Agent reads the content
- Asks questions based on the material
- Perfect for studying from your own notes!

### Multi-Agent System
- **Tutor Agent** - Generates Socratic questions
- **Verifier Agent** - Ensures no answer spoiling
- **Handoff Controller** - Orchestrates the flow

## Troubleshooting

**Backend not starting?**
- Check `.env` has GROQ_API_KEY
- Run: `pip install -r requirements.txt`

**Frontend not loading?**
- Run: `cd frontend && npm install`
- Check backend is running on port 8000

**Database errors?**
- Run: `python database\init_db.py`
- Check DATABASE_URL in `.env`

## License

MIT License

## Author

Built with love by Sanjana Gadamsetty
