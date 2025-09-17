from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging
import traceback

from src.extraction.extractor import DataExtractor
from src.ocr.processor import OCRProcessor

# Import the debug classes

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload/debug")
async def debug_upload_file(file: UploadFile = File(...)):
    """Debug version of upload endpoint with detailed logging"""
    try:
        # Log request details
        logger.info("=" * 50)
        logger.info("DEBUG UPLOAD STARTED")
        logger.info(f"File: {file.filename}")
        logger.info(f"Content Type: {file.content_type}")
        logger.info(f"Headers: {dict(file.headers) if hasattr(file, 'headers') else 'No headers'}")
        
        # Validate file
        if not file.filename:
            logger.error("No filename provided")
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
        if file.content_type not in allowed_types:
            logger.error(f"Unsupported file type: {file.content_type}")
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
        
        # Step 1: Initialize OCR Processor
        logger.info("Step 1: Initializing OCR Processor...")
        try:
            ocr_processor = OCRProcessor()
            logger.info("✓ OCR Processor initialized successfully")
        except Exception as e:
            logger.error(f"✗ Failed to initialize OCR Processor: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OCR initialization failed: {str(e)}")
        
        # Step 2: Process OCR
        logger.info("Step 2: Processing OCR...")
        try:
            ocr_result = await ocr_processor.process(file)
            logger.info("✓ OCR processing completed")
            logger.info(f"OCR result keys: {list(ocr_result.keys()) if ocr_result else 'None'}")
        except Exception as e:
            logger.error(f"✗ OCR processing failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
        
        # Step 3: Extract data
        logger.info("Step 3: Extracting structured data...")
        try:
            data_extractor = DataExtractor(ocr_result)
            extracted_data = data_extractor.extract_all_enhanced()
            logger.info("✓ Data extraction completed")
        except Exception as e:
            logger.error(f"✗ Data extraction failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Data extraction failed: {str(e)}")
        
        # Prepare response
        response = {
            "status": "success",
            "filename": file.filename,
            "content_type": file.content_type,
            "ocr_raw_result": ocr_result,
            "extracted_data": extracted_data,
            "debug_info": {
                "ocr_text_length": len(ocr_result.get("extracted_text", "")),
                "extraction_method": "pattern_matching"
            }
        }
        
        logger.info("DEBUG UPLOAD COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in debug_upload_file: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Original upload endpoint - redirect to debug for now"""
    logger.info("Redirecting to debug endpoint...")
    return await debug_upload_file(file)


@router.get("/test-api")
async def test_gemini_api():
    """Test endpoint to verify Gemini API is working"""
    try:
        from src.settings import APP_SETTINGS
        import google.generativeai as genai
        
        if not APP_SETTINGS.GEMINI_API_KEY:
            return {
                "status": "error",
                "message": "GEMINI_API_KEY not found in settings",
                "api_key_present": False
            }
        
        genai.configure(api_key=APP_SETTINGS.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content("Hello! Please respond with 'API is working correctly'")
        
        return {
            "status": "success",
            "message": "Gemini API is working",
            "api_key_present": True,
            "api_response": response.text
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"API test failed: {str(e)}",
            "api_key_present": bool(APP_SETTINGS.GEMINI_API_KEY)
        }


@router.get("/health")
async def health_check():
    """Enhanced health check"""
    from src.settings import APP_SETTINGS
    
    return {
        "status": "healthy",
        "api_key_configured": bool(APP_SETTINGS.GEMINI_API_KEY),
        "dependencies": {
            "google_generativeai": True,
            "PIL": True,
            "PyMuPDF": True
        }
    }