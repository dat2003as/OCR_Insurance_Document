"""
PDF to Image Processing with PyMuPDF
"""
import fitz  # PyMuPDF
from PIL import Image
import io
from typing import List
from fastapi import HTTPException
from src.settings import APP_SETTINGS


class PDFProcessor:
    """Process PDF files to images"""
    
    @staticmethod
    def pdf_to_images(pdf_bytes: bytes) -> List[Image.Image]:
        """Convert PDF pages to PIL Images"""
        try:
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            images = []
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                # High resolution conversion
                zoom = APP_SETTINGS.PDF_DPI / 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                images.append(img)
            
            pdf_document.close()
            return images
        
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"PDF processing failed: {str(e)}"
            )
    
    @staticmethod
    def validate_pdf(pdf_bytes: bytes) -> bool:
        """Validate PDF file"""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page_count = len(doc)
            doc.close()
            
            if page_count < APP_SETTINGS.MAX_PAGES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Expected {APP_SETTINGS.MAX_PAGES} pages, got {page_count}"
                )
            
            return True
        except fitz.FileDataError:
            raise HTTPException(status_code=400, detail="Invalid PDF file")
    
    @staticmethod
    def get_page_count(pdf_bytes: bytes) -> int:
        """Get number of pages in PDF"""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            count = len(doc)
            doc.close()
            return count
        except:
            return 0