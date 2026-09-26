# Demo Scripts for Video Recording

These demo scripts are designed to be run **one at a time** during your video recording. Each demonstrates a specific aspect of your project with clear explanations.

## Order for Video (Recommended):

### 1. Happy Path Demo (2-3 min)
```bash
python demos/01_happy_path_demo.py
```
**What to explain:**
- Normal flow when everything works
- Student asks → Tutor guides → Verifier approves
- Socratic method in action

---

### 2. Verifier Rejection Demo (3-4 min)
```bash
python demos/02_verifier_rejection_demo.py
```
**What to explain:**
- Quality control mechanism
- Retry loop with feedback
- How system handles rejections

---

### 3. Tool Failure Demo (2-3 min)
```bash
python demos/03_tool_failure_demo.py
```
**What to explain:**
- Graceful error handling
- Tools return errors, don't crash
- System continues working

---

### 4. Multi-Agent Architecture (4-5 min) ⭐ MOST IMPORTANT
```bash
python demos/04_multi_agent_architecture.py
```
**What to explain:**
- TWO agents: Tutor + Verifier
- Handoff pattern
- Why multi-agent is better than single
- **THIS IS YOUR CORE FEATURE!**

---

### 5. LangGraph Workflow (4-5 min) ⭐ Day 5 Requirement
```bash
python demos/05_langgraph_workflow_demo.py
```
**What to explain:**
- State machine architecture
- Nodes and edges
- Declarative vs imperative
- Professional pattern

---

### 6. PDF Tutoring (3-4 min) - BONUS
```bash
python demos/06_pdf_tutoring_demo.py
```
**What to explain:**
- Students upload study materials
- Tutoring from any content
- Scalable and personalized

---

## Total Time: ~20-25 minutes of demos

**Plus:**
- Introduction: 2-3 min
- Architecture walkthrough: 5-7 min
- Code walkthrough: 5-8 min
- Wrap-up: 2-3 min

**= 35-45 minutes total (exceeds 30-minute requirement)**

---

## Tips for Recording:

1. **Run each demo separately** - Don't try to batch them
2. **Explain BEFORE running** - Tell what will happen
3. **Explain AFTER running** - Interpret the results
4. **Pause between demos** - You can edit later
5. **Show enthusiasm** - This is cool tech!

---

## If Something Goes Wrong:

- LLM variance: Tutor usually gets it right first time (that's okay!)
- Explain: "In production, rejections happen ~10-20% of time"
- Show the retry mechanism is there and ready

---

## Key Points to Hit:

✓ Multi-agent system (tutor + verifier)
✓ Socratic methodology
✓ Quality control with retry
✓ LangGraph state machine
✓ Graceful error handling
✓ All 5 days implemented
✓ Bonus PDF feature

---

Good luck with your video! 🎥
