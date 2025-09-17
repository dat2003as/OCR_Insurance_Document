from fastapi import APIRouter
from .endpoints import (
    upload
)
api_router = APIRouter(prefix="/v1")
api_router.include_router(upload.router, tags=["Upload"])
