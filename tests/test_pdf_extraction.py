"""
Test PDF Extraction - Test text extraction from PDF files.

This is a standalone test that doesn't require the API server.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.utils.pdf_extractor import extract_text_from_pdf, get_pdf_summary

print("=" * 60)
print("PDF EXTRACTION TEST")
print("=" * 60)

# Step 1: Create a sample PDF
print("\n[1/3] Creating sample PDF...")

pdf_path = "test_biology.pdf"
c = canvas.Canvas(pdf_path, pagesize=letter)

# Page 1
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
c.drawString(100, 505, "1. Light-dependent reactions (occur in thylakoid membranes)")
c.drawString(100, 490, "2. Light-independent reactions (Calvin cycle in stroma)")

c.showPage()  # New page

# Page 2
c.setFont("Helvetica-Bold", 14)
c.drawString(100, 750, "Light-Dependent Reactions")

c.setFont("Helvetica", 12)
c.drawString(100, 700, "Also called the light reactions, these occur in the thylakoid membranes.")
c.drawString(100, 685, "They require light to proceed and produce:")

c.drawString(100, 650, "- ATP (adenosine triphosphate) - energy currency")
c.drawString(100, 635, "- NADPH (electron carrier)")
c.drawString(100, 620, "- Oxygen (O2) - released as byproduct")

c.showPage()

# Page 3
c.setFont("Helvetica-Bold", 14)
c.drawString(100, 750, "Calvin Cycle (Light-Independent)")

c.setFont("Helvetica", 12)
c.drawString(100, 700, "The Calvin cycle does not directly require light but uses products from")
c.drawString(100, 685, "light-dependent reactions (ATP and NADPH).")

c.drawString(100, 650, "Steps:")
c.drawString(100, 635, "1. Carbon fixation")
c.drawString(100, 620, "2. Reduction")
c.drawString(100, 605, "3. Regeneration of RuBP")

c.drawString(100, 570, "The end product is glucose (C6H12O6), which plants use for energy and growth.")

c.save()

print(f"Created '{pdf_path}' with 3 pages")

# Step 2: Extract text
print("\n[2/3] Extracting text from PDF...")

extraction_result = extract_text_from_pdf(pdf_path)

if not extraction_result["success"]:
    print(f"FAILED: {extraction_result['error']}")
    exit(1)

print(f"Success! Extracted from {extraction_result['page_count']} pages")
print(f"Total characters: {len(extraction_result['text'])}")

# Step 3: Show extracted content
print("\n[3/3] Extracted content:")
print("-" * 60)
print(extraction_result['text'])
print("-" * 60)

# Test summary generation
print("\nText summary (200 chars):")
summary = get_pdf_summary(extraction_result['text'], 200)
print(summary)

# Cleanup
print("\n" + "=" * 60)
print("Cleaning up...")
if os.path.exists(pdf_path):
    os.remove(pdf_path)
    print(f"Deleted '{pdf_path}'")

print("\n" + "=" * 60)
print("PDF EXTRACTION TEST COMPLETE!")
print("=" * 60)

print("\nKEY FEATURES DEMONSTRATED:")
print("1. Multi-page PDF support")
print("2. Text extraction per page")
print("3. Clean text formatting")
print("4. Summary generation")
print("\nThis extracted text can now be used as context for the tutor agent!")
