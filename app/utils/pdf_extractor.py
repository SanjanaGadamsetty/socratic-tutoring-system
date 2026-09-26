"""
PDF Text Extractor - Extract text content from PDF files.

This utility handles:
- Reading PDF files
- Extracting text from all pages
- Cleaning and formatting extracted text
- Error handling for corrupted PDFs
"""

import os
from typing import Dict, Any
from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> Dict[str, Any]:
    """
    Extract text content from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Dictionary with:
            - success: bool
            - text: str (extracted text)
            - page_count: int
            - error: str (if failed)
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "text": "",
                "page_count": 0,
                "error": f"File not found: {file_path}"
            }

        # Read PDF
        reader = PdfReader(file_path)
        page_count = len(reader.pages)

        # Extract text from all pages
        extracted_text = []
        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            if page_text.strip():  # Only add non-empty pages
                extracted_text.append(f"--- Page {page_num} ---\n{page_text}")

        # Join all pages
        full_text = "\n\n".join(extracted_text)

        # Clean text
        full_text = clean_extracted_text(full_text)

        print(f"[PDFExtractor] Extracted {len(full_text)} characters from {page_count} pages")

        return {
            "success": True,
            "text": full_text,
            "page_count": page_count,
            "error": None
        }

    except Exception as e:
        print(f"[PDFExtractor] Error: {e}")
        return {
            "success": False,
            "text": "",
            "page_count": 0,
            "error": str(e)
        }


def clean_extracted_text(text: str) -> str:
    """
    Clean and format extracted text.

    Args:
        text: Raw extracted text

    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if line:  # Keep non-empty lines
            cleaned_lines.append(line)

    # Join with single newlines
    cleaned_text = '\n'.join(cleaned_lines)

    # Remove excessive blank lines (more than 2 consecutive newlines)
    while '\n\n\n' in cleaned_text:
        cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')

    return cleaned_text


def get_pdf_summary(text: str, max_chars: int = 500) -> str:
    """
    Get a summary/preview of PDF content.

    Args:
        text: Full extracted text
        max_chars: Maximum characters to include

    Returns:
        Summary text
    """
    if len(text) <= max_chars:
        return text

    # Get first max_chars and add ellipsis
    summary = text[:max_chars].rsplit(' ', 1)[0]  # Don't cut mid-word
    return summary + "..."


# ===== EXPLANATION =====

"""
HOW PDF EXTRACTION WORKS:

1. PyPDF Library:
    PdfReader(file_path) -> Opens PDF
    reader.pages -> List of pages
    page.extract_text() -> Gets text from one page

2. Text Extraction:
    For each page:
        - Extract raw text
        - Add page marker (--- Page 1 ---)
        - Combine all pages

3. Text Cleaning:
    Raw PDF text can be messy:
        - Extra whitespace
        - Weird line breaks
        - Empty lines

    Cleaning:
        - Remove extra whitespace
        - Join lines properly
        - Remove excessive blank lines

4. Why Store Extracted Text?
    Option 1: Extract on every session start
        - Slower
        - Wastes API calls
        - Redundant processing

    Option 2: Extract once, store in DB
        - Fast
        - Efficient
        - Can search through text

    We use Option 2!

USAGE IN OUR SYSTEM:

Upload Flow:
    Student uploads PDF
        |
        v
    Save PDF file
        |
        v
    Extract text with this utility
        |
        v
    Store text in database (pdf_documents.extracted_text)
        |
        v
    Ready for tutoring!

Session Flow:
    Student starts session with PDF ID
        |
        v
    Load extracted_text from database
        |
        v
    Pass to tutor agent as context
        |
        v
    Tutor asks questions from PDF content
        |
        v
    Verifier ensures no answer leaks

EXAMPLE:

PDF Content:
    "Photosynthesis is the process by which plants convert
    light energy into chemical energy. The formula is:
    6CO2 + 6H2O + light -> C6H12O6 + 6O2"

Student asks:
    "What is photosynthesis?"

Tutor (with PDF context):
    "Great question! Based on the material, can you identify
    what photosynthesis converts and what it produces?"

    (Guides without revealing the answer!)

ADVANTAGES:

1. Rich Content:
    Students can learn from their own study materials
    Not limited to pre-defined problems

2. Personalized:
    Each student brings their own PDFs
    Tutoring adapts to their curriculum

3. Flexible:
    Works with any PDF (textbooks, notes, slides)

4. Scalable:
    No need to manually create problems
    System generates questions from content

ERROR HANDLING:

- File not found -> Clear error message
- Corrupted PDF -> Catch exception, return error
- Empty PDF -> Handle gracefully
- Unreadable text -> Return what we can extract

This makes the system robust!
"""
