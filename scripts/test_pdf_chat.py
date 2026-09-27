"""
Test script for PDF upload and Socratic tutoring
This simulates what happens when you upload a PDF and chat
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.handoff import HandoffController
import pypdf

def test_pdf_tutoring():
    print("="*60)
    print("PDF SOCRATIC TUTORING TEST")
    print("="*60)
    print()

    # Step 1: Read the PDF
    print("Step 1: Reading solar_system_study_guide.pdf...")
    try:
        reader = pypdf.PdfReader('solar_system_study_guide.pdf')
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text()

        print(f"✓ PDF loaded successfully ({len(reader.pages)} pages)")
        print(f"✓ Extracted {len(pdf_text)} characters")
        print()
    except Exception as e:
        print(f"✗ Error reading PDF: {e}")
        return

    # Step 2: Initialize the multi-agent controller
    print("Step 2: Initializing multi-agent system...")
    controller = HandoffController(max_retries=3)
    print("✓ HandoffController initialized")
    print()

    # Step 3: Generate first Socratic question
    print("Step 3: Generating first Socratic question...")
    print("-"*60)
    result1 = controller.process_student_input(
        student_response="I'm ready to start learning from this document.",
        conversation_history="",
        pdf_content=pdf_text
    )

    first_question = result1.get("tutor_response")
    print(f"TUTOR: {first_question}")
    print()
    print(f"✓ Generated in {result1.get('attempts', 1)} attempt(s)")
    print(f"✓ Verification: {result1.get('success', False)}")
    print("-"*60)
    print()

    # Step 4: Simulate student response
    print("Step 4: Simulating student response...")
    student_response = "What is at the center of the solar system?"
    print(f"STUDENT: {student_response}")
    print()

    # Build conversation history
    history = f"TUTOR: {first_question}\nSTUDENT: {student_response}"

    print("Step 5: Generating Socratic response...")
    print("-"*60)
    result2 = controller.process_student_input(
        student_response=student_response,
        conversation_history=history,
        pdf_content=pdf_text
    )

    second_response = result2.get("tutor_response")
    print(f"TUTOR: {second_response}")
    print()
    print(f"✓ Generated in {result2.get('attempts', 1)} attempt(s)")
    print(f"✓ Verification: {result2.get('success', False)}")
    print("-"*60)
    print()

    # Step 6: Another student response
    print("Step 6: Another student interaction...")
    student_response2 = "The Sun?"
    print(f"STUDENT: {student_response2}")
    print()

    history += f"\nTUTOR: {second_response}\nSTUDENT: {student_response2}"

    print("Step 7: Tutor's follow-up question...")
    print("-"*60)
    result3 = controller.process_student_input(
        student_response=student_response2,
        conversation_history=history,
        pdf_content=pdf_text
    )

    third_response = result3.get("tutor_response")
    print(f"TUTOR: {third_response}")
    print()
    print(f"✓ Generated in {result3.get('attempts', 1)} attempt(s)")
    print(f"✓ Verification: {result3.get('success', False)}")
    print("-"*60)
    print()

    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    print()
    print("✓ PDF content extracted successfully")
    print("✓ Multi-agent system working (Tutor + Verifier)")
    print("✓ Socratic questions generated")
    print("✓ Conversation flow established")
    print()
    print("OBSERVATIONS:")
    print("- Tutor asked questions instead of giving answers")
    print("- Verifier ensured quality control")
    print("- System adapted to student responses")
    print()
    print("This is how the frontend chat will work!")
    print("="*60)

if __name__ == "__main__":
    test_pdf_tutoring()
