# COMPLETE VIDEO DEMO SCRIPT
## Multi-Agent Socratic Tutoring System

**Total Time: 45-50 minutes**

This script tells you EXACTLY what to say, what to show, and what to do at every moment.

---

## SECTION 1: INTRODUCTION (3-4 minutes)

### [00:00 - 00:30] Opening

**[SCREEN: Show your face / intro slide]**

**SAY:**
> "Hello! I'm [Your Name], and today I'm presenting my 5-day AI project: a Multi-Agent Socratic Tutoring System. This project solves a real problem in AI education - how do we ensure AI tutors guide students to discover answers themselves, rather than just revealing solutions directly?"

**[ACTION: Open VS Code with your project folder]**

---

### [00:30 - 01:30] Problem Statement

**[SCREEN: Still on intro or switch to notepad with problem written]**

**SAY:**
> "The problem with traditional AI tutors is simple: they often reveal answers too quickly. A student asks 'What is 15 times 8?' and the AI says 'The answer is 120.' But that's not learning - that's just giving answers.
>
> The Socratic method is different. Instead of telling, you ask guiding questions. Like: 'Can you break 15 into 10 plus 5? How would you multiply each part by 8?'
>
> My project ensures the AI never leaks answers by using a multi-agent architecture where one agent generates questions and another agent verifies they don't reveal the answer."

---

### [01:30 - 02:30] Solution Overview

**[SCREEN: Open `About my project/Diagrams/1-Architecture-Diagram.drawio` in draw.io or show as image]**

**SAY:**
> "Here's my solution at a high level. The system has three main layers:
>
> First, the database layer using PostgreSQL on Supabase - this stores problems, sessions, conversation history, and verification logs.
>
> Second, the API layer using FastAPI - this exposes REST endpoints for starting sessions, submitting student responses, and streaming real-time updates.
>
> Third, and most importantly, the AI agent layer - this is where the magic happens. I have TWO AI agents: a Tutor Agent that generates Socratic questions, and a Verifier Agent that checks every response to ensure no answer leaking.
>
> The HandoffController orchestrates these agents in a retry loop - if the verifier rejects a response, the tutor tries again with feedback, up to 3 attempts."

**[POINT TO: Each layer in the diagram as you mention it]**

---

### [02:30 - 03:30] Technology Stack

**[SCREEN: Open `requirements.txt`]**

**FILE:** `requirements.txt`

**SAY:**
> "Let me show you the technology stack. Opening requirements.txt..."

**[ACTION: Open the file]**

**SAY:**
> "I'm using:
> - Groq API with OpenAI GPT models for the LLM
> - LangChain for agent orchestration - this gives us tools, output parsers, and agent frameworks
> - LangGraph for state machine workflows - this is the Day 5 requirement for declarative workflow management
> - FastAPI for the REST API
> - SQLAlchemy ORM with PostgreSQL on Supabase for persistence
> - PyPDF for the bonus PDF feature where students can upload study materials
>
> Everything you see here was built over 5 days following the project guidelines."

**[POINT TO: Each major dependency as you mention it - lines 2, 14, 21, 8, 7, 26]**

---

## SECTION 2: ARCHITECTURE DEEP DIVE (7-8 minutes)

### [03:30 - 05:00] Database Schema

**[SCREEN: Open `database/models.py`]**

**FILE:** `database/models.py`

**SAY:**
> "Let's start with the foundation - the database schema. Opening database/models.py..."

**[ACTION: Open file, scroll to show structure]**

**SAY:**
> "I have 7 main tables, all using SQLAlchemy ORM. Let me walk through the key ones."

**[SCROLL TO: Line 52 - Problem class]**

**SAY:**
> "First, the Problems table at line 52. This stores tutoring problems that instructors create. Each problem has a title, the problem text, the correct answer - which the tutor must NEVER reveal - and metadata like topic and difficulty level."

**[POINT TO: Lines 61-66 - the fields]**

**[SCROLL TO: Line 76 - Session class]**

**SAY:**
> "Next is the Sessions table at line 76. Each session represents one student working on one problem. Notice at line 84, we have problem_id as a foreign key. But also at line 85, we have pdf_document_id - this is optional and for the bonus PDF feature where students can upload their own study materials."

**[POINT TO: Lines 84-85]**

**[SCROLL TO: Line 101 - Turn class]**

**SAY:**
> "The Turns table at line 101 captures each back-and-forth in the conversation. Each turn has a speaker - either tutor or student - and the message content. This gives us full conversation history."

**[SCROLL TO: Line 145 - VerifierFlag class]**

**SAY:**
> "Now this is crucial - the VerifierFlag table at line 145. Every time the verifier agent rejects a tutor's response, we log it here. We store what the tutor tried to say at line 155, and why it was rejected at line 156. This creates a complete audit trail of quality control."

**[POINT TO: Lines 155-156]**

**[SCROLL TO: Line 206 - PDFDocument class]**

**SAY:**
> "And here's the PDFDocument table at line 206 for the bonus feature. When students upload a PDF, we extract the text and store it at line 214. This allows tutoring from any content, not just pre-defined problems."

**[POINT TO: Line 214]**

---

### [05:00 - 07:00] Agent Architecture

**[SCREEN: Open `app/agents/tutor_agent.py`]**

**FILE:** `app/agents/tutor_agent.py`

**SAY:**
> "Now let's look at the AI agents - the heart of the system. Opening tutor_agent.py..."

**[SCROLL TO: Lines 21-40 - TutorAgent class]**

**SAY:**
> "This is the Tutor Agent. At line 33, I initialize it with ChatGroq - that's the Groq API with OpenAI's GPT model. Notice the temperature is 0.7 at line 35 - that's relatively high because we WANT creativity in generating Socratic questions."

**[POINT TO: Lines 33-36]**

**[SCROLL TO: Lines 56-64 - system prompt]**

**SAY:**
> "The critical part is the system prompt starting at line 56. Look at the rules:
> - Line 59: NEVER state the answer directly
> - Line 60: NEVER reveal the correct answer
> - Line 61: ASK guiding questions
>
> This is the Socratic method baked into the prompt. The tutor's job is to guide, not tell."

**[POINT TO: Lines 59-61]**

**[SCROLL TO: Lines 67-75 - user prompt]**

**SAY:**
> "When we call the tutor, we pass the problem text and correct answer at lines 67-68, but we tell it explicitly: DO NOT REVEAL THIS. We also pass conversation history so it can build on previous turns."

**[POINT TO: Line 68 - DO NOT REVEAL THIS]**

---

**[SCREEN: Open `app/agents/verifier_agent.py`]**

**FILE:** `app/agents/verifier_agent.py`

**SAY:**
> "Now the second agent - the Verifier. Opening verifier_agent.py..."

**[SCROLL TO: Lines 24-30 - VerificationResult]**

**SAY:**
> "First, I define structured output using Pydantic at line 24. The verifier MUST return a decision - either APPROVE or REJECT at line 28 - plus a reason. This ensures consistent, parseable output."

**[POINT TO: Line 28]**

**[SCROLL TO: Lines 42-52 - VerifierAgent init]**

**SAY:**
> "The verifier uses the same LLM but with a key difference - look at line 50, temperature is 0.3, much lower than the tutor's 0.7. We want the verifier to be CONSISTENT and strict, not creative."

**[POINT TO: Line 50]**

**[SCROLL TO: Lines 66-94 - verification prompt]**

**SAY:**
> "The verification prompt starting at line 66 is fascinating. We give it the problem, the correct answer, and the tutor's draft response. Then at lines 78-89, we define strict decision rules:
>
> Line 79: REJECT if the answer appears anywhere
> Line 80: REJECT if it shows the final result  
> Line 82: APPROVE if only asking guiding questions
>
> This is the quality control mechanism."

**[POINT TO: Lines 79-82]**

---

**[SCREEN: Open `app/agents/handoff.py`]**

**FILE:** `app/agents/handoff.py`

**SAY:**
> "Now the orchestrator that brings them together. Opening handoff.py..."

**[SCROLL TO: Lines 16-32 - HandoffController class]**

**SAY:**
> "The HandoffController manages the tutor-verifier handoff. At line 34, we configure max_retries equals 3. If the verifier keeps rejecting, we stop after 3 attempts and use a safe fallback."

**[POINT TO: Line 34]**

**[SCROLL TO: Lines 86-128 - retry loop]**

**SAY:**
> "This is the core loop starting at line 86. Watch the flow:
>
> Line 90: Tutor generates a response
> Line 96: Verifier checks that response  
> Line 109: If APPROVED, we return it immediately
> Line 119: If REJECTED and we have retries left, we try again
> Line 126: We add the rejection reason to the conversation history
>
> This is the key: when we retry, the tutor sees WHY it was rejected and can adjust. That's the feedback loop."

**[POINT TO: Lines 90, 96, 109, 119, 126]**

**[SCROLL TO: Lines 142-148 - fallback]**

**SAY:**
> "If all 3 attempts fail, line 142, we use a safe fallback response. It's generic but guaranteed never to leak the answer. Better a generic hint than revealing the solution."

**[POINT TO: Lines 142-148]**

---

### [07:00 - 08:30] LangGraph State Machine (Day 5)

**[SCREEN: Open `app/agents/workflow.py`]**

**FILE:** `app/agents/workflow.py`

**SAY:**
> "On Day 5, I implemented the same logic using LangGraph, which is a state machine framework. Opening workflow.py..."

**[SCROLL TO: Lines 15-34 - TutoringState]**

**SAY:**
> "First, I define the state that flows through the graph at line 15. This includes input like problem_text and student_response, working state like attempt_count, and output like final_response."

**[POINT TO: Lines 15-34]**

**[SCROLL TO: Lines 37-53 - Flow diagram in comments]**

**SAY:**
> "The flow is documented at line 37. START goes to tutor_node, then verifier_node, then a decision:
> - If APPROVED, go to decision_node and END
> - If REJECTED and retries left, loop back to tutor_node
> - If REJECTED and no retries, go to fallback_node
>
> This is the same logic as handoff.py but declarative instead of imperative."

**[POINT TO: Lines 37-53]**

**[SCROLL TO: Lines 147-175 - Graph construction]**

**SAY:**
> "Building the graph at line 147. Look at the pattern:
>
> Line 150: Add nodes - tutor, verifier, fallback, decision
> Line 156: Add edges - simple flow from tutor to verifier
> Line 160: Add conditional edges - from verifier, we route based on the decision
>
> This creates a visual, debuggable workflow. Much cleaner than nested if-else statements."

**[POINT TO: Lines 150, 156, 160]**

---

## SECTION 3: LIVE DEMOS (20-25 minutes)

### [08:30 - 11:00] Demo 1: Happy Path

**[SCREEN: Terminal]**

**SAY:**
> "Alright, enough architecture. Let's see it in action. I've created 6 demo scripts that show different scenarios. Let's start with the happy path - normal successful operation."

**[ACTION: Navigate to project directory in terminal]**

**COMMAND:**
```bash
cd "C:\Users\Sanju\OneDrive\Desktop\Apps n Extensions\HOPE-Elite\HDP 1-Agentic AI\AgenticAI-Project\socratic-tutoring-system"
python demos/01_happy_path_demo.py
```

**SAY:**
> "Running demo 1..."

**[WAIT: Read the screen output]**

**SAY:**
> "Okay, it's showing the setup. Problem is 'What is 12 plus 8?', correct answer is 20, and the student says they don't know how to add. Let's run it..."

**[ACTION: Press ENTER when prompted]**

**[WAIT: Watch the output]**

**SAY WHEN YOU SEE OUTPUT:**
> "Perfect! Watch what's happening:
>
> [READ OUTPUT] The Tutor Agent is generating a response... and the Verifier is checking it...
>
> And look at the final result: [READ THE TUTOR'S RESPONSE FROM OUTPUT]
>
> Notice the tutor asked QUESTIONS, it didn't say 'the answer is 20'. It's guiding the student to think about addition. And the verifier approved it on the first attempt because it didn't leak the answer.
>
> This is the Socratic method working correctly - teaching through questioning, not telling."

---

### [11:00 - 14:30] Demo 2: Verifier Rejection & Retry

**[SCREEN: Keep terminal open]**

**SAY:**
> "Demo 2 shows what happens when the tutor makes a mistake and the verifier catches it. This is the quality control in action."

**COMMAND:**
```bash
python demos/02_verifier_rejection_demo.py
```

**SAY:**
> "This demo explains the retry mechanism..."

**[WAIT: Read intro screen]**

**SAY:**
> "So without a verifier, a tutor might accidentally say 'The answer is 120' - problem! With our verifier, it would catch that and make the tutor try again. Let's see it..."

**[ACTION: Press ENTER]**

**[WAIT: Watch output]**

**SAY WHEN OUTPUT APPEARS:**
> "Interesting - [READ WHAT HAPPENED]. In this run, the tutor got it right on the first attempt, so there was no rejection. That's actually good - it shows the tutor prompt is working well.
>
> But the important part is that the mechanism is there. Look at the code - we saw the retry loop in handoff.py. In production, when the tutor occasionally slips up and tries to reveal answers, the verifier catches it and makes it retry.
>
> The verification history shows [READ VERIFICATION DETAILS]. The verifier's reasoning is logged, the decision is tracked, and if there were rejections, we'd see each attempt with feedback.
>
> This is real AI engineering - building quality control into AI systems."

---

### [14:30 - 17:00] Demo 3: Tool Failure Recovery

**[SCREEN: Terminal]**

**SAY:**
> "Demo 3 shows graceful error handling. In production, tools fail - APIs timeout, inputs are invalid, networks drop. The system needs to handle this without crashing."

**COMMAND:**
```bash
python demos/03_tool_failure_demo.py
```

**[WAIT: Read intro]**

**SAY:**
> "We have three tools: calculator, check_answer, and get_hint. Let's test them with failures..."

**[ACTION: Press ENTER]**

**[WAIT: Watch tests run]**

**SAY FOR EACH TEST:**

**Test 1 (invalid calculator input):**
> "Test 1 - calculator with words instead of numbers. [READ OUTPUT] See? Success is false, error message is returned. The system didn't crash. The tool gracefully said 'I can't handle this' and returned an error. An agent receiving this could try a different approach."

**Test 2 (division by zero):**
> "Test 2 - division by zero. [READ OUTPUT] Again, graceful failure. Error message explains what went wrong. No crash."

**Test 3 (valid calculator):**
> "Test 3 - valid input. [READ OUTPUT] And when the input IS valid, it works perfectly. Returns success true and the result."

**Test 4-5 (other tools):**
> "Tests 4 and 5 show the other tools working. Check_answer correctly identifies right and wrong answers. Get_hint provides escalating hints - level 1 is subtle, level 3 is more direct but still doesn't give the full answer."

**[POINT TO: Each tool's output as it appears]**

**SAY:**
> "The key pattern: every tool returns a dictionary with 'success' boolean. If success is false, there's an error message. If true, there's the result. This consistent interface makes error handling systematic."

---

### [17:00 - 21:30] Demo 4: Multi-Agent Architecture ⭐ MOST IMPORTANT

**[SCREEN: Terminal]**

**SAY:**
> "Demo 4 is the most important - this demonstrates the multi-agent architecture, which is the core requirement of the project. This is what makes this project advanced AI engineering, not just calling an LLM."

**COMMAND:**
```bash
python demos/04_multi_agent_architecture.py
```

**[WAIT: Read intro screen explaining single vs multi-agent]**

**SAY:**
> "This is the key distinction. [READ THE COMPARISON FROM SCREEN]
>
> Traditional single-agent: Student to AI to Response - no quality control.
>
> Our multi-agent system: Student to Tutor to Verifier to Response - built-in quality control.
>
> Let's see the three components initialize..."

**[ACTION: Press ENTER]**

**[WAIT: See agents initialize]**

**SAY:**
> "There we go - [READ OUTPUT]
> - TutorAgent initialized with Socratic prompting
> - VerifierAgent initialized with answer leak detection  
> - HandoffController initialized with max 3 retries
>
> Two AI agents, one orchestrator. Let's watch them work together..."

**[ACTION: Press ENTER again]**

**[WAIT: Watch handoff execution]**

**SAY DURING EXECUTION:**
> "Watch the handoff in action:
> [READ WHAT'S HAPPENING]
> - Attempt 1 of 3
> - Tutor is generating a response...
> - Verifier is checking the response...
> - [READ DECISION]
>
> [IF APPROVED:]
> And it's approved! The verifier confirmed the tutor didn't leak the answer. Look at the verification reason: [READ REASON FROM OUTPUT]
>
> [IF REJECTED (unlikely but possible):]
> Interesting - it was rejected. The verifier caught something. Look at the reason: [READ REASON]. Now the tutor will try again with this feedback..."

**SAY AFTER COMPLETION:**
> "Final response to the student: [READ TUTOR RESPONSE]
>
> This is Socratic teaching. The tutor guides with questions. The verifier ensures quality. The student learns through discovery, not memorization.
>
> Why multi-agent?
> 1. Single agents make mistakes
> 2. Verifier adds a quality control layer
> 3. Catches problems before reaching students
> 4. This is the pattern used in production AI systems at companies like OpenAI and Anthropic
>
> This is the core value proposition of my project."

---

### [21:30 - 25:30] Demo 5: LangGraph State Machine

**[SCREEN: Terminal]**

**SAY:**
> "Demo 5 shows Day 5's requirement - implementing the workflow as a LangGraph state machine. This is about professional software engineering patterns in AI systems."

**COMMAND:**
```bash
python demos/05_langgraph_workflow_demo.py
```

**[WAIT: Read explanation of LangGraph]**

**SAY:**
> "LangGraph transforms imperative code into declarative workflows. [READ THE COMPARISON FROM SCREEN]
>
> Traditional: for loop, if statements, manual control flow.
> LangGraph: Define nodes, define edges, let the framework handle execution.
>
> The benefits: [READ BENEFITS FROM SCREEN]
> 1. Declarative - say WHAT not HOW
> 2. Visual - can draw the graph
> 3. Debuggable - see which node failed  
> 4. Resumable - save and restore state
> 5. Professional - used in production
>
> Let's create the workflow..."

**[ACTION: Press ENTER]**

**[WAIT: See workflow compile]**

**SAY:**
> "Workflow compiled successfully. LangGraph has built the state machine from our definitions. The nodes are registered, edges are defined, and it's ready to execute.
>
> Let's prepare the initial state and invoke it..."

**[ACTION: Press ENTER]**

**[WAIT: Watch execution with state flowing through nodes]**

**SAY DURING EXECUTION:**
> "Watch the state flow:
> [READ OUTPUT]
> - TUTOR NODE - Attempt 1/3, generating response...
> - VERIFIER NODE - Checking response...
> - [READ DECISION]
> - DECISION NODE - Finalizing...
>
> See how clean that is? The state flows through nodes automatically. We defined the graph structure, and LangGraph handles the execution, routing, and state management.
>
> Compare this to the manual loops in handoff.py - same functionality, but this is easier to visualize, debug, and maintain."

**SAY AFTER COMPLETION:**
> "The final state: [READ RESULTS]
> - Final response: [READ RESPONSE]
> - Success: [READ SUCCESS]
> - Attempts: [READ ATTEMPTS]
>
> This is modern AI engineering. Companies building production AI systems use state machines like this for complex workflows. You can export this as a diagram, you can debug at the node level, you can save and resume workflows.
>
> This is why Day 5 required LangGraph - it's the industry standard pattern."

---

### [25:30 - 29:00] Demo 6: PDF Tutoring (Bonus)

**[SCREEN: Terminal]**

**SAY:**
> "Demo 6 is a bonus feature beyond the requirements. This shows PDF-based tutoring where students can upload their own study materials and get tutored on that content."

**COMMAND:**
```bash
python demos/06_pdf_tutoring_demo.py
```

**[WAIT: Read explanation]**

**SAY:**
> "The problem with problem-based tutoring is scalability. [READ FROM SCREEN] Instructors have to manually create every problem. That doesn't scale.
>
> PDF-based tutoring is different. Students upload their textbook chapters, study guides, lecture notes - anything. The system extracts the text and tutors from that content. Infinitely scalable.
>
> Let's see it work..."

**[ACTION: Press ENTER to create PDF]**

**SAY:**
> "Creating a sample PDF about atomic structure in chemistry..."

**[WAIT: PDF created]**

**[ACTION: Press ENTER to extract]**

**SAY:**
> "Now extracting text from the PDF using the PyPDF library...
>
> [READ OUTPUT] Success! Extracted [X] characters from the PDF. Here's a preview: [READ PREVIEW]
>
> This text becomes the context for the tutor. Instead of a pre-defined problem and answer, the tutor has PDF content to work with."

**[ACTION: Press ENTER to start tutoring]**

**SAY:**
> "The student asks: 'What is an atom made of?' - a question about the PDF content. Watch the tutor respond..."

**[WAIT: See tutor response]**

**SAY:**
> "Beautiful! [READ TUTOR RESPONSE]
>
> The tutor asked a Socratic question based on the PDF content. It's not revealing information from the text - it's guiding the student to engage with the material and think.
>
> The key difference: [READ FROM SCREEN]
> - Problem mode: has specific answer to avoid
> - PDF mode: no specific answer, just guide exploration
>
> Use cases: 
> - College student uploads textbook chapter, gets tutoring
> - Test prep: upload study guide
> - Research: upload academic paper, tutor helps understand
>
> This is a bonus feature that makes the system much more flexible and practical."

---

## SECTION 4: CODE WALKTHROUGH (8-10 minutes)

### [29:00 - 31:00] Database Schema Deep Dive

**[SCREEN: Open `database/models.py`]**

**FILE:** `database/models.py`

**SAY:**
> "Now let's walk through the actual code that makes this work. Starting with the database schema - this is the foundation for persistence."

**[SCROLL TO: Line 22 - DifficultyLevel enum]**

**SAY:**
> "At line 22, I define enums for data validation. DifficultyLevel can only be EASY, MEDIUM, or HARD. This prevents bad data at the database level."

**[SCROLL TO: Line 29 - SessionStatus enum]**

**SAY:**
> "SessionStatus at line 29 tracks the lifecycle: STARTED, IN_PROGRESS, COMPLETED, or ABANDONED. This state machine helps us track how students are progressing."

**[SCROLL TO: Line 69 - relationships]**

**SAY:**
> "Line 69 shows SQLAlchemy relationships. This line says 'a Problem has many Sessions'. Later at line 92, the reverse: 'a Session belongs to one Problem'. These relationships let us navigate: problem.sessions gives all sessions for that problem. This is ORM magic - Object-Relational Mapping."

**[POINT TO: Lines 69, 92]**

**[SCROLL TO: Line 93 - cascade]**

**SAY:**
> "Line 93: cascade='all, delete-orphan'. This means when you delete a session, automatically delete all its turns, hints, and verifier flags. Keeps the database clean. Without this, you'd have orphaned records."

**[POINT TO: Line 93]**

---

### [31:00 - 33:00] API Layer

**[SCREEN: Open `app/api/main.py`]**

**FILE:** `app/api/main.py`

**SAY:**
> "Now the API layer that exposes the system over HTTP. Opening main.py..."

**[SCROLL TO: Lines 35-48 - FastAPI app creation]**

**SAY:**
> "Lines 35-39: Create the FastAPI application with title, description, and version. This generates automatic API documentation at /docs."

**[SCROLL TO: Line 42-48 - CORS]**

**SAY:**
> "Lines 42-48: CORS middleware. This allows the frontend (when we build it) to call the API from a different domain. In production, you'd restrict this to specific origins, but for development, allow_origins=['*'] works."

**[SCROLL TO: Line 51-54 - routers]**

**SAY:**
> "Lines 51-54: Include routers. This is modular API design. Instead of one giant file, I split endpoints into:
> - Streaming router for SSE (Server-Sent Events)
> - Jobs router for background tasks
> - PDFs router for document upload
>
> Each router is in its own file under app/api/."

**[POINT TO: Each include_router line]**

**[SCROLL TO: Around line 80 - start session endpoint]**

**SAY:**
> "Here's a key endpoint - start a session. [FIND AND SHOW THE ENDPOINT]
> This creates a new tutoring session, links it to a problem or PDF, and returns a session ID.
>
> Notice the db: Session = Depends(get_db) parameter - this is dependency injection. FastAPI automatically provides a database connection to each request."

---

### [33:00 - 36:00] Tool Implementation

**[SCREEN: Open `app/tools/basic_tools.py`]**

**FILE:** `app/tools/basic_tools.py`

**SAY:**
> "Let's look at the tools that agents can use. Opening basic_tools.py..."

**[SCROLL TO: Calculator function]**

**SAY:**
> "The calculator tool. [FIND IT IN THE FILE]
>
> Notice the try-except pattern. Line [X]: try to evaluate the expression. If it works, return success: True with the result. If it fails - line [X] - catch the exception and return success: False with the error message.
>
> No crash. No exception thrown. Just a clean error response that the agent can reason about.
>
> This is how you build robust AI systems."

**[POINT TO: The try/except blocks]**

**[SCROLL TO: check_answer function]**

**SAY:**
> "The check_answer tool compares student's answer to the correct answer. Simple string comparison, returns 'correct' or 'incorrect'. Notice we convert both to strings and lowercase for comparison - handles '120' vs '120.0' vs '120 '."

**[SCROLL TO: get_hint function]**

**SAY:**
> "The get_hint tool provides escalating hints. Level 1 is subtle, level 2 is more direct, level 3 basically gives it away. This is another way to guide students - not questions, but progressively stronger hints."

---

### [36:00 - 37:30] Error Handling Patterns

**[SCREEN: Open `app/agents/handoff.py` again]**

**FILE:** `app/agents/handoff.py`

**SAY:**
> "One more thing about the code - error handling patterns. Back to handoff.py..."

**[SCROLL TO: The fallback function around line 142]**

**SAY:**
> "The fallback at line 142. When ALL retries fail - tutor tried 3 times and verifier rejected each one - we don't crash, we don't give up, we return a safe generic question.
>
> It's not great - it's generic. But it's SAFE. It will never leak an answer. And that's the priority in education.
>
> Better a mediocre safe response than a brilliant response that teaches by giving answers."

**[POINT TO: The fallback implementation]**

---

## SECTION 5: TESTING & QUALITY (3-4 minutes)

### [37:30 - 40:00] Test Coverage

**[SCREEN: Open file explorer showing tests/ folder]**

**SAY:**
> "Quality matters, so I wrote comprehensive tests. Let me show you the tests folder..."

**[ACTION: Navigate to tests/ folder]**

**SAY:**
> "I have tests for:
> - Day 1: Agent fundamentals
> - Day 2: API endpoints  
> - Day 3: Background jobs
> - Day 4: Multi-agent system
> - Day 5: LangGraph workflow
> - PDF extraction
> - PDF tutoring
>
> Plus the 6 demo scripts we just ran.
>
> Each test covers a normal case, a failure case, and edge cases specific to that feature."

**[ACTION: Open `tests/test_day4.py` as example]**

**FILE:** `tests/test_day4.py`

**SAY:**
> "For example, test_day4.py tests the multi-agent system. It sets up a problem, runs the handoff controller, and verifies:
> - The tutor generated a response
> - The verifier checked it
> - The system handled rejections (if any)
> - The final response doesn't leak the answer
>
> This ensures the core feature works before I deploy."

---

## SECTION 6: ARCHITECTURE DOCUMENTATION (2-3 minutes)

### [40:00 - 42:00] Three-Page Document

**[SCREEN: Open the 3-page architecture document you'll create next]**

**SAY:**
> "For submission, I created a 3-page architecture document. Let me show you..."

**[ACTION: Open the PDF]**

**SAY:**
> "Page 1: Problem statement and high-level architecture diagram. This shows the flow: Client calls API, API triggers agents, agents use tools, everything persists to database.

**[SHOW: Page 1]**

**SAY:**
> "Page 2: Database schema and API endpoints. The schema shows the 7 tables and their relationships. The endpoints list shows what the API exposes.

**[SHOW: Page 2]**

**SAY:**
> "Page 3: The agent/LangGraph flow - this is what graders care about most. It shows:
> - The tutor agent loop
> - The verifier agent logic  
> - The handoff pattern with retry
> - The LangGraph state machine nodes and edges
>
> This page proves I understand AI architecture, not just how to call an LLM."

**[SHOW: Page 3]**

---

## SECTION 7: WRAP-UP (2-3 minutes)

### [42:00 - 44:30] Reflections

**[SCREEN: Back to your face or final slide]**

**SAY:**
> "Let me wrap up with reflections on the 5-day journey.
>
> **What was hardest:**
> The hardest part was getting the verifier to be strict enough to catch answer leaks but not so strict it rejects everything. I went through many prompt iterations. The key was providing clear examples of what counts as leaking vs guiding.
>
> **What I'd do differently with more time:**
> 1. Add more sophisticated tools - web search, code execution, knowledge graphs
> 2. Build a React frontend with real-time streaming visualization
> 3. Add support for multi-turn conversation analysis - looking at patterns across multiple exchanges
> 4. Fine-tune a smaller model specifically for Socratic questioning
>
> **What I learned:**
> This project taught me that building production AI systems is not just about calling an LLM. It's about:
> - Multi-agent architectures for quality control
> - State machines for complex workflows
> - Error handling at every layer
> - Structured outputs for reliability
> - Persistence for durability
> - Testing for confidence
>
> These are the skills that separate hobbyist AI projects from production systems."

---

### [44:30 - 45:30] Summary

**SAY:**
> "To summarize what I built:
>
> **Database Layer:**
> 7 tables with SQLAlchemy ORM on Supabase PostgreSQL. Full conversation history, verification audit logs, and support for both problems and PDFs.
>
> **API Layer:**
> FastAPI REST API with endpoints for sessions, turns, jobs, and PDFs. Server-Sent Events for real-time streaming. Background job processing for durable execution.
>
> **AI Layer - The Core:**
> Two AI agents - Tutor and Verifier - orchestrated by a HandoffController with retry logic. Implemented both imperatively (Day 4) and declaratively with LangGraph (Day 5). This multi-agent architecture ensures quality control through verification and retry with feedback.
>
> **Tools:**
> Calculator, answer checker, and hint system with graceful error handling. PDF extraction with PyPDF for document-based tutoring.
>
> **Testing:**
> Comprehensive tests covering normal operation, failure recovery, and edge cases for every major feature.
>
> **Lines of Code:**
> Over 6,500 lines of production Python code across 5 days, with full version control on GitHub."

---

### [45:30 - 46:00] Closing

**SAY:**
> "The complete project is on GitHub at [SHOW GITHUB URL ON SCREEN]. Every commit is documented, every feature is tested, and the code is ready to run locally.
>
> This project demonstrates that I can:
> - Design multi-agent AI systems
> - Implement quality control in AI
> - Use modern frameworks like LangChain and LangGraph
> - Build robust, error-tolerant systems
> - Work through a 5-day engineering sprint
>
> Thank you for watching. I'm excited to discuss this project further."

**[SCREEN: Show final slide with GitHub URL, your name, and project title]**

---

## POST-RECORDING CHECKLIST:

Before you submit, verify you covered:

✅ Introduction (2-3 min) - Problem and approach
✅ Architecture walkthrough (5-7 min) - Page 1/3 diagrams  
✅ Live demo (10-15 min) - Happy path + failure case
✅ Code walkthrough (5-8 min) - Agent loop, tools, schema
✅ Wrap-up (2-3 min) - Hardest parts, learnings

✅ Video is 30+ minutes (you should be 45-50 min)
✅ Shows actual code (file paths and line numbers)
✅ Runs live demos (not slides)
✅ Explains the multi-agent architecture clearly
✅ Uploaded to YouTube (unlisted is fine)

---

**YOU'RE READY TO RECORD! 🎥**

**Pro tips:**
- Practice each section once before recording
- Keep water nearby
- You can pause and restart sections - edit later
- Speak slowly and clearly
- Show enthusiasm - this is cool tech!
- If you mess up, just start that section over

**Good luck!**
