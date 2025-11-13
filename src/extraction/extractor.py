"""
Data Extraction using Google Gemini Vision API
"""
import google.generativeai as genai
from PIL import Image
import json
from typing import Dict, Any, List
from src.settings import APP_SETTINGS
from src.settings.prompts import PromptFactory  
import asyncio

# Configure Gemini
if APP_SETTINGS.GEMINI_API_KEY:
    genai.configure(api_key=APP_SETTINGS.GEMINI_API_KEY)


class GeminiExtractor:
    """Extract structured data from images using Gemini"""
    
    def __init__(self):
        if not APP_SETTINGS.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        self.model = genai.GenerativeModel(APP_SETTINGS.GEMINI_MODEL)
        self.prompt_factory = PromptFactory()
    
    async def extract_page(
        self, 
        image: Image.Image, 
        page_number: int
    ) -> Dict[str, Any]:
        """Extract data from a single page"""
        try:
            # Get specialized prompt for this page
            page_prompt = self.prompt_factory.get_page_prompt(page_number)
            
            # Generate content with Gemini
            response = self.model.generate_content([page_prompt.prompt, image])
            response_text = response.text
            
            # Parse JSON response
            return self._parse_json_response(response_text)
        
        except Exception as e:
            return {
                "error": f"Extraction failed for page {page_number}: {str(e)}",
                "page": page_number
            }
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from Gemini response"""
        try:
            # Remove markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            return json.loads(response_text.strip())
        
        except json.JSONDecodeError:
            return {
                "raw_response": response_text,
                "note": "Failed to parse as JSON"
            }
    
    async def extract_multipage(
        self, 
        images: List[Image.Image]
    ) -> List[Dict[str, Any]]:
        """Extract data from multiple pages with rate limiting"""
        results = []
        
        for i, image in enumerate(images[:APP_SETTINGS.MAX_PAGES]):
            page_num = i + 1
            print(f"Processing page {page_num}...")
            
            result = await self.extract_page(image, page_num)
            results.append(result)
            
            # Rate limiting
            if i < len(images) - 1:
                await asyncio.sleep(APP_SETTINGS.RATE_LIMIT_DELAY)
        
        return results