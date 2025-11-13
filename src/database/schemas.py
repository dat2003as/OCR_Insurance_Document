from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class DocumentBase(BaseModel):
    filename: str
    file_size: Optional[int] = None


class DocumentCreate(DocumentBase):
    file_path: str
    mime_type: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: int
    uploaded_at: datetime
    processed: bool
    status: str
    
    class Config:
        from_attributes = True


class ExtractionBase(BaseModel):
    document_id: int
    agent_workflow: str = "standard"


class ExtractionCreate(ExtractionBase):
    pass


class ExtractionResponse(BaseModel):
    id: int
    document_id: int
    status: str
    policy_details: Optional[Dict[str, Any]] = None
    insured_info: Optional[Dict[str, Any]] = None
    payment_instructions: Optional[Dict[str, Any]] = None
    declaration: Optional[Dict[str, Any]] = None
    physician_report: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    validation_errors: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: int
    extraction_id: int
    action: str
    user_id: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True
