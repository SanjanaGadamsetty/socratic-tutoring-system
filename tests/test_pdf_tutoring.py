"""
Test PDF-Based Tutoring - Complete test of PDF feature with multi-agent system.

This demonstrates:
1. Creating a PDF with study material
2. Extracting text from PDF
3. Using PDF content for Socratic tutoring
4. Multi-agent handoff (tutor + verifier) with PDF context
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.utils.pdf_extractor import extract_text_from_pdf
from app.agents.handoff import HandoffController

print("=" * 60)
print("PDF-BASED TUTORING TEST")
print("=" * 60)

# Step 1: Create a sample PDF with biology content
print("\n[1/4] Creating sample biology PDF...")

pdf_path = "test_biology_photosynthesis.pdf"
c = canvas.Canvas(pdf_path, pagesize=letter)

# Add rich content about photosynthesis
c.setFont("Helvetica-Bold", 16)
c.drawString(100, 750, "Chapter 3: Photosynthesis")

c.setFont("Helvetica", 12)
c.drawString(100, 700, "Photosynthesis is the process by which plants convert light energy into chemical energy.")
c.drawString(100, 685, "This process occurs in the chloroplasts of plant cells.")

c.drawString(100, 650, "The overall equation:")
c.setFont("Courier", 11)
c.drawString(120, 635, "6CO2 + 6H2O + light energy -> C6H12O6 + 6O2")

c.setFont("Helvetica", 12)
c.drawString(100, 600, "Key Points:")
c.drawString(120, 585, "1. Takes place in chloroplasts")
c.drawString(120, 570, "2. Requires chlorophyll (green pigment)")
c.drawString(120, 555, "3. Has two main stages: light-dependent and light-independent")
c.drawString(120, 540, "4. Produces glucose and oxygen")

c.drawString(100, 505, "Light-Dependent Reactions:")
c.drawString(120, 490, "- Occur in thylakoid membranes")
c.drawString(120, 475, "- Require sunlight")
c.drawString(120, 460, "- Produce ATP and NADPH")
c.drawString(120, 445, "- Release oxygen as byproduct")

c.drawString(100, 410, "Calvin Cycle (Light-Independent):")
c.drawString(120, 395, "- Occurs in the stroma")
c.drawString(120, 380, "- Uses ATP and NADPH from light reactions")
c.drawString(120, 365, "- Fixes carbon dioxide")
c.drawString(120, 350, "- Produces glucose")

c.save()

print(f"Created '{pdf_path}'")

# Step 2: Extract text from PDF
print("\n[2/4] Extracting text from PDF...")

extraction_result = extract_text_from_pdf(pdf_path)

if not extraction_result["success"]:
    print(f"FAILED: {extraction_result['error']}")
    os.remove(pdf_path)
    exit(1)

pdf_text = extraction_result["text"]
print(f"Extracted {len(pdf_text)} characters")
print(f"Preview: {pdf_text[:200]}...")

# Step 3: Initialize multi-agent system
print("\n[3/4] Initializing multi-agent tutoring system...")

controller = HandoffController(max_retries=3)

# Step 4: Test PDF-based tutoring conversation
print("\n[4/4] Starting PDF-based tutoring session...")
print("=" * 60)

# Scenario: Student asks about photosynthesis
student_question = "I'm reading about photosynthesis but I'm confused. Can you help me understand what it is?"

print(f"\nSTUDENT: {student_question}")

# Process through tutor-verifier system
result = controller.process_student_input(
    student_response=student_question,
    conversation_history="",
    pdf_content=pdf_text  # Pass PDF content instead of problem/answer
)

print("\n" + "=" * 60)
print("TUTORING RESULT")
print("=" * 60)

print(f"\nTUTOR RESPONSE:")
print(f"  {result['tutor_response']}")

print(f"\nMETRICS:")
print(f"  Attempts: {result['attempts']}")
print(f"  Success: {result['success']}")
print(f"  Final Verdict: {result['final_verdict']}")

print(f"\nVERIFICATION HISTORY:")
for v in result['verifications']:
    print(f"\n  Attempt {v['attempt']}:")
    print(f"    Decision: {v['verification']['decision']}")
    print(f"    Reason: {v['verification']['reason']}")

# Test second turn
print("\n" + "=" * 60)
print("SECOND TURN - Student follow-up")
print("=" * 60)

student_followup = "You mentioned chloroplasts. What are those exactly?"

print(f"\nSTUDENT: {student_followup}")

# Add first turn to history
conversation_history = f"Student: {student_question}\nTutor: {result['tutor_response']}\n"

result2 = controller.process_student_input(
    student_response=student_followup,
    conversation_history=conversation_history,
    pdf_content=pdf_text
)

print(f"\nTUTOR RESPONSE:")
print(f"  {result2['tutor_response']}")

# Cleanup
print("\n" + "=" * 60)
print("Cleaning up...")
if os.path.exists(pdf_path):
    os.remove(pdf_path)
    print(f"Deleted '{pdf_path}'")

print("\n" + "=" * 60)
print("PDF-BASED TUTORING TEST COMPLETE!")
print("=" * 60)

print("\nWHAT WE DEMONSTRATED:")
print("1. PDF text extraction")
print("2. PDF content as context for tutor agent")
print("3. Socratic questioning based on PDF material")
print("4. Multi-agent quality control (tutor + verifier)")
print("5. Conversational flow with PDF context")

print("\nKEY DIFFERENCE FROM PROBLEM-BASED:")
print("- Problem-based: Tutor has specific answer to avoid revealing")
print("- PDF-based: Tutor guides exploration of PDF content")
print("- Both use Socratic method!")

print("\nNEXT: Integrate with API endpoints for full feature!")
