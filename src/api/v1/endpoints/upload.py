"""
Upload and Processing Endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from src.ocr.processor import PDFProcessor
from src.extraction.extractor import GeminiExtractor
from src.utils.merger import ResultMerger  # Import from utils
from src.utils.validator import DataValidator  # Import from utils
from src.WrapperFunction import ImageHelper
from src.settings import APP_SETTINGS

router = APIRouter()


class ExtractionResponse(BaseModel):
    total_pages: int
    merged_data: Dict[str, Any]
    page_results: list
    processing_method: str
    validation_errors: Dict[str, Any] = {}


@router.post("/extract-multipage", response_model=ExtractionResponse)
async def extract_multipage_document(file: UploadFile = File(...)):
    """
    Extract structured data from 4-page medical claim form
    """
    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files supported")
    
    try:
        # Read file
        pdf_bytes = await file.read()
        
        # Validate file size
        if len(pdf_bytes) > APP_SETTINGS.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Process PDF
        processor = PDFProcessor()
        processor.validate_pdf(pdf_bytes)
        images = processor.pdf_to_images(pdf_bytes)
        
        # Extract data with Gemini
        extractor = GeminiExtractor()
        page_results = await extractor.extract_multipage(images)
        
        # Validate and clean data
        validated_results = [
            DataValidator.validate_extracted_data(result) 
            for result in page_results
        ]
        
        # Merge results
        merged_data = ResultMerger.merge_results(validated_results)
        
        # Validate complete form
        validation_errors = DataValidator.validate_medical_form(merged_data)
        
        # Format response
        formatted_results = [
            {
                "page_number": i + 1,
                "extracted_data": result,
                "confidence": "high" if "error" not in result else "low"
            }
            for i, result in enumerate(validated_results)
        ]
        
        return ExtractionResponse(
            total_pages=len(images),
            merged_data=merged_data,
            page_results=formatted_results,
            processing_method="PyMuPDF + Gemini Vision API",
            validation_errors=validation_errors
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview-pages")
async def preview_pdf_pages(file: UploadFile = File(...)):
    """Preview PDF pages as base64 images"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files supported")
    
    try:
        pdf_bytes = await file.read()
        processor = PDFProcessor()
        images = processor.pdf_to_images(pdf_bytes)
        
        previews = []
        for i, img in enumerate(images):
            resized = ImageHelper.resize_for_preview(img)
            base64_img = ImageHelper.image_to_base64(resized)
            
            previews.append({
                "page": i + 1,
                "width": resized.width,
                "height": resized.height,
                "base64": f"data:image/png;base64,{base64_img}"
            })
        
        return {
            "total_pages": len(images),
            "previews": previews
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))