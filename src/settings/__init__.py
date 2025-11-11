import os

from traitlets import List
from .design_pattern import singleton
from dotenv import load_dotenv

load_dotenv()


@singleton
class AppSettings:
    APP_NAME: str = "OCR Medical Document API"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    # Gemini API Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = "gemini-2.5-flash"
    ALLOWED_ORIGINS: List[str] = ["*"]
    # File upload settings
    ALLOWED_EXTENSIONS: set = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
    PDF_DPI: int = 300
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf"]
    
    # Processing
    MAX_PAGES: int = 4
    RATE_LIMIT_DELAY: float = 1.0  # seconds between API calls
    
    # Paths
    UPLOAD_DIR: str = "uploads"
    TEMP_DIR: str = "temp"
    
    class Config:
        case_sensitive = True
        env_file = ".env"
APP_SETTINGS = AppSettings()