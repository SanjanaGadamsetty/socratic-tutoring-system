"""
Server-Sent Events (SSE) streaming endpoints.

Allows clients to watch the agent thinking in real-time.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from database.models import Problem, Session as DBSession, Turn, Speaker, SessionStatus
from database.connection import get_db
from app.api.schemas import TurnSubmitRequest


router = APIRouter()


class StreamingAgent:
    """
    Wrapper around TutoringAgent that yields progress events.
    """

    def __init__(self):
        from app.agent import TutoringAgent
        self.agent = TutoringAgent()

    async def run_with_streaming(self, prompt: str, max_iterations: int = 5) -> AsyncGenerator[dict, None]:
        """
        Run agent and yield progress events.

        Yields:
            Events like:
                {"type": "thinking", "message": "Agent is thinking..."}
                {"type": "tool_call", "tool": "calculator", "args": {...}}
                {"type": "tool_result", "result": {...}}
                {"type": "response", "message": "Final response"}
        """
        yield {"type": "status", "message": "Initializing agent..."}
        await asyncio.sleep(0.1)  # Small delay for demo effect

        # Build conversation
        self.agent.messages = [
            {"role": "system", "content": self.agent._build_system_prompt()},
            {"role": "user", "content": prompt}
        ]

        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            yield {"type": "status", "message": f"Iteration {iteration}/{max_iterations}"}

            try:
                # Call LLM
                yield {"type": "thinking", "message": "Agent is thinking..."}
                await asyncio.sleep(0.1)

                response = self.agent.client.chat.completions.create(
                    model=self.agent.model,
                    messages=self.agent.messages,
                    temperature=0.7,
                    max_tokens=500
                )

                assistant_message = response.choices[0].message.content

                # Add to conversation
                self.agent.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })

                # Check for tool call
                tool_call = self.agent._parse_tool_call(assistant_message)

                if tool_call:
                    # Agent wants to use a tool
                    yield {
                        "type": "tool_call",
                        "tool": tool_call["tool"],
                        "arguments": tool_call["arguments"]
                    }

                    # Execute tool
                    tool_result = self.agent._execute_tool(
                        tool_call["tool"],
                        tool_call["arguments"]
                    )

                    yield {
                        "type": "tool_result",
                        "result": tool_result
                    }

                    # Add observation to conversation
                    observation = f"TOOL_RESULT: {json.dumps(tool_result, indent=2)}"
                    self.agent.messages.append({
                        "role": "user",
                        "content": observation
                    })

                    # Continue loop
                else:
                    # No tool call - agent is done
                    yield {
                        "type": "response",
                        "message": assistant_message
                    }
                    break

            except Exception as e:
                yield {
                    "type": "error",
                    "message": str(e)
                }
                # Add error to conversation and continue
                self.agent.messages.append({
                    "role": "user",
                    "content": f"Error: {str(e)}. Let me try a different approach."
                })

        yield {"type": "complete"}


@router.post("/sessions/{session_id}/turn/stream")
async def submit_turn_streaming(
    session_id: int,
    request: TurnSubmitRequest,
    db: Session = Depends(get_db)
):
    """
    Submit student turn and stream the agent's thinking process in real-time.

    Returns Server-Sent Events (SSE) stream.

    Event types:
        - status: General status updates
        - thinking: Agent is processing
        - tool_call: Agent is using a tool
        - tool_result: Tool execution result
        - response: Final agent response
        - complete: Stream finished
    """

    # Validate session
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    problem = session.problem

    # Save student turn
    turn_number = db.query(Turn).filter(Turn.session_id == session_id).count() + 1

    student_turn = Turn(
        session_id=session_id,
        turn_number=turn_number,
        speaker=Speaker.STUDENT,
        message=request.student_answer
    )
    db.add(student_turn)
    db.commit()

    # Check if correct
    is_correct = request.student_answer.strip().lower() == problem.correct_answer.strip().lower()

    async def event_generator():
        """Generate SSE events"""

        if is_correct:
            # Student got it right
            session.status = SessionStatus.COMPLETED
            db.commit()

            yield {
                "event": "message",
                "data": json.dumps({
                    "type": "correct",
                    "message": "Excellent! You got it right!"
                })
            }

            tutor_response = "Excellent! You got it right! Great work using logical thinking to solve this problem."
        else:
            # Generate next question with streaming
            agent = StreamingAgent()

            # Get conversation history
            previous_turns = db.query(Turn).filter(
                Turn.session_id == session_id
            ).order_by(Turn.turn_number).all()

            history = "\n".join([
                f"{turn.speaker.value.upper()}: {turn.message}"
                for turn in previous_turns
            ])

            prompt = f"""You are continuing a Socratic tutoring session.

Problem: {problem.problem_text}
Correct Answer (DO NOT REVEAL): {problem.correct_answer}

Conversation so far:
{history}

The student's latest answer is INCORRECT. Generate your next Socratic question to guide them closer to the answer.
Remember: ASK guiding questions, don't reveal the answer!"""

            tutor_response = None

            async for event in agent.run_with_streaming(prompt, max_iterations=3):
                # Stream each event to client
                yield {
                    "event": "message",
                    "data": json.dumps(event)
                }

                if event["type"] == "response":
                    tutor_response = event["message"]

        # Save tutor turn
        tutor_turn = Turn(
            session_id=session_id,
            turn_number=turn_number + 1,
            speaker=Speaker.TUTOR,
            message=tutor_response
        )
        db.add(tutor_turn)
        db.commit()

        # Send final event
        yield {
            "event": "message",
            "data": json.dumps({
                "type": "complete",
                "session_id": session_id,
                "is_correct": is_correct,
                "session_status": session.status.value
            })
        }

    return EventSourceResponse(event_generator())


# ===== EXPLANATION =====

"""
WHAT IS SERVER-SENT EVENTS (SSE)?

HTTP request that stays open and sends multiple messages:

Normal HTTP:
    Client: "Give me data"
    Server: "Here's data" [connection closes]

SSE:
    Client: "Give me data"
    Server: "Here's update 1..."
    Server: "Here's update 2..."
    Server: "Here's update 3..."
    Server: "Done" [connection closes]

HOW SSE WORKS:

1. Client connects to endpoint
2. Server yields events one by one
3. Client receives each event in real-time
4. Connection stays open until complete

FLOW:

Client opens SSE connection
    |
    v
Server yields: {"type": "status", "message": "Starting..."}
    |
    v
Client receives event, updates UI
    |
    v
Server yields: {"type": "thinking", "message": "Agent thinking..."}
    |
    v
Client receives, shows loading spinner
    |
    v
Server yields: {"type": "tool_call", "tool": "calculator"}
    |
    v
Client receives, shows "Using calculator..."
    |
    v
Server yields: {"type": "response", "message": "Final answer"}
    |
    v
Client receives, displays answer
    |
    v
Server yields: {"type": "complete"}
    |
    v
Connection closes

WHY USE SSE?

Better user experience:
    - User sees progress in real-time
    - Not just waiting with no feedback
    - Can see agent thinking process
    - More transparent AI behavior

DEMO CODE TO CONSUME SSE:

    JavaScript:
        const eventSource = new EventSource('/sessions/1/turn/stream');
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(data.type, data.message);
        };

    Python:
        import sseclient
        response = requests.post(url, stream=True)
        client = sseclient.SSEClient(response)
        for event in client.events():
            data = json.loads(event.data)
            print(data)
"""
