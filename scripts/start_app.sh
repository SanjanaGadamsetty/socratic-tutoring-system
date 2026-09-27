#!/bin/bash

# Startup script for Socratic Tutoring System
# This script starts both backend and frontend

echo "================================"
echo "Socratic Tutoring System Startup"
echo "================================"
echo ""

# Check if backend dependencies are installed
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python -m venv venv
    source venv/Scripts/activate
    pip install -r requirements.txt
else
    echo "✓ Virtual environment found"
    source venv/Scripts/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Frontend dependencies not found. Installing..."
    cd frontend
    npm install
    cd ..
else
    echo "✓ Frontend dependencies found"
fi

echo ""
echo "Starting services..."
echo ""

# Start backend in background
echo "Starting FastAPI backend on http://localhost:8000"
python -m uvicorn app.api.main:app --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting React frontend on http://localhost:5173"
cd frontend
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
