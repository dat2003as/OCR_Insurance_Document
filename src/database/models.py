from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base


class Document(Base):
    """Document model for uploaded files"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)  # in bytes
    mime_type = Column(String(100))
    file_hash = Column(String(64), index=True)  # MD5 hash for deduplication
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, index=True)
    processed_at = Column(DateTime)
    
    # Status
    processed = Column(Boolean, default=False)
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    
    # Relationships
    extractions = relationship("Extraction", back_populates="document")
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "processed": self.processed,
            "status": self.status
        }


class Extraction(Base):
    """Extraction result model"""
    __tablename__ = "extractions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    
    # Status
    status = Column(String(50), default="pending", index=True)
    # pending, processing, completed, failed, needs_review
    
    # Extracted data (JSON fields)
    policy_details = Column(JSON)
    insured_info = Column(JSON)
    benefits_to_claim = Column(JSON)
    payment_instructions = Column(JSON)
    declaration = Column(JSON)
    physician_report = Column(JSON)
    
    # Metadata
    total_pages = Column(Integer)
    confidence_score = Column(Float)
    processing_time = Column(Float)  # in seconds
    validation_errors = Column(JSON)
    
    # Agent info
    agent_workflow = Column(String(50))  # standard, advanced, parallel
    agent_version = Column(String(20))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Celery task
    task_id = Column(String(255), index=True)
    
    # Relationships
    document = relationship("Document", back_populates="extractions")
    audit_logs = relationship("AuditLog", back_populates="extraction")
    
    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "status": self.status,
            "policy_details": self.policy_details,
            "insured_info": self.insured_info,
            "benefits_to_claim": self.benefits_to_claim,
            "payment_instructions": self.payment_instructions,
            "declaration": self.declaration,
            "physician_report": self.physician_report,
            "total_pages": self.total_pages,
            "confidence_score": self.confidence_score,
            "processing_time": self.processing_time,
            "validation_errors": self.validation_errors,
            "agent_workflow": self.agent_workflow,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class AuditLog(Base):
    """Audit log for tracking changes and actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    extraction_id = Column(Integer, ForeignKey("extractions.id"), index=True)
    
    # Action details
    action = Column(String(100), index=True)  # created, updated, validated, corrected
    user_id = Column(String(100))
    user_email = Column(String(255))
    
    # Changes
    changes = Column(JSON)  # What was changed
    old_values = Column(JSON)  # Previous values
    new_values = Column(JSON)  # New values
    
    # Metadata
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    extraction = relationship("Extraction", back_populates="audit_logs")
    
    def to_dict(self):
        return {
            "id": self.id,
            "extraction_id": self.extraction_id,
            "action": self.action,
            "user_id": self.user_id,
            "changes": self.changes,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

