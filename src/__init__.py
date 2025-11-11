"""
Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.router import api_router
from src.settings import APP_SETTINGS

def create_app() -> FastAPI:
    app = FastAPI(
        title=APP_SETTINGS.APP_NAME,
        version=APP_SETTINGS.APP_VERSION,
        description="OCR Medical Document Extraction API"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=APP_SETTINGS.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    app.include_router(api_router, prefix=APP_SETTINGS.API_V1_PREFIX)
    @app.get("/")
    async def root():
        return {
            "message": "OCR Medical Document API",
            "version": APP_SETTINGS.APP_VERSION,
            "docs": f"{APP_SETTINGS.API_V1_PREFIX}/docs"
        }
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "gemini_configured": APP_SETTINGS.GEMINI_API_KEY is not None
        }
    
    return app

app = create_app()
