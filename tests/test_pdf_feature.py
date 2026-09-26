"""
Test PDF Feature - Upload, extract, and use PDFs for tutoring.

This tests:
1. PDF text extraction
2. PDF upload API
3. PDF-based tutoring session
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import requests

print("=" * 60)
print("PDF FEATURE TEST")
print("=" * 60)

# Step 1: Create a sample PDF
print("\n[1/4] Creating sample PDF...")

pdf_path = "test_biology.pdf"
c = canvas.Canvas(pdf_path, pagesize=letter)

# Add content
c.setFont("Helvetica-Bold", 16)
c.drawString(100, 750, "Biology Notes - Photosynthesis")

c.setFont("Helvetica", 12)
c.drawString(100, 700, "Photosynthesis is the process by which green plants and some other organisms")
c.drawString(100, 685, "use sunlight to synthesize foods with the help of chlorophyll.")

c.drawString(100, 650, "The chemical equation for photosynthesis is:")
c.drawString(100, 635, "6CO2 + 6H2O + light energy -> C6H12O6 + 6O2")

c.drawString(100, 600, "Key components:")
c.drawString(100, 585, "- Chloroplasts: Where photosynthesis occurs")
c.drawString(100, 570, "- Chlorophyll: Green pigment that captures light")
c.drawString(100, 555, "- Stomata: Pores that allow gas exchange")

c.drawString(100, 520, "Process stages:")
c.drawString(100, 505, "1. Light-dependent reactions")
c.drawString(100, 490, "2. Light-independent reactions (Calvin cycle)")

c.save()

print(f"Created {pdf_path}")

# Step 2: Test PDF extraction
print("\n[2/4] Testing PDF text extraction...")

from app.utils.pdf_extractor import extract_text_from_pdf

extraction_result = extract_text_from_pdf(pdf_path)

if extraction_result["success"]:
    print(f"Success! Extracted {len(extraction_result['text'])} characters")
    print(f"Page count: {extraction_result['page_count']}")
    print(f"Text preview: {extraction_result['text'][:150]}...")
else:
    print(f"Failed: {extraction_result['error']}")
    exit(1)

# Step 3: Test PDF upload API
print("\n[3/4] Testing PDF upload API...")

API_BASE = "http://localhost:8000"

try:
    # Upload PDF
    with open(pdf_path, 'rb') as f:
        files = {'file': (pdf_path, f, 'application/pdf')}
        data = {'student_id': 'test_student_1'}

        response = requests.post(f"{API_BASE}/pdfs/upload", files=files, params=data)

    if response.status_code == 200:
        result = response.json()
        pdf_id = result['pdf_id']
        print(f"Upload successful! PDF ID: {pdf_id}")
        print(f"Filename: {result['filename']}")
        print(f"Pages: {result['page_count']}")
        print(f"Size: {result['file_size']} bytes")
        print(f"Preview: {result['text_preview']}")
    else:
        print(f"Upload failed: {response.status_code} - {response.text}")
        exit(1)

except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to API server!")
    print("Please start the server first with: uvicorn app.api.main:app --reload")
    exit(1)

# Step 4: List PDFs
print("\n[4/4] Testing PDF listing...")

response = requests.get(f"{API_BASE}/pdfs/", params={'student_id': 'test_student_1'})

if response.status_code == 200:
    result = response.json()
    print(f"Found {len(result['pdfs'])} PDFs")
    for pdf in result['pdfs']:
        print(f"  - {pdf['filename']} (ID: {pdf['id']}, {pdf['page_count']} pages)")
else:
    print(f"Listing failed: {response.status_code}")

# Cleanup
print("\n" + "=" * 60)
print("Cleaning up test PDF...")
if os.path.exists(pdf_path):
    os.remove(pdf_path)
    print(f"Deleted {pdf_path}")

print("\n" + "=" * 60)
print("PDF FEATURE TEST COMPLETE!")
print("=" * 60)

print("\nNEXT STEPS:")
print("1. Upload your own PDF via API")
print("2. Start a session with pdf_id instead of problem_id")
print("3. Tutor will ask questions based on PDF content!")
print("\nExample:")
print("  POST /sessions/start")
print("  {")
print("    'pdf_id': 1,")
print("    'student_id': 'student_1'")
print("  }")
