"""
PDF API Endpoints - Upload and manage PDF documents.

Endpoints:
- POST /pdfs/upload - Upload a PDF
- GET /pdfs - List all PDFs
- GET /pdfs/{id} - Get PDF details
- DELETE /pdfs/{id} - Delete a PDF
"""

import os
import shutil
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import PDFDocument
from app.utils.pdf_extractor import extract_text_from_pdf, get_pdf_summary


router = APIRouter(prefix="/pdfs", tags=["PDFs"])

# Directory to store uploaded PDFs
UPLOAD_DIR = "uploads/pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(None),
    student_id: str = Form("anonymous"),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF document.

    Flow:
        1. Validate file is PDF
        2. Save file to disk
        3. Extract text content
        4. Store metadata in database
        5. Return PDF ID
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.pdf"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get file size
        file_size = os.path.getsize(file_path)

        # Extract text from PDF
        extraction_result = extract_text_from_pdf(file_path)

        if not extraction_result["success"]:
            # Delete file if extraction failed
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text from PDF: {extraction_result['error']}"
            )

        # Create database record
        pdf_doc = PDFDocument(
            title=title,
            description=description,
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            extracted_text=extraction_result["text"],
            page_count=extraction_result["page_count"],
            file_size=file_size,
            uploaded_by=student_id
        )

        db.add(pdf_doc)
        db.commit()
        db.refresh(pdf_doc)

        print(f"[PDF Upload] Uploaded {file.filename} -> ID {pdf_doc.id}")

        return {
            "success": True,
            "pdf_id": pdf_doc.id,
            "filename": file.filename,
            "page_count": pdf_doc.page_count,
            "file_size": pdf_doc.file_size,
            "text_preview": get_pdf_summary(pdf_doc.extracted_text, 200),
            "uploaded_at": pdf_doc.uploaded_at.isoformat()
        }

    except Exception as e:
        # Clean up file if something went wrong
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/")
def list_pdfs(
    student_id: str = None,
    db: Session = Depends(get_db)
):
    """
    List all uploaded PDFs.

    Optional filter by student_id.
    """
    query = db.query(PDFDocument)

    if student_id:
        query = query.filter(PDFDocument.uploaded_by == student_id)

    pdfs = query.order_by(PDFDocument.uploaded_at.desc()).all()

    return {
        "pdfs": [
            {
                "id": pdf.id,
                "filename": pdf.original_filename,
                "page_count": pdf.page_count,
                "file_size": pdf.file_size,
                "uploaded_by": pdf.uploaded_by,
                "uploaded_at": pdf.uploaded_at.isoformat(),
                "text_preview": get_pdf_summary(pdf.extracted_text, 150)
            }
            for pdf in pdfs
        ]
    }


@router.get("/{pdf_id}")
def get_pdf_details(
    pdf_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific PDF.
    """
    pdf = db.query(PDFDocument).filter(PDFDocument.id == pdf_id).first()

    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    return {
        "id": pdf.id,
        "filename": pdf.original_filename,
        "page_count": pdf.page_count,
        "file_size": pdf.file_size,
        "uploaded_by": pdf.uploaded_by,
        "uploaded_at": pdf.uploaded_at.isoformat(),
        "extracted_text": pdf.extracted_text,  # Full text
        "session_count": len(pdf.sessions)  # How many sessions used this PDF
    }


@router.delete("/{pdf_id}")
def delete_pdf(
    pdf_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a PDF document.

    Removes from database and deletes file.
    """
    pdf = db.query(PDFDocument).filter(PDFDocument.id == pdf_id).first()

    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    # Delete file from disk
    if os.path.exists(pdf.file_path):
        os.remove(pdf.file_path)

    # Delete from database
    db.delete(pdf)
    db.commit()

    return {
        "success": True,
        "message": f"PDF '{pdf.original_filename}' deleted"
    }


# ===== EXPLANATION =====

"""
PDF UPLOAD FLOW:

1. Client sends PDF file:
    POST /pdfs/upload
    Content-Type: multipart/form-data
    Body: file (PDF binary)

2. Server validates:
    - Is it a PDF? (.pdf extension)
    - Can we read it?

3. Server saves file:
    Generate unique ID: uuid.uuid4()
    Save as: uploads/pdfs/{uuid}.pdf

4. Server extracts text:
    Call pdf_extractor.extract_text_from_pdf()
    Get full text content

5. Server stores in DB:
    PDFDocument record with:
        - Original filename
        - File path
        - Extracted text
        - Metadata (size, pages, etc.)

6. Server responds:
    {
        "pdf_id": 123,
        "filename": "biology_notes.pdf",
        "page_count": 15,
        "text_preview": "Chapter 1: Cells..."
    }

PDF-BASED SESSION FLOW:

1. Student uploads PDF:
    POST /pdfs/upload
    -> pdf_id = 123

2. Student starts session:
    POST /sessions/start
    {
        "pdf_id": 123,
        "student_id": "student_1"
    }

3. Session loads PDF text:
    SELECT extracted_text FROM pdf_documents WHERE id = 123

4. Tutor gets PDF context:
    context = {
        "pdf_content": extracted_text,
        "student_question": "What is a cell?"
    }

5. Tutor generates question:
    "Based on the reading, can you identify the main
    components mentioned in a cell's structure?"

6. Verifier checks:
    Does response reveal answers from PDF?

7. Student learns:
    Interactive Q&A based on their own study material!

FILE STORAGE:

Why save files?
    - Need original PDF for future reference
    - Extraction might need retrying
    - Student might want to download again

Directory structure:
    uploads/
        pdfs/
            abc-123-def.pdf
            xyz-456-ghi.pdf

Each file gets unique UUID name to avoid conflicts.

DATABASE vs FILE:

Database stores:
    - Metadata (filename, size, page count)
    - Extracted text (for quick access)
    - Relationships (sessions using this PDF)

File system stores:
    - Actual PDF binary

This separation is best practice!

ERROR HANDLING:

1. Invalid file type:
    -> 400 Bad Request

2. Extraction fails:
    -> Delete file, return error

3. Database save fails:
    -> Delete file, return error

4. File not found (later access):
    -> 404 Not Found

Always clean up (delete file) if something fails!

SECURITY CONSIDERATIONS:

1. File type validation:
    Only allow .pdf
    Prevent malicious uploads

2. File size limits:
    (Add in production)
    Prevent huge uploads

3. Access control:
    (Add in production)
    Only owner can delete PDF

4. Virus scanning:
    (Add in production)
    Scan uploaded files

For now, basic validation is enough for demo!
"""
