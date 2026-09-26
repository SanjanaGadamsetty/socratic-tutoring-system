"""
DEMO 6: PDF-BASED TUTORING (Bonus Feature)

What to explain in video:
- Students can upload PDFs
- System extracts text
- Tutor asks questions based on PDF content
- No pre-defined problems needed
- Flexible, personalized learning

Time: 3-4 minutes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.utils.pdf_extractor import extract_text_from_pdf
from app.agents.handoff import HandoffController

print("=" * 70)
print("DEMO 6: PDF-BASED TUTORING (Bonus Feature)")
print("=" * 70)

print("\n[WHY PDF FEATURE?]")
print("")
print("Problem-based tutoring (original):")
print("  - Instructor creates problems manually")
print("  - Limited to pre-defined questions")
print("  - Doesn't scale")
print("")
print("PDF-based tutoring (bonus):")
print("  - Student uploads their own study materials")
print("  - System tutors from ANY content")
print("  - Personalized to student's curriculum")
print("  - Infinitely scalable!")

print("\n[FLOW]")
print("1. Student uploads PDF (textbook, notes, slides)")
print("2. System extracts text content")
print("3. Student asks questions about content")
print("4. Tutor generates Socratic questions from PDF")
print("5. Interactive learning from student's own materials")

input("\nPress ENTER to create a sample PDF...")

print("\n" + "=" * 70)
print("STEP 1: CREATING SAMPLE PDF")
print("=" * 70)

pdf_path = "demo_chemistry.pdf"
c = canvas.Canvas(pdf_path, pagesize=letter)

c.setFont("Helvetica-Bold", 16)
c.drawString(100, 750, "Chemistry: Atomic Structure")

c.setFont("Helvetica", 12)
c.drawString(100, 700, "An atom consists of a nucleus containing protons and neutrons,")
c.drawString(100, 685, "surrounded by electrons in orbitals.")

c.drawString(100, 650, "Key Points:")
c.drawString(120, 635, "- Protons: Positive charge, in nucleus")
c.drawString(120, 620, "- Neutrons: No charge, in nucleus")
c.drawString(120, 605, "- Electrons: Negative charge, in orbitals")
c.drawString(120, 590, "- Atomic number = number of protons")

c.drawString(100, 555, "The nucleus contains most of the atom's mass, while electrons")
c.drawString(100, 540, "determine chemical properties through bonding.")

c.save()

print(f"Created '{pdf_path}'")
print("Content: Chemistry notes about atomic structure")

input("\nPress ENTER to extract text from PDF...")

print("\n" + "=" * 70)
print("STEP 2: EXTRACTING TEXT")
print("=" * 70)

extraction = extract_text_from_pdf(pdf_path)

if extraction['success']:
    pdf_text = extraction['text']
    print(f"✓ Extracted {len(pdf_text)} characters")
    print(f"✓ Page count: {extraction['page_count']}")
    print(f"\nExtracted content preview:")
    print("-" * 70)
    print(pdf_text[:300] + "...")
    print("-" * 70)
else:
    print(f"✗ Extraction failed: {extraction['error']}")
    exit(1)

input("\nPress ENTER to start tutoring session with PDF...")

print("\n" + "=" * 70)
print("STEP 3: PDF-BASED TUTORING SESSION")
print("=" * 70)

print("\nScenario:")
print("  Student reads PDF about atomic structure")
print("  Student asks: 'What is an atom made of?'")
print("  System tutors using PDF content (not pre-defined answer)")

controller = HandoffController(max_retries=3)

student_question = "What is an atom made of?"
print(f"\nStudent question: '{student_question}'")

input("\nPress ENTER to run tutor with PDF context...")

result = controller.process_student_input(
    student_response=student_question,
    conversation_history="",
    pdf_content=pdf_text  # PDF content, not problem/answer
)

print("\n" + "=" * 70)
print("TUTORING RESULT")
print("=" * 70)

print(f"\nTutor's Socratic question:")
print(f"  '{result['tutor_response']}'")

print(f"\nHow it worked:")
print(f"  1. Tutor received PDF text as context")
print(f"  2. Generated question based on content")
print(f"  3. Used Socratic method (guides, doesn't tell)")
print(f"  4. Student learns through exploration")

print(f"\nMetrics:")
print(f"  Success: {result['success']}")
print(f"  Attempts: {result['attempts']}")

print("\n" + "=" * 70)
print("KEY DIFFERENCES: PROBLEM VS PDF MODE")
print("=" * 70)

print("\nProblem-based mode:")
print("  - Has specific correct answer")
print("  - Verifier checks: 'Did tutor reveal THE answer?'")
print("  - Strict verification")

print("\nPDF-based mode:")
print("  - No single 'correct answer'")
print("  - Verifier checks: 'Is tutor using Socratic method?'")
print("  - Lighter verification (asking questions?)")

print("\n" + "=" * 70)
print("API ENDPOINTS FOR PDF FEATURE")
print("=" * 70)

print("\nEndpoints implemented:")
print("  POST /pdfs/upload - Upload PDF file")
print("  GET /pdfs - List uploaded PDFs")
print("  GET /pdfs/{id} - Get PDF details")
print("  DELETE /pdfs/{id} - Delete PDF")
print("  POST /sessions/start - Start session with pdf_id")

print("\n" + "=" * 70)
print("USE CASES")
print("=" * 70)

print("\n1. College student:")
print("   - Uploads textbook chapter PDF")
print("   - Gets Socratic tutoring on chapter content")

print("\n2. Test prep:")
print("   - Uploads study guide PDF")
print("   - Practices with questions from guide")

print("\n3. Research paper:")
print("   - Uploads academic paper")
print("   - Tutor helps understand concepts")

# Cleanup
print("\n" + "=" * 70)
print("Cleaning up...")
if os.path.exists(pdf_path):
    os.remove(pdf_path)
    print(f"Deleted '{pdf_path}'")

print("\n[SUCCESS] PDF tutoring demo complete!")
print("\nThis is a BONUS feature beyond requirements!")
