"""
Main FastAPI Application with Prometheus Metrics
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import time

from src.api.v1.router import api_router
from src.settings import APP_SETTINGS
from src.monitoring import api_requests_total, api_request_duration

def create_app() -> FastAPI:
    app = FastAPI(
        title=APP_SETTINGS.APP_NAME,
        version=APP_SETTINGS.APP_VERSION,
        description="OCR Medical Document Extraction API with Monitoring"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=APP_SETTINGS.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Prometheus metrics middleware
    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # Record metrics
        api_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        api_request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response
    
    # Include API router
    app.include_router(api_router, prefix=APP_SETTINGS.API_V1_PREFIX)
    
    # Prometheus metrics endpoint
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint"""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    @app.get("/")
    async def root():
        return {
            "message": "OCR Medical Document API",
            "version": APP_SETTINGS.APP_VERSION,
            "docs": f"{APP_SETTINGS.API_V1_PREFIX}/docs",
            "metrics": "/metrics"
        }
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": time.time()
        }
    
    return app

app = create_app()