import os
import io
import tempfile
import google.generativeai as genai
from PIL import Image
import fitz  # PyMuPDF for PDF processing
from src.settings import APP_SETTINGS
import logging

logger = logging.getLogger(__name__)

class OCRProcessor:
    def __init__(self):
        self.api_key = APP_SETTINGS.GEMINI_API_KEY
        logger.info(f"API Key loaded: {'Yes' if self.api_key else 'No'}")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in settings")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def process(self, file):
        """Debug version with detailed logging"""
        try:
            logger.info(f"Processing file: {file.filename}")
            logger.info(f"Content type: {file.content_type}")
            logger.info(f"File size: {file.size if hasattr(file, 'size') else 'Unknown'}")
            
            # Step 1: Read file content
            content = await file.read()
            logger.info(f"File content read: {len(content)} bytes")
            
            # Step 2: Test Gemini connection
            await self._test_gemini_connection()
            
            # Step 3: Process based on file type
            if file.content_type.startswith('image/'):
                logger.info("Processing as image file")
                text = await self._process_image_debug(content)
            elif file.content_type == 'application/pdf':
                logger.info("Processing as PDF file")
                text = await self._process_pdf_debug(content)
            else:
                raise ValueError(f"Unsupported file type: {file.content_type}")
            
            logger.info(f"Extracted text length: {len(text) if text else 0}")
            logger.info(f"Extracted text preview: {text[:200] if text else 'No text extracted'}")
            
            return {"extracted_text": text, "file_info": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size_bytes": len(content)
            }}
            
        except Exception as e:
            logger.error(f"Error in process: {str(e)}", exc_info=True)
            raise

    async def _test_gemini_connection(self):
        """Test if Gemini API is working"""
        try:
            logger.info("Testing Gemini API connection...")
            response = self.model.generate_content("Hello, this is a test. Please respond with 'API working'.")
            logger.info(f"Gemini test response: {response.text}")
        except Exception as e:
            logger.error(f"Gemini API test failed: {str(e)}")
            raise

    async def _process_image_debug(self, image_content):
        """Debug version of image processing"""
        try:
            logger.info("Converting bytes to PIL Image...")
            image = Image.open(io.BytesIO(image_content))
            logger.info(f"Image loaded: {image.size}, mode: {image.mode}")
            
            # Save a copy for debugging (optional)
            # image.save("debug_image.png")
            
            prompt = """
            Please extract ALL text from this image. Include:
            1. All printed text
            2. All handwritten text
            3. Numbers, dates, names
            4. Any form fields or labels
            
            Provide the complete extracted text without any formatting or analysis.
            """
            
            logger.info("Sending request to Gemini Vision API...")
            response = self.model.generate_content([prompt, image])
            logger.info(f"Gemini response received, length: {len(response.text) if response.text else 0}")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in _process_image_debug: {str(e)}", exc_info=True)
            raise

    async def _process_pdf_debug(self, pdf_content):
        """Debug version of PDF processing"""
        try:
            logger.info("Creating temporary PDF file...")
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_content)
                tmp_file_path = tmp_file.name
            
            logger.info(f"Temporary PDF created: {tmp_file_path}")
            
            try:
                pdf_document = fitz.open(tmp_file_path)
                logger.info(f"PDF opened, pages: {pdf_document.page_count}")
                
                page = pdf_document[0]  # Process first page only for debugging
                logger.info("Converting PDF page to image...")
                
                # Convert to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                img_data = pix.tobytes("png")
                logger.info(f"PDF page converted to image: {len(img_data)} bytes")
                
                # Process with Gemini
                image = Image.open(io.BytesIO(img_data))
                logger.info(f"Image created from PDF: {image.size}")
                
                prompt = """
                This is a page from a PDF document. Please extract ALL text content:
                1. All printed text and labels
                2. All handwritten entries
                3. All numbers, dates, and codes
                4. Form field contents
                
                Extract everything you can see as plain text.
                """
                
                logger.info("Sending PDF image to Gemini...")
                response = self.model.generate_content([prompt, image])
                logger.info(f"Response received from Gemini for PDF")
                
                pdf_document.close()
                return response.text
                
            finally:
                os.unlink(tmp_file_path)
                logger.info("Temporary PDF file deleted")
                
        except Exception as e:
            logger.error(f"Error in _process_pdf_debug: {str(e)}", exc_info=True)
            raise