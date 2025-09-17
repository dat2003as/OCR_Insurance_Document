import os
from .design_pattern import singleton
from dotenv import load_dotenv

load_dotenv()


@singleton
class AppSettings:
    APP_NAME: str = "Insurance Document Processor"
    APP_VERSION: str = "1.0.0"
    
    # Gemini API Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

APP_SETTINGS = AppSettings()